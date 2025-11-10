from typing import Any, Literal

from rich.console import RenderableType

from ..core.theme import get_theme
from .alert import Alert
from .bar import Bar
from .kv import KeyValue
from .section import Section

StatusLevel = Literal["healthy", "warning", "error", "unknown"]
BarSeverity = Literal["success", "warning", "error"]


class StatusCard:
    """
    Composite status card displaying status with metrics and visualizations.

    Combines Section, KeyValue, Bar, and Alert components to create rich status displays.
    This is a generic composition component - you control all severity and styling.

    Examples:
        >>> from chalkbox import StatusCard, Alert, get_console
        >>> console = get_console()
        >>>
        >>> # Simple status card
        >>> card = StatusCard(
        ...     title="Database Service",
        ...     status="healthy",
        ...     metrics={"Uptime": "24d 5h", "Connections": "42/100"},
        ... )
        >>> console.print(card)
        >>>
        >>> # With explicit severity bars
        >>> card = StatusCard(
        ...     title="API Gateway",
        ...     status="warning",
        ...     metrics={"Requests/sec": "1,234", "Error Rate": "0.8%"},
        ...     bars=[
        ...         ("Throughput", 85, 100, "warning"),
        ...         ("Response Time", 145, 200, "success"),
        ...     ],
        ... )
        >>> console.print(card)
        >>>
        >>> # With alert
        >>> card = StatusCard(
        ...     title="Cache Service",
        ...     status="error",
        ...     metrics={"Hit Rate": "0%"},
        ...     alert=Alert.error("Connection failed", details="Redis server unreachable"),
        ... )
        >>> console.print(card)
    """

    def __init__(
        self,
        title: str,
        status: StatusLevel = "unknown",
        subtitle: str | None = None,
        metrics: dict[str, Any] | None = None,
        bars: list[tuple[str, float, float] | tuple[str, float, float, BarSeverity]] | None = None,
        alert: Alert | None = None,
        bar_thresholds: dict[str, tuple[float, float]] | None = None,
        expand: bool = False,
    ):
        """Create a status card."""
        self.title = title
        self.status = status
        self.subtitle = subtitle
        self.metrics = metrics or {}
        self.bars = bars or []
        self.alert = alert
        self.bar_thresholds = bar_thresholds or {}
        self.expand = expand
        self.theme = get_theme()

    def _get_status_glyph(self) -> str:
        """Get status indicator glyph based on status level."""
        glyphs = {
            "healthy": "✓",
            "warning": "⚠",
            "error": "✖",
            "unknown": "?",
        }
        return glyphs.get(self.status, "?")

    def _get_status_style(self) -> str:
        """Get style based on status level."""
        status_styles = {
            "healthy": self.theme.get_style("success"),
            "warning": self.theme.get_style("warning"),
            "error": self.theme.get_style("error"),
            "unknown": self.theme.get_style("muted"),
        }
        return status_styles.get(self.status, self.theme.get_style("muted"))

    def _get_bar_severity(self, label: str, value: float, max_value: float) -> BarSeverity:
        """Calculate severity for a bar based on thresholds."""
        if max_value <= 0:
            return "success"

        percent = (value / max_value) * 100

        if label in self.bar_thresholds:
            warning_threshold, error_threshold = self.bar_thresholds[label]

            if percent >= error_threshold:
                return "error"
            elif percent >= warning_threshold:
                return "warning"

        return "success"

    def __rich__(self) -> RenderableType:
        """Render the status card as a Rich renderable."""
        try:
            glyph = self._get_status_glyph()
            status_style = self._get_status_style()
            full_title = f"{glyph} {self.title}"

            section = Section(
                title=full_title,
                subtitle=self.subtitle,
                border_style=status_style,
                expand=self.expand,
            )

            if self.alert:
                section.add(self.alert)
                if self.metrics or self.bars:
                    section.add_spacing()

            if self.metrics:
                kv = KeyValue(self.metrics)
                section.add(kv)
                if self.bars:
                    section.add_spacing()

            if self.bars:
                for i, bar_data in enumerate(self.bars):
                    # Handle both 3-tuple and 4-tuple formats
                    if len(bar_data) == 4:
                        label, value, max_value, severity = bar_data
                    elif len(bar_data) == 3:
                        label, value, max_value = bar_data
                        # Calculate severity from thresholds or default to success
                        severity = self._get_bar_severity(label, value, max_value)
                    else:
                        # Invalid format, skip
                        continue

                    percent = (value / max_value * 100) if max_value > 0 else 0

                    section.add_text(f"{label}: {percent:.1f}% ({value}/{max_value})")

                    bar = Bar.fraction(value, max_value, severity=severity, width=40)
                    section.add(bar)

                    if i < len(self.bars) - 1:
                        section.add_spacing()

            return section.__rich__()

        except Exception as e:
            # Fail-safe: return minimal error representation
            return f"[red]StatusCard Error:[/red] {e!s}"

    @classmethod
    def from_health_check(
        cls,
        service_name: str,
        health_data: dict[str, Any],
        **kwargs: Any,
    ) -> "StatusCard":
        """
        Create a StatusCard from health check data.

        Examples:
            >>> health = {
            ...     "status": "healthy",
            ...     "uptime": "24d 5h 32m",
            ...     "connections": "42/100",
            ...     "response_time": "12ms",
            ... }
            >>> card = StatusCard.from_health_check("Database", health)
        """
        # Extract and normalize status
        status_value = health_data.get("status", "unknown")
        status: StatusLevel
        if isinstance(status_value, str):
            # Normalize common status strings
            status_map: dict[str, StatusLevel] = {
                "healthy": "healthy",
                "ok": "healthy",
                "success": "healthy",
                "warning": "warning",
                "warn": "warning",
                "error": "error",
                "critical": "error",
                "fail": "error",
                "failed": "error",
                "unknown": "unknown",
            }
            status = status_map.get(status_value.lower(), "unknown")
        else:
            status = "unknown"

        metrics = {k: v for k, v in health_data.items() if k not in ("status", "bars", "alert")}

        bars = health_data.get("bars")
        alert = health_data.get("alert")

        return cls(
            title=service_name,
            status=status,
            metrics=metrics if metrics else None,
            bars=bars,
            alert=alert,
            **kwargs,
        )
