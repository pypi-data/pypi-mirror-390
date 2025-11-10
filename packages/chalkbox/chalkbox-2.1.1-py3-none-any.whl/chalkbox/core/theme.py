import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
import toml


class ColorsConfig(BaseModel):
    """Color configuration for theme."""

    model_config = ConfigDict(extra="forbid")

    primary: str = "cyan"
    secondary: str = "blue"
    success: str = "green"
    warning: str = "yellow"
    error: str = "red"
    info: str = "blue"
    muted: str = "dim white"
    accent: str = "bright_cyan"
    background: str = "default"
    text: str = "default"
    debug: str = "dim cyan"
    critical: str = "bright_red"


class SpacingConfig(BaseModel):
    """Spacing configuration for theme."""

    model_config = ConfigDict(extra="forbid")

    xs: int = 0
    sm: int = 1
    default: int = 1
    md: int = 2
    lg: int = 3
    xl: int = 4


class GlyphsConfig(BaseModel):
    """Glyph configuration for theme."""

    model_config = ConfigDict(extra="forbid")

    success: str = "✓"
    error: str = "✖"
    warning: str = "⚠"
    info: str = "i"
    debug: str = "▪"
    critical: str = "‼"
    arrow: str = "→"
    bullet: str = "•"
    check: str = "✓"
    cross: str = "✖"
    spinner: str = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    pending: str = "○"
    running: str = "◔"
    complete: str = "●"
    failed: str = "✖"
    skipped: str = "⊘"


class BordersConfig(BaseModel):
    """Border configuration for theme."""

    model_config = ConfigDict(extra="forbid")

    style: str = "rounded"
    panel: str = "rounded"
    table: str = "rounded"
    section: str = "rounded"


class TableConfig(BaseModel):
    """Table component configuration."""

    model_config = ConfigDict(extra="forbid")

    auto_expand_threshold: int = Field(
        default=5,
        ge=0,
        description="Column count threshold for auto-expand. Tables with this many columns or more will expand to terminal width when expand='auto'. Wide tables need more space.",
    )

    responsive_mode: bool = Field(
        default=False,
        description="Enable responsive table sizing based on terminal width. When enabled, tables adapt their width to terminal size like CSS media queries.",
    )

    responsive_breakpoints: dict[str, int] = Field(
        default_factory=lambda: {
            "compact": 60,  # < 60 cols: stay narrow
            "medium": 80,  # 60-80 cols: calculate width
            "wide": 81,  # > 80 cols: full expand
        },
        description="Terminal width breakpoints for responsive sizing. Keys: compact, medium, wide. Values: terminal column widths.",
    )


