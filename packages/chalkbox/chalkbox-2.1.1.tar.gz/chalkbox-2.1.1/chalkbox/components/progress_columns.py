from rich.progress import ProgressColumn, Task
from rich.text import Text


class MinuteSecondsColumn(ProgressColumn):
    """Progress column that displays elapsed time in M:SS format (minutes:seconds).

    Unlike TimeElapsedColumn which shows H:MM:SS, this column shows a more
    compact M:SS format suitable for shorter tasks (e.g., "0:05", "2:30").
    """

    def render(self, task: Task) -> Text:
        """Render elapsed time as M:SS format."""
        elapsed_ms = int((task.elapsed or 0) * 1000)

        minutes = elapsed_ms // 60000
        seconds = (elapsed_ms % 60000) // 1000

        return Text(f"{minutes}:{seconds:02d}", style="progress.elapsed")
