from typing import Any, Literal

from rich.align import Align as RichAlign
from rich.console import RenderableType

from ..core.console import get_console


class Align:
    """
    Themed content alignment wrapper with fail-safe defaults.

    A fail-safe wrapper around Rich's Align for positioning content horizontally
    and vertically. Useful for centering headers, aligning footers, and creating
    balanced layouts.

    Examples:
        >>> from chalkbox import Align, Alert, get_console
        >>> console = get_console()
        >>>
        >>> # Center an alert
        >>> alert = Alert.success("Deployment complete!")
        >>> console.print(Align.center(alert))
        >>>
        >>> # Right-align a table
        >>> table = Table(headers=["Metric", "Value"])
        >>> console.print(Align.right(table))
        >>>
        >>> # Vertical and horizontal alignment
        >>> content = Panel("Welcome", title="App")
        >>> console.print(Align.middle(content, vertical="middle"))
    """

    def __init__(
        self,
        renderable: RenderableType,
        align: Literal["left", "center", "right"] = "left",
        vertical: Literal["top", "middle", "bottom"] | None = None,
        width: int | None = None,
        height: int | None = None,
        style: str | None = None,
        pad: bool = True,
    ):
        """Create an aligned content wrapper."""
        self.renderable = renderable
        self.align = align
        self.vertical = vertical
        self.width = width
        self.height = height
        self.style = style
        self.pad = pad
        self.console = get_console()

        # Fail-safe: Validate alignment values
        if self.align not in ("left", "center", "right"):
            self.console.log(
                f"[yellow]Warning:[/yellow] Invalid align '{self.align}', using 'left'"
            )
            self.align = "left"

        if self.vertical and self.vertical not in ("top", "middle", "bottom"):
            self.console.log(
                f"[yellow]Warning:[/yellow] Invalid vertical '{self.vertical}', " f"using None"
            )
            self.vertical = None

    def __rich__(self) -> RenderableType:
        """Render the aligned content as a Rich renderable."""
        try:
            return RichAlign(
                renderable=self.renderable,
                align=self.align,
                vertical=self.vertical,
                width=self.width,
                height=self.height,
                style=self.style,
                pad=self.pad,
            )
        except Exception as e:
            # Fail-safe: Return original renderable
            self.console.log(f"[yellow]Warning:[/yellow] Could not align content: {e}")
            return self.renderable

    def print(self) -> None:
        """Print the aligned content to console."""
        self.console.print(self.__rich__())

    @classmethod
    def left(
        cls,
        renderable: RenderableType,
        vertical: Literal["top", "middle", "bottom"] | None = None,
        **kwargs: Any,
    ) -> "Align":
        """
        Create left-aligned content.

        Examples:
            >>> Align.left(alert)
            >>> Align.left(table, vertical="middle")
        """
        return cls(renderable, align="left", vertical=vertical, **kwargs)

    @classmethod
    def center(
        cls,
        renderable: RenderableType,
        vertical: Literal["top", "middle", "bottom"] | None = None,
        **kwargs: Any,
    ) -> "Align":
        """
        Create center-aligned content.

        Examples:
            >>> Align.center(Panel("Welcome"))
            >>> Align.center(alert, vertical="middle")
        """
        return cls(renderable, align="center", vertical=vertical, **kwargs)

    @classmethod
    def right(
        cls,
        renderable: RenderableType,
        vertical: Literal["top", "middle", "bottom"] | None = None,
        **kwargs: Any,
    ) -> "Align":
        """
        Create right-aligned content.

        Examples:
            >>> Align.right(table)
            >>> Align.right(alert, vertical="bottom")
        """
        return cls(renderable, align="right", vertical=vertical, **kwargs)

    @classmethod
    def middle(
        cls,
        renderable: RenderableType,
        align: Literal["left", "center", "right"] = "center",
        **kwargs: Any,
    ) -> "Align":
        """
        Create vertically centered content.

        Examples:
            >>> Align.middle(Panel("Loading..."))
            >>> Align.middle(alert, align="left")
        """
        return cls(renderable, align=align, vertical="middle", **kwargs)

    @classmethod
    def top(
        cls,
        renderable: RenderableType,
        align: Literal["left", "center", "right"] = "center",
        **kwargs: Any,
    ) -> "Align":
        """
        Create top-aligned content.

        Examples:
            >>> Align.top(Panel("Header"))
            >>> Align.top(alert, align="right")
        """
        return cls(renderable, align=align, vertical="top", **kwargs)

    @classmethod
    def bottom(
        cls,
        renderable: RenderableType,
        align: Literal["left", "center", "right"] = "center",
        **kwargs: Any,
    ) -> "Align":
        """
        Create bottom-aligned content.

        Examples:
            >>> Align.bottom(Panel("Footer"))
            >>> Align.bottom(KeyValue({"Status": "Ready"}), align="left")
        """
        return cls(renderable, align=align, vertical="bottom", **kwargs)
