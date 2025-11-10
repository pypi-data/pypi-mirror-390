# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.1] - 2025-11-10

### Fixed

- **DynamicProgress Component**: Fixed critical rendering bugs
  - Fixed double rendering issue (tasks appeared duplicated)
  - Fixed progress bars showing live updates (not just final state)
  - Fixed elapsed time display (was showing 0:00 for all tasks)
  - Fixed task position format (now shows N/Total like 1/5, 2/5)
  - Removed `show_section_titles` parameter
  - Component now displays all tasks immediately with live progress
  - Tasks dynamically reorder as they complete (sorted by speed, fastest first)

### Note

This patch release fixes critical bugs in the DynamicProgress component
released in v2.1.0. All Table enhancements from v2.1.0 remain intact and functional.

## [2.1.0] - 2025-11-09

### Added

- **DynamicProgress Component**: Auto-reordering progress tracker for parallel task execution

  - Automatically sorts completed tasks by completion time (fastest first/millisecond precision)
  - Time displayed as `M:SS` format (e.g., "0:05", "2:30") without milliseconds
  - Separate "Active Tasks" and "Completed Tasks" sections (optional)
  - Optional section titles with `show_section_titles=True`
  - Context manager aware pattern: `with DynamicProgress() as progress:`
  - Theme-aware styling with ChalkBox colors
  - Perfect for: web scraping, batch processing, API benchmarking, any scenario where the order of the completion matters
  - New `MinuteSecondsColumn` progress column for compact time display

- **Table Component**: Auto-expand and responsive sizing

  - New `expand="auto"` parameter option for smart width management
  - Configurable threshold via `table.auto_expand_threshold` in theme config (default: 5)
  - Wide tables (5+ columns) expand to fill terminal width
  - Narrow tables (< 5 columns) stay compact
  - Backward compatible - default behavior unchanged (`expand=False`)
  - Render-time calculation respects dynamically added columns
  - **Responsive sizing** (CSS media query-like behavior):
    - Responsive mode disabled by default (`table.responsive_mode: false` in theme config)
    - Three terminal size breakpoints: compact (\<60 cols), medium (60-80 cols), wide (>80 cols)
    - **Compact terminals** (\<60 cols): Tables never expand (mobile-like behavior)
    - **Medium terminals** (60-80 cols): Wide tables get calculated width for optimal fit
    - **Wide terminals** (>80 cols): Standard auto-expand threshold logic applies
    - Configurable breakpoints via `table.responsive_breakpoints` in theme config
    - Works with existing `.live()` method for terminal resize responsiveness
    - Environment variables: `CHALKBOX_THEME_TABLE_RESPONSIVE_MODE`, `CHALKBOX_THEME_TABLE_RESPONSIVE_BREAKPOINTS_COMPACT`, etc.

1. **Table expansion**:

   ```python
   # Narrow tables (2-3 columns) - stay compact (already fit well)
   narrow = Table(headers=["Field", "Value"], expand="auto")

   # Wide tables (7+ columns) - expand to fill width (need more space)
   wide = Table(
       headers=["Provider", "Product", "Amount", "Price", "Change", "Available", "Scraped"],
       expand="auto"
   )

   # Explicit control still works
   table = Table(headers=["Name", "Status"], expand=True)  # Always expand
   table = Table(headers=["Name", "Status"], expand=False)  # Never expand (default)
   ```

   Configure the threshold in `~/.chalkbox/theme.toml`:

   ```toml
   [table]
   # Tables with 7 or more columns will expand (default: 5)
   auto_expand_threshold = 7
   ```

   Or via environment variable:

   ```bash
   export CHALKBOX_THEME_TABLE_AUTO_EXPAND_THRESHOLD=7
   ```

   Or programmatically:

   ```python
   from chalkbox import set_theme
   set_theme(table_auto_expand_threshold=7)
   ```

## [2.0.0] - 2025-11-02

### Added

- **Pydantic2**: Migrated theme system from dataclass to Pydantic v2
  - Runtime validation of all theme configuration values
  - Type hints for theme attributes
  - Automatic type validation for colors, spacing, glyphs, and borders
  - Four nested Pydantic models: `ColorsConfig`, `SpacingConfig`, `GlyphsConfig`, `BordersConfig`
  - Strict validation (`extra="forbid"`) prevents typos and undocumented theme fields
  - Clear validation error messages for invalid theme configurations
- **Dependencies**: Added `pydantic` (v2.12.3) and `pydantic-settings` (v2.11.0)

### Changed

