import time
from typing import Any

from rich.console import Group, RenderableType
from rich.live import Live
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress as RichProgress,
    ProgressColumn,
    SpinnerColumn,
    TaskID,
    TextColumn,
)

from ..core.console import get_console
from ..core.theme import get_theme
from .progress_columns import MinuteSecondsColumn


class DynamicProgress:
    """Progress tracker with automatic task reordering.

    Displays tasks in two sections:
    - Active: Currently running tasks
    - Completed: Finished tasks sorted by completion time (fastest first)

    Uses millisecond precision for accurate ordering when tasks
    finish at nearly the same time, but displays time as M:SS format.
    """

    def __init__(
        self,
        console: Any | None = None,
        transient: bool = False,
        show_section_titles: bool = False,
    ):
        """Initialize dynamic progress tracker."""
        self.console = console or get_console()
        self.theme = get_theme()
        self.transient = transient
        self.show_section_titles = show_section_titles

        # Progress instances for active and completed sections
        self.active: RichProgress | None = None
        self.completed: RichProgress | None = None

        # Task tracking
        self.tasks: dict[TaskID, dict[str, Any]] = {}

        # Completed tasks list
        self.completed_tasks: list[dict[str, Any]] = []

        # Live display wrapper
        self._live: Live | None = None

        # Auto-increment task ID
        self._next_id = 0

    def _create_progress(self, title: str | None = None) -> RichProgress:
        """Create a progress instance with themed columns."""
        columns: list[ProgressColumn] = []

        if title and self.show_section_titles:
            columns.append(TextColumn(f"[bold]{title}[/bold]", justify="left"))

        columns.extend(
            [
                SpinnerColumn(style=self.theme.get_style("primary")),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(
                    complete_style=self.theme.get_style("success"),
                    finished_style=self.theme.get_style("success"),
                ),
                MofNCompleteColumn(),
                MinuteSecondsColumn(),  # Custom M:SS format
            ]
        )

        return RichProgress(
            *columns,
            console=self.console,
            transient=False,
            auto_refresh=True,
        )

    def _build_group(self) -> RenderableType:
        """Build the display group with active and completed sections."""
        renderables = []

        if self.tasks and self.active:
            renderables.append(self.active)

        if self.completed_tasks and self.completed:
            renderables.append(self.completed)

        return Group(*renderables) if renderables else Group()

    def __enter__(self) -> "DynamicProgress":
        """Start progress display with Live wrapper."""
        self.active = self._create_progress("Active Tasks" if self.show_section_titles else None)
        self.completed = self._create_progress(
            "Completed Tasks" if self.show_section_titles else None
        )

        self.active.start()
        self.completed.start()

        self._live = Live(
            self._build_group(),
            console=self.console,
            refresh_per_second=10,
            transient=self.transient,
        )
        self._live.start()

        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop progress display and cleanup."""
        if self._live:
            self._live.stop()

        if self.active:
            self.active.stop()

        if self.completed:
            self.completed.stop()

    def add_task(self, description: str, total: float = 100, **kwargs: Any) -> TaskID:
        """Add a new task to the active section."""
        if not self.active:
            raise RuntimeError("Progress not started (use context manager)")

        external_id = TaskID(self._next_id)
        self._next_id += 1

        active_task_id = self.active.add_task(description, total=total, **kwargs)

        self.tasks[external_id] = {
            "description": description,
            "total": total,
            "active_id": active_task_id,
            "start_ms": time.time_ns() // 1_000_000,  # Nanoseconds to milliseconds
            "kwargs": kwargs,
        }

        if self._live:
            self._live.update(self._build_group())

        return external_id

    def update(
        self,
        task_id: TaskID,
        *,
        advance: float | None = None,
        completed: float | None = None,
        total: float | None = None,
        description: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Update task progress and handle completion."""
        if task_id not in self.tasks:
            raise ValueError(f"Unknown task ID: {task_id}")

        if not self.active:
            raise RuntimeError("Progress not active")

        task_data = self.tasks[task_id]
        active_task_id = task_data["active_id"]

        self.active.update(
            active_task_id,
            advance=advance,
            completed=completed,
            total=total,
            description=description,
            **kwargs,
        )

        if description is not None:
            task_data["description"] = description

        active_task = self.active._tasks[active_task_id]
        if active_task.finished:
            self._move_to_completed(task_id)

        if self._live:
            self._live.update(self._build_group())

    def _move_to_completed(self, task_id: TaskID) -> None:
        """Move a task from active to completed section."""
        if task_id not in self.tasks:
            return

        task_data = self.tasks.pop(task_id)
        task_data["finish_ms"] = time.time_ns() // 1_000_000

        duration_ms = task_data["finish_ms"] - task_data["start_ms"]
        task_data["duration_ms"] = duration_ms

        if self.active:
            self.active.remove_task(task_data["active_id"])

        self.completed_tasks.append(task_data)

        self.completed_tasks.sort(key=lambda t: t["duration_ms"])

        self._rebuild_completed()

    def _rebuild_completed(self) -> None:
        """Rebuild completed section with tasks in sorted order.

        Tasks are sorted by completion time (fastest first) to show
        which tasks finished quickest.
        """
        if not self.completed:
            return

        for tid in list(self.completed._tasks.keys()):
            self.completed.remove_task(tid)

        for task_data in self.completed_tasks:
            completed_tid = self.completed.add_task(
                task_data["description"],
                total=task_data["total"],
                completed=task_data["total"],
                **task_data.get("kwargs", {}),
            )

            task_data["completed_id"] = completed_tid

    def remove_task(self, task_id: TaskID) -> None:
        """Remove a task completely (from active or completed).

        Note: This method is rarely needed as tasks automatically move
         to the completed section but kept for JustinCase.
        """
        if task_id in self.tasks:
            task_data = self.tasks.pop(task_id)
            if self.active:
                self.active.remove_task(task_data["active_id"])

        else:
            for i, task_data in enumerate(self.completed_tasks):
                if task_data.get("external_id") == task_id:
                    self.completed_tasks.pop(i)
                    self._rebuild_completed()
                    break

        if self._live:
            self._live.update(self._build_group())