class Theme(BaseModel):
    """Theme configuration with design tokens."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    colors: ColorsConfig = Field(default_factory=lambda: ColorsConfig())
    spacing: SpacingConfig = Field(default_factory=lambda: SpacingConfig())
    glyphs: GlyphsConfig = Field(default_factory=lambda: GlyphsConfig())
    borders: BordersConfig = Field(default_factory=lambda: BordersConfig())
    table: TableConfig = Field(default_factory=lambda: TableConfig())

    @classmethod
    def from_file(cls, path: Path) -> "Theme":
        """Load theme from a TOML file."""
        if not path.exists():
            return cls()

        data = toml.load(path)

        theme_data: dict[str, Any] = {}
        if "colors" in data:
            theme_data["colors"] = ColorsConfig(**data["colors"])
        if "spacing" in data:
            theme_data["spacing"] = SpacingConfig(**data["spacing"])
        if "glyphs" in data:
            theme_data["glyphs"] = GlyphsConfig(**data["glyphs"])
        if "borders" in data:
            theme_data["borders"] = BordersConfig(**data["borders"])
        if "table" in data:
            theme_data["table"] = TableConfig(**data["table"])

        return cls(**theme_data)

    @classmethod
    def from_env(cls) -> "Theme":
        """Create theme with environment variable overrides."""
        theme = cls()

        prefix = "CHALKBOX_THEME_"
        updates: dict[str, dict[str, Any]] = {
            "colors": {},
            "spacing": {},
            "glyphs": {},
            "borders": {},
            "table": {},
        }

        for key, value in os.environ.items():
            if key.startswith(prefix):
                path = key[len(prefix) :].lower().replace("_", ".")
                parts = path.split(".")

                if len(parts) == 2:
                    category, field_name = parts
                    if category in updates:
                        if category in ("spacing", "table"):
                            try:
                                updates[category][field_name] = int(value)
                            except ValueError:
                                updates[category][field_name] = value
                        else:
                            updates[category][field_name] = value

        if updates["colors"]:
            theme.colors = ColorsConfig(**{**theme.colors.model_dump(), **updates["colors"]})
        if updates["spacing"]:
            theme.spacing = SpacingConfig(**{**theme.spacing.model_dump(), **updates["spacing"]})
        if updates["glyphs"]:
            theme.glyphs = GlyphsConfig(**{**theme.glyphs.model_dump(), **updates["glyphs"]})
        if updates["borders"]:
            theme.borders = BordersConfig(**{**theme.borders.model_dump(), **updates["borders"]})
        if updates["table"]:
            theme.table = TableConfig(**{**theme.table.model_dump(), **updates["table"]})

        return theme

    def get_style(self, level: str = "default") -> str:
        """Get Rich style string for a severity level."""
        color_map = {
            "debug": self.colors.debug,
            "info": self.colors.info,
            "success": self.colors.success,
            "warning": self.colors.warning,
            "error": self.colors.error,
            "critical": self.colors.critical,
            "default": self.colors.text,
            "muted": self.colors.muted,
            "primary": self.colors.primary,
        }
        return color_map.get(level, self.colors.text)


_theme: Theme | None = None


def get_theme() -> Theme:
    """Get the current theme instance."""
    global _theme
    if _theme is None:
        _theme = Theme()

        # Load from config file if exists
        config_path = Path.home() / ".chalkbox" / "theme.toml"
        if config_path.exists():
            _theme = Theme.from_file(config_path)

        # Apply environment overrides
        env_theme = Theme.from_env()
        _theme.colors = ColorsConfig(
            **{**_theme.colors.model_dump(), **env_theme.colors.model_dump()}
        )
        _theme.spacing = SpacingConfig(
            **{**_theme.spacing.model_dump(), **env_theme.spacing.model_dump()}
        )
        _theme.glyphs = GlyphsConfig(
            **{**_theme.glyphs.model_dump(), **env_theme.glyphs.model_dump()}
        )
        _theme.borders = BordersConfig(
            **{**_theme.borders.model_dump(), **env_theme.borders.model_dump()}
        )
        _theme.table = TableConfig(**{**_theme.table.model_dump(), **env_theme.table.model_dump()})

    return _theme


def set_theme(theme: Theme | None = None, **kwargs: Any) -> None:
    """Set the global theme."""
    global _theme

    if theme is not None:
        _theme = theme
    elif kwargs:
        if _theme is None:
            _theme = Theme()

        # Parse kwargs for nested updates (e.g., colors_primary -> colors.primary)
        updates: dict[str, dict[str, Any]] = {
            "colors": {},
            "spacing": {},
            "glyphs": {},
            "borders": {},
            "table": {},
        }

        for key, value in kwargs.items():
            parts = key.split("_", 1)
            if len(parts) == 2:
                category, field_name = parts
                if category in updates:
                    updates[category][field_name] = value

        if updates["colors"]:
            _theme.colors = ColorsConfig(**{**_theme.colors.model_dump(), **updates["colors"]})
        if updates["spacing"]:
            _theme.spacing = SpacingConfig(**{**_theme.spacing.model_dump(), **updates["spacing"]})
        if updates["glyphs"]:
            _theme.glyphs = GlyphsConfig(**{**_theme.glyphs.model_dump(), **updates["glyphs"]})
        if updates["borders"]:
            _theme.borders = BordersConfig(**{**_theme.borders.model_dump(), **updates["borders"]})
        if updates["table"]:
            _theme.table = TableConfig(**{**_theme.table.model_dump(), **updates["table"]})