- **Theme Access Pattern**: Theme values now accessed via direct attributes
  - **Before**: `theme.get("colors.primary")` or `theme.colors["primary"]`
  - **After**: `theme.colors.primary` (dot notation throughout)
  - Use `getattr(theme.colors, key, default)` for dynamic attribute access
- **Theme Updates**: `set_theme()` now uses underscore notation for kwargs
  - **Before**: `set_theme(None, **{"colors.primary": "blue"})`
  - **After**: `set_theme(None, colors_primary="blue")`
- **All Components**: Updated to use direct attribute access for theme values
  - `padding.py`, `bar.py`, `alert.py`, `spinner.py`, `stepper.py`, `section.py`

### Removed

- **Breaking**: Removed `theme.get(path, default)` method
  - Use direct attribute access: `theme.colors.primary`
  - Use `getattr()` for dynamic access: `getattr(theme.colors, key, default)`
- **Breaking**: Removed `theme.update(updates)` method
  - Use `set_theme()` with kwargs instead: `set_theme(None, colors_primary="blue")`
- **Breaking**: Dictionary-style theme access no longer supported
  - `theme.colors["primary"]` → `theme.colors.primary`
  - `theme.spacing["md"]` → `theme.spacing.md`

### Migration Guide

If you're upgrading from v1.x to v2.0:

1. **Update theme access**:

   ```python
   # Old (v1.x)
   color = theme.get("colors.primary")
   spacing = theme.spacing["md"]

   # New (v2.0)
   color = theme.colors.primary
   spacing = theme.spacing.md
   ```

1. **Update theme modifications**:

   ```python
   # Old (v1.x)
   theme.update({"colors.primary": "blue"})
   set_theme(None, **{"colors.primary": "blue"})

   # New (v2.0)
   set_theme(None, colors_primary="blue")
   ```

1. **Dynamic access**:

   ```python
   # Old (v1.x)
   value = theme.get(f"colors.{key}")

   # New (v2.0)
   value = getattr(theme.colors, key, default)
   ```

## [1.2.0] - 2025-10-26

### Added

- **StatusCard Component**: Generic status card component for rich status displays
  - Combines Section, KeyValue, Bar, and Alert components
  - Explicit severity via 4-tuple bars: `(label, value, max, severity)`
  - Auto-calculated severity via 3-tuple bars + `bar_thresholds` parameter
  - Factory method: `from_health_check()` for normalizing health check data
  - Status levels: healthy (✓), warning (⚠), error (✖), unknown (?)
  - Generic design - full control all severity and styling levels
  - Perfect for dashboards, monitoring tools, and health checks
- **Type Checking Support**: Added `py.typed` marker file
  - Enables proper type checking in projects consuming ChalkBox
  - Fixes mypy "missing library stubs or py.typed marker" errors
  - Full IDE type hint support (VSCode, PyCharm, etc.)
- **Component Demos**: Added demo script for StatusCard examples
  - `demos/components/status_card.py` - StatusCard usage patterns with both bar formats
- **Tests**: Added many tests for the StatusCard component
  - `tests/test_status_card.py` - Covers StatusCard functionality including both bar formats

### Changed

- **Dependencies**: Updated `psutil` from `^5.9.0` to `^7.1.2`
- **Documentation**: Updated project documentation with StatusCard usage examples
- **Package Metadata**: Added `chalkbox/py.typed` to distribution includes in `pyproject.toml`

## [1.1.0] - 2025-10-18

### Added

- **Bar Component**: Horizontal bar visualization for metrics and progress tracking
  - Factory methods: `percentage()`, `fraction()`, `from_ratio()`, `indeterminate()`
  - Severity-based coloring (success/warning/error/info/critical)
  - Customizable width and styles
  - Perfect for displaying API quotas, system resources, task progress, and ratings
- **Align Component**: Content alignment wrapper with defaults
  - Horizontal alignment: left, center, right
  - Vertical alignment: top, middle, bottom
  - Factory methods: `left()`, `center()`, `right()`, `middle()`, `top()`, `bottom()`
  - Width and height control for positioning
  - Ideal for headers, footers, menus, and emphasized content
- **Padding Component**: Theme-aware spacing wrapper with multiple patterns
  - Theme-based padding levels: `xs()`, `small()`, `medium()`, `large()`, `xl()`
  - Pattern methods: `symmetric()`, `vertical()`, `horizontal()`, `custom()`
  - Integrates with ChalkBox theme spacing tokens
  - validation for negative padding values
  - Perfect for creating visual hierarchy and card-like layouts
