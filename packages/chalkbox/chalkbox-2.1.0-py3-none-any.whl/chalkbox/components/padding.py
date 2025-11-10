from typing import Any

from rich.console import RenderableType
from rich.padding import Padding as RichPadding

from ..core.console import get_console
from ..core.theme import get_theme


class Padding:
    """
    Themed spacing wrapper with theme-aware defaults.

    A fail-safe wrapper around Rich's Padding that integrates with ChalkBox's
    theme spacing tokens. Use this to add consistent spacing around components.

    Examples:
        >>> from chalkbox import Padding, Alert, get_console
        >>> console = get_console()
        >>>
        >>> # Add padding to an alert
        >>> alert = Alert.success("Done!")
        >>> console.print(Padding(alert, pad=1))
        >>>
        >>> # Asymmetric padding
        >>> console.print(Padding(alert, pad=(2, 4)))  # (vertical, horizontal)
        >>>
        >>> # Using theme spacing tokens
        >>> console.print(Padding.medium(alert))
        >>> console.print(Padding.large(alert))
    """

    def __init__(
        self,
        renderable: RenderableType,
        pad: int | tuple[int, int] | tuple[int, int, int, int] = 1,
        style: str | None = None,
        expand: bool = True,
    ):
        """Create a padded content wrapper."""
        self.renderable = renderable
        self.pad = pad
        self.style = style
        self.expand = expand
        self.console = get_console()
        self.theme = get_theme()

        # Validate padding values
        if isinstance(self.pad, int):
            if self.pad < 0:
                self.console.log(f"[yellow]Warning:[/yellow] Negative padding {self.pad}, using 0")
                self.pad = 0
        elif isinstance(self.pad, tuple):
            if len(self.pad) == 2:
                # (vertical, horizontal)
                v, h = self.pad
                if v < 0 or h < 0:
                    self.console.log("[yellow]Warning:[/yellow] Negative padding values, using 0")
                    self.pad = (max(0, v), max(0, h))
            elif len(self.pad) == 4:
                # (top, right, bottom, left)
                t, r, b, left = self.pad
                if any(x < 0 for x in self.pad):
                    self.console.log("[yellow]Warning:[/yellow] Negative padding values, using 0")
                    self.pad = (max(0, t), max(0, r), max(0, b), max(0, left))
            else:
                self.console.log(
                    f"[yellow]Warning:[/yellow] Invalid padding tuple length "
                    f"{len(self.pad)}, using default"
                )
                self.pad = 1

    def __rich__(self) -> RenderableType:
        """Render the padded content as a Rich renderable."""
        try:
            # Rich Padding doesn't accept None for style, so only pass if defined
            if self.style is not None:
                return RichPadding(
                    renderable=self.renderable,
                    pad=self.pad,
                    style=self.style,
                    expand=self.expand,
                )
            else:
                return RichPadding(
                    renderable=self.renderable,
                    pad=self.pad,
                    expand=self.expand,
                )
        except Exception as e:
            # Return original renderable
            self.console.log(f"[yellow]Warning:[/yellow] Could not apply padding: {e}")
            return self.renderable

    def print(self) -> None:
        """Print the padded content to console."""
        self.console.print(self.__rich__())

    @classmethod
    def none(cls, renderable: RenderableType, **kwargs: Any) -> "Padding":
        """
        Create content with no padding (explicit zero padding).

        Examples:
            >>> Padding.none(alert)
        """
        return cls(renderable, pad=0, **kwargs)

    @classmethod
    def xs(cls, renderable: RenderableType, **kwargs: Any) -> "Padding":
        """
        Create content with extra-small padding (uses theme spacing.xs).

        Examples:
            >>> Padding.xs(alert)
        """
        theme = get_theme()
        spacing = theme.spacing.xs
        return cls(renderable, pad=spacing, **kwargs)

    @classmethod
    def small(cls, renderable: RenderableType, **kwargs: Any) -> "Padding":
        """
        Create content with small padding (uses theme spacing.sm).

        Examples:
            >>> Padding.small(table)
        """
        theme = get_theme()
        spacing = theme.spacing.sm
        return cls(renderable, pad=spacing, **kwargs)

    @classmethod
    def medium(cls, renderable: RenderableType, **kwargs: Any) -> "Padding":
        """
        Create content with medium padding (uses theme spacing.md).

        Examples:
            >>> Padding.medium(section)
        """
        theme = get_theme()
        spacing = theme.spacing.md
        return cls(renderable, pad=spacing, **kwargs)

    @classmethod
    def large(cls, renderable: RenderableType, **kwargs: Any) -> "Padding":
        """
        Create content with large padding (uses theme spacing.lg).

        Examples:
            >>> Padding.large(alert)
        """
        theme = get_theme()
        spacing = theme.spacing.lg
        return cls(renderable, pad=spacing, **kwargs)

    @classmethod
    def xl(cls, renderable: RenderableType, **kwargs: Any) -> "Padding":
        """
        Create content with extra-large padding (uses theme spacing.xl).

        Examples:
            >>> Padding.xl(Panel("Important"))
        """
        theme = get_theme()
        spacing = theme.spacing.xl
        return cls(renderable, pad=spacing, **kwargs)

    @classmethod
    def symmetric(
        cls,
        renderable: RenderableType,
        vertical: int = 1,
        horizontal: int = 2,
        **kwargs: Any,
    ) -> "Padding":
        """
        Create content with symmetric padding (vertical, horizontal).

        Examples:
            >>> Padding.symmetric(alert, vertical=2, horizontal=4)
        """
        return cls(renderable, pad=(vertical, horizontal), **kwargs)

    @classmethod
    def custom(
        cls,
        renderable: RenderableType,
        top: int = 0,
        right: int = 0,
        bottom: int = 0,
        left: int = 0,
        **kwargs: Any,
    ) -> "Padding":
        """
        Create content with custom padding on each side.

        Examples:
            >>> Padding.custom(alert, top=1, bottom=2, left=3, right=4)
        """
        return cls(renderable, pad=(top, right, bottom, left), **kwargs)

    @classmethod
    def vertical(cls, renderable: RenderableType, amount: int = 1, **kwargs: Any) -> "Padding":
        """
        Create content with vertical padding only (top and bottom).

        Examples:
            >>> Padding.vertical(table, amount=2)
        """
        return cls(renderable, pad=(amount, 0), **kwargs)

    @classmethod
    def horizontal(cls, renderable: RenderableType, amount: int = 2, **kwargs: Any) -> "Padding":
        """
        Create content with horizontal padding only (left and right).

        Examples:
            >>> Padding.horizontal(alert, amount=4)
        """
        return cls(renderable, pad=(0, amount), **kwargs)
