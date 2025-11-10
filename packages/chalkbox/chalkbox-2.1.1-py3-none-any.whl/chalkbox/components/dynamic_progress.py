import time
from typing import Any

from rich.console import Group, RenderableType
from rich.live import Live
from rich.progress import TaskID
from rich.text import Text

from ..core.console import get_console
from ..core.theme import get_theme


class DynamicProgress:
    """Progress tracker with automatic task reordering and live progress display.

    Displays all tasks (active and completed) with live progress bars.
    Completed tasks are sorted by completion time (fastest first),
    active tasks appear below.

    Uses millisecond precision for accurate ordering when tasks
    finish at nearly the same time, displays time as M:SS format.
    """

    def __init__(
        self,
        console: Any | None = None,
        transient: bool = False,
    ):
        """Initialize dynamic progress tracker."""
        self.console = console or get_console()
        self.theme = get_theme()
        self.transient = transient

        # Task tracking: {TaskID: {description, total, completed, start_ms, add_order}}
        self.tasks: dict[TaskID, dict[str, Any]] = {}

        # Completed tasks list: [{description, total, duration_ms, add_order}, ...]
        self.completed_tasks: list[dict[str, Any]] = []

        # Live display wrapper
        self._live: Live | None = None

        # Auto-increment task ID
        self._next_id = 0

    def _render_all_tasks(self) -> RenderableType:
        """Render all tasks (both active and completed) with live progress."""
        all_tasks_data = []

        # Add completed tasks (will be sorted by duration)
        for task_data in self.completed_tasks:
            all_tasks_data.append(
                {
                    "description": task_data["description"],
                    "completed": task_data["total"],
                    "total": task_data["total"],
                    "duration_ms": task_data["duration_ms"],
                    "add_order": task_data["add_order"],
                    "is_completed": True,
                }
            )

        # Add active tasks
        for _task_id, task_data in self.tasks.items():
            # Calculate current duration for active tasks
            current_ms = time.time_ns() // 1_000_000
            duration_ms = current_ms - task_data["start_ms"]

            all_tasks_data.append(
                {
                    "description": task_data["description"],
                    "completed": task_data["completed"],
                    "total": task_data["total"],
                    "duration_ms": duration_ms,
                    "add_order": task_data["add_order"],
                    "is_completed": False,
                }
            )

        # Sort: completed tasks by duration (fastest first), then active by add order
        completed = [t for t in all_tasks_data if t["is_completed"]]
        active = [t for t in all_tasks_data if not t["is_completed"]]

        completed.sort(key=lambda t: t["duration_ms"])
        active.sort(key=lambda t: t["add_order"])

        sorted_tasks = completed + active

        if not sorted_tasks:
            return Group()

        lines = []
        total_tasks = len(sorted_tasks)

        for idx, task in enumerate(sorted_tasks):
            # Format elapsed time as M:SS
            duration_sec = task["duration_ms"] / 1000.0
            minutes = int(duration_sec // 60)
            seconds = int(duration_sec % 60)
            time_str = f"{minutes}:{seconds:02d}"

            # Calculate progress bar fill
            bar_width = 38
            if task["total"] > 0:
                percentage = task["completed"] / task["total"]
                filled_width = int(percentage * bar_width)
            else:
                filled_width = 0

            filled = "━" * filled_width
            empty = " " * (bar_width - filled_width)
            bar_str = filled + empty

            # Description with fixed width
            description = task["description"]
            desc_width = 22
            if len(description) > desc_width:
                description = description[: desc_width - 3] + "..."
            else:
                description = description.ljust(desc_width)

            # Task position (e.g., "1/5")
            position = idx + 1
            count_str = f"{position}/{total_tasks}".rjust(5)

            # Build the line with proper styling
            line = Text(no_wrap=True, overflow="ignore")
            line.append("⠋", style=self.theme.get_style("primary"))
            line.append(f" {description} ", style="default")

            # Bar color: green if completed, primary if active
            bar_style = (
                self.theme.get_style("success")
                if task["is_completed"]
                else self.theme.get_style("primary")
            )
            line.append(bar_str, style=bar_style)

            line.append(f" {count_str}", style="green")
            line.append(f" {time_str}", style="yellow")

            lines.append(line)

        return Group(*lines)

    def _build_group(self) -> RenderableType:
        """Build the display group with all tasks."""
        return self._render_all_tasks()

    def __enter__(self) -> "DynamicProgress":
        """Start progress display with Live wrapper."""
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

    def add_task(self, description: str, total: float = 100, **kwargs: Any) -> TaskID:
        """Add a new task to track."""
        if self._live is None:
            raise RuntimeError("Progress not started (use context manager)")

        task_id = TaskID(self._next_id)
        self._next_id += 1

        self.tasks[task_id] = {
            "description": description,
            "total": total,
            "completed": 0.0,
            "start_ms": time.time_ns() // 1_000_000,  # Nanoseconds to milliseconds
            "add_order": self._next_id,  # Track insertion order
            "kwargs": kwargs,
        }

        # Refresh display to show new task immediately
        if self._live:
            self._live.update(self._build_group())

        return task_id

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

        task_data = self.tasks[task_id]

        if advance is not None:
            task_data["completed"] += advance
        if completed is not None:
            task_data["completed"] = completed
        if total is not None:
            task_data["total"] = total
        if description is not None:
            task_data["description"] = description

        # Check if task is finished
        if task_data["completed"] >= task_data["total"]:
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

        self.completed_tasks.append(task_data)

    def remove_task(self, task_id: TaskID) -> None:
        """Remove a task completely."""
        if task_id in self.tasks:
            self.tasks.pop(task_id)

        self.completed_tasks = [
            task for task in self.completed_tasks if task.get("task_id") != task_id
        ]

        if self._live:
            self._live.update(self._build_group())