- **Component Demos**: Added comprehensive demos for all three new components
  - `demos/components/bar.py` - Bar charts, metrics, progress tracking
  - `demos/components/align.py` - Content alignment patterns
  - `demos/components/padding.py` - Spacing and layout examples
- **Tests**: Added 61 comprehensive tests for new components
  - `tests/test_bar.py` - 16 tests covering all Bar functionality
  - `tests/test_align.py` - 19 tests for alignment features
  - `tests/test_padding.py` - 26 tests including theme integration

### Changed

- **Documentation**: Updated README.md with new components

## [1.0.0] - 2025-10-13

### Added

- **Alert Component**: Added `debug` and `critical` severity levels (expanded from 4 to 6 levels)
  - `Alert.debug()` - For verbose debugging output with "▪" glyph and dim cyan color
  - `Alert.critical()` - For system-critical failures with "‼" glyph and bright red color
- **Alert Component**: Added `title_align` parameter for customizable title positioning
  - Supports "left" (default), "center", and "right" alignment
  - Available in all alert factory methods (`Alert.debug()`, `Alert.info()`, etc.)
- **Alert Component**: Added `padding` parameter for customizable internal spacing
  - Accepts integer for all sides or tuple `(vertical, horizontal)` for asymmetric padding
  - Default remains `(0, 1)` for backward compatibility
- **Section Component**: Added `title_align` and `subtitle_align` parameters
  - Both support "left", "center", and "right" alignment
  - `title_align` defaults to "left", `subtitle_align` defaults to "right"
  - Enables better visual hierarchy and emphasis in sections
- **Table Component**: Added `border_style` parameter for custom table theming
  - Accepts any Rich color string (e.g., "bright_cyan", "red", "dim white")
  - Defaults to theme's primary color for backward compatibility
  - Enables color-coded tables for different data types
- **Spinner Component**: Added `refresh_per_second` parameter for performance tuning
  - Controls animation refresh rate (default: 10 fps)
  - Lower values (4-6 fps) for slow terminals or remote connections
  - Higher values (15-20 fps) for smooth animations on fast terminals

### Changed

- **Theme System**: Updated color tokens to include `debug` (dim cyan) and `critical` (bright red)
- **Theme System**: Updated glyph tokens to include `debug` (▪) and `critical` (‼)
- **Documentation**: Updated `README.md` and `docs/COMPONENTS.md` with examples of all 6 alert levels
- **Demo Scripts**: Updated component demos to showcase all new features (title alignment, border styles, refresh rates)
- **Theme Files**: Updated `demos/theming/theme-dark.toml` and `theme-light.toml` with debug/critical support

## [0.9.0] - 2025-10-12

### Changed

- Project renamed from `Terminal UI Kit` to `ChalkBox`
- Updated Rich package version to 14.2.0
- Converted all interactive demos to auto-run mode for batch execution
- Added explicit Python 3.12+ requirement documentation

### Fixed

- Fixed Spinner component duplicate output when using `transient=False`
- Fixed demo file naming (removed `_demo` suffix from component demos)
- Fixed `interactive_components.py` to use simulated interaction for batch runs

### Added

- Documentation:
- Created CONTRIBUTING.md with comprehensive contribution guidelines
- Added "Why Python 3.12+" section to README explaining modern features
- Added badges to README (PyPI version, downloads, Python version, license, Rich, Poetry, quality tools, community metrics)
- Added Poetry badge to indicate dependency management approach

## [0.8.0] - 2025-07-27

### Added

- **Live & Responsive Components**:

  - LiveComponent: Generic wrapper for making any component live and responsive
  - LiveTable: Pre-configured live table wrapper
  - LiveLayout: Pre-configured live layout wrapper
  - Dashboard: High-level dashboard builder with header/sidebar/main/footer sections
  - Built-in `.live()` methods for Table and MultiPanel components
  - Automatic terminal resize handling for all live components
  - Support for both static (scrolling) and live (updating) output modes

- **Advanced Demos**:

  - Live component demos with auto-updating displays
  - Dashboard builder demonstrations
  - Responsive layout examples showing terminal resize adaptation

### Changed

- Updated Rich package version to 14.1.0

## [0.7.0] - 2025-03-30

### Added

- MultiPanel: Complex layouts component for grids and dashboards with automatic responsiveness
- Advanced live dashboard demos showcasing multi-section layouts
- Nested panel demonstrations showing composition patterns

### Changed

- Updated Rich package version to 14.0.0

## [0.6.0] - 2025-01-22

### Added

- **KeyValue**: Key-value display component with automatic secret masking for passwords, keys, tokens
  - Comprehensive test suite for KeyValue component
  - Secret detection patterns (password, secret, key, token, credential)

