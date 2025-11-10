from typing import Any, Literal

from rich.bar import Bar as RichBar
from rich.console import RenderableType

from ..core.console import get_console
from ..core.theme import get_theme


class Bar:
    """
    Themed horizontal bar visualization for metrics and progress.

    A fail-safe wrapper around Rich's Bar with ChalkBox theming and automatic
    validation. Useful for displaying metrics, quotas, ratings, and progress
    percentages.

    Examples:
        >>> from chalkbox import Bar, get_console
        >>> console = get_console()
        >>>
        >>> # Simple percentage bar
        >>> bar = Bar(75, 100, width=40)
        >>> console.print(bar)
        >>>
        >>> # With severity-based coloring
        >>> console.print(Bar(90, 100, severity="warning"))  # High usage
        >>> console.print(Bar(45, 100, severity="success"))  # Normal usage
        >>> console.print(Bar(98, 100, severity="error"))  # Critical usage
        >>>
        >>> # Custom styling
        >>> bar = Bar(512, 1024, width=50, style="cyan", complete_style="bright_cyan")
        >>> console.print(f"Memory: {bar} 512MB/1024MB")
    """

    def __init__(
        self,
        completed: float,
        total: float | None = None,
        width: int | None = 40,
        pulse: bool = False,
        style: str | None = None,
        complete_style: str | None = None,
        finished_style: str | None = None,
        severity: Literal["success", "warning", "error", "info"] | None = None,
    ):
        """Create a horizontal bar visualization."""
        self.completed = completed
        self.total = total
        self.width = width
        self.pulse = pulse
        self.console = get_console()
        self.theme = get_theme()

        # Ensure completed is non-negative
        if self.completed < 0:
            self.completed = 0

        # Ensure total is positive if provided
        if self.total is not None and self.total <= 0:
            self.total = None  # Treat as indeterminate

        # Ensure width is reasonable
        if width is not None and width < 1:
            self.width = 40  # Default safe width

        # Determine styles based on severity or custom styles
        if severity:
            severity_style = self.theme.get_style(severity)
            self.complete_style = complete_style or severity_style
            self.finished_style = finished_style or severity_style
        else:
            self.complete_style = complete_style or self.theme.colors.primary
            self.finished_style = finished_style or complete_style or self.theme.colors.success

        self.style = style or "default"

    def __rich__(self) -> RenderableType:
        """Render the bar as a Rich renderable."""
        try:
            # Check if bar is complete
            is_complete = self.total is not None and self.completed >= self.total

            # Note: Rich Bar uses color/bgcolor, not style/complete_style
            # Map our styles to Rich's Bar API
            bar_color = self.finished_style if is_complete else self.complete_style
            bar_bgcolor = self.style

            return RichBar(
                size=self.total if self.total is not None else 100,
                begin=0,
                end=self.completed,
                width=self.width,
                color=bar_color,
                bgcolor=bar_bgcolor,
            )
        except Exception as e:
            # Return error text
            self.console.log(f"[yellow]Warning:[/yellow] Could not render bar: {e}")
            return f"[{self.completed}/{self.total or '?'}]"

    def print(self) -> None:
        """Print the bar to console."""
        self.console.print(self.__rich__())

    @classmethod
    def percentage(
        cls,
        percent: float,
        width: int | None = 40,
        severity: Literal["success", "warning", "error", "info"] | None = None,
        **kwargs: Any,
    ) -> "Bar":
        """Create a bar from a percentage (0-100).

        Args:
            percent: Percentage value (0-100)
            width: Width of the bar
            severity: Severity level for coloring
            **kwargs: Additional Bar constructor arguments

        Returns:
            Bar instance representing the percentage

        Examples:
            >>> Bar.percentage(75.5, severity="success")
            >>> Bar.percentage(92, severity="warning")
        """
        # Clamp percentage to 0-100
        percent = max(0, min(100, percent))
        return cls(completed=percent, total=100, width=width, severity=severity, **kwargs)

    @classmethod
    def fraction(
        cls,
        numerator: float,
        denominator: float,
        width: int | None = 40,
        severity: Literal["success", "warning", "error", "info"] | None = None,
        **kwargs: Any,
    ) -> "Bar":
        """Create a bar from a fraction.

        Args:
            numerator: Completed amount
            denominator: Total amount
            width: Width of the bar
            severity: Severity level for coloring
            **kwargs: Additional Bar constructor arguments

        Returns:
            Bar instance representing the fraction

        Examples:
            >>> Bar.fraction(3, 4, severity="success")  # 3/4 = 75%
            >>> Bar.fraction(512, 1024, severity="warning")  # 512MB/1GB = 50%
        """
        return cls(completed=numerator, total=denominator, width=width, severity=severity, **kwargs)

    @classmethod
    def indeterminate(cls, width: int | None = 40, pulse: bool = True, **kwargs: Any) -> "Bar":
        """Create an indeterminate (unknown total) bar with pulse animation.

        Args:
            width: Width of the bar
            pulse: Whether to show pulse animation
            **kwargs: Additional Bar constructor arguments

        Returns:
            Bar instance with indeterminate state

        Examples:
            >>> Bar.indeterminate()  # Pulsing bar
            >>> Bar.indeterminate(pulse=False)  # Static bar
        """
        return cls(completed=0, total=None, width=width, pulse=pulse, **kwargs)

    @classmethod
    def from_ratio(
        cls,
        ratio: float,
        width: int | None = 40,
        severity: Literal["success", "warning", "error", "info"] | None = None,
        **kwargs: Any,
    ) -> "Bar":
        """Create a bar from a ratio (0.0-1.0).

        Args:
            ratio: Ratio value (0.0 = 0%, 1.0 = 100%)
            width: Width of the bar
            severity: Severity level for coloring
            **kwargs: Additional Bar constructor arguments

        Returns:
            Bar instance representing the ratio

        Examples:
            >>> Bar.from_ratio(0.75, severity="success")  # 75%
            >>> Bar.from_ratio(0.92, severity="warning")  # 92%
        """
        # Clamp ratio to 0.0-1.0
        ratio = max(0.0, min(1.0, ratio))
        return cls(completed=ratio * 100, total=100, width=width, severity=severity, **kwargs)