## [0.5.0] - 2025-01-10

### Added

- **CodeBlock**: Syntax-highlighted code display component with file reading support
- **Progress**: Multi-task progress bars with ETA and thread-safe updates
- Comprehensive test coverage for new components
- Support for multiple programming languages in CodeBlock

### Changed

- Migrated from Black, isort, and flake8 to Ruff for linting and formatting
- Improved code quality and consistency with unified linting tool

## [0.4.0] - 2025-01-10

### Added

- **Input Components**: Interactive prompt components for user interaction
  - Input: Basic text input with validation
  - IntInput: Integer input with range validation
  - FloatInput: Float input with range validation
  - Select: Choice selection from list
  - Confirm: Yes/no confirmation prompts
- Test suite for input components

### Changed

- Updated Rich package version to 13.9.4

## [0.1.0] - 2025-01-09

### Added

- **Initial Release** of terminal-ui-kit (project later renamed to ChalkBox in 0.9.5)

## Core Components

- **Spinner**: Context manager for async operations with success/fail/warning states
- **Alert**: Debug/info/success/warning/error/critical callouts with optional details
- **Table**: Auto-sizing tables with severity-based row styling and smart truncation
- **Section**: Organized content containers with optional subtitles
- **Divider**: Section dividers with multiple styles (standard, double, heavy, dotted, dashed)
- **Status**: Non-blocking status indicators for background operations
- **ColumnLayout**: Responsive column layouts with equal/custom sizing
- **Stepper**: Multi-step workflow tracking with status indicators
- **Tree**: Hierarchical data visualization with file system support
- **Markdown**: Markdown rendering component
- **JsonView**: JSON data visualization with pretty printing

## Theme System

- Token-based theming with colors, spacing, glyphs, and borders
- Three-tier configuration: defaults → config file → environment variables
- Config file support (`~/.chalkbox/theme.toml`)
- Environment variable overrides (`CHALKBOX_THEME_*`)
- Dot-notation access (e.g., `theme.get("colors.primary")`)
- Severity-based styling (success/warning/error/info)

## Core Features

- **Fail-safe design**: Components never raise exceptions, degrade gracefully
- **Non-TTY support**: Automatic degradation in CI/CD and piped output
- **Thread-safe operations**: Safe concurrent updates for Progress and stateful components
- **Context managers**: All stateful components support `with` statements
- **Factory methods**: Convenience constructors for common patterns
- **Singleton console**: `get_console()` for shared console access
- **Rich compatibility**: All components return Rich renderables for composition

## Logging

- Pre-configured Rich logging via `setup_logging()`
- Console and file handlers with configurable levels
- Rich tracebacks for better error diagnostics

## Development Tools

- Python 3.12+ requirement (uses modern type hints and `type` statement)
- Built on Rich >= 13.7.0
- Poetry for dependency management
- Ruff for linting and formatting
- MyPy for type checking
- Bandit for security analysis
- Pytest for testing with coverage support

## Documentation & Examples

- Component demos in `demos/components/` (individual examples)
- Showcase demos in `demos/showcases/` (multi-component demos)
- Workflow examples in `demos/workflows/` (real-world demos)
- README with quick start and examples
- Fail-safe patterns and best practices documentation

## Developer Experience

- Consistent naming conventions (snake_case for variables, kebab-case for CLI)
- Type hints throughout codebase using Python 3.12 syntax
- Fail-safe error handling patterns in all components
- Zero dependencies beyond Rich

## Version History Summary

- **0.1.0** (2025-01-09) - Initial release as terminal-ui-kit with core components
- **0.4.0** (2025-01-10) - Added interactive input components
- **0.5.0** (2025-01-10) - Added CodeBlock and Progress, migrated to Ruff
- **0.6.0** (2025-01-22) - Added KeyValue with secret masking
- **0.7.0** (2025-03-30) - Added MultiPanel and advanced live demos
- **0.8.0** (2025-07-27) - Added live components and Dashboard builder
- **0.9.0** (2025-10-12) - Renamed to ChalkBox, comprehensive documentation
- **1.0.0** (2025-10-13) - **Stable release**: Enhanced components, production-ready, 100% linting compliance

## Links

- **PyPI**: https://pypi.org/project/chalkbox/
- **GitHub**: https://github.com/bulletinmybeard/chalkbox
- **Issues**: https://github.com/bulletinmybeard/chalkbox/issues
- **Changelog**: https://github.com/bulletinmybeard/chalkbox/blob/main/CHANGELOG.md
