# nscolors

Lightweight cross-platform terminal coloring & utilities for Python

nscolors is a compact package that provides ANSI/WinAPI-aware terminal coloring, simple RGB/256-color helpers, progress bars, cursor movement utilities, tables and more — all without external dependencies. This repository contains an early (v1.0.0) implementation designed for small CLI tools and scripts.

---

## Key features

- Foreground (FG) and background (BG) helpers and convenience functions
- direct color helpers (RGB, 256-color, random colors)
- Table builder with ANSI-safe width calculations
- Multiple progress-bar styles and a customizable progress method
- Cursor control helpers (move, goto, hide/show)
- Dual support: ANSI sequences and Windows WINAPI where available
- Palettes loaded from `nscolors/palettes/` (JSON/TXT)
- No external dependencies (pure Python)

---

## Quick install

This project is a global package. To install (optional):

```powershell
# from repository nscolors
python -m pip install nscolors
```

Or just import directly from the package folder in your project.

---

## Quick start

Preferred import styles (avoid `from nscolors import *` in your own projects):

```python
# explicit import (recommended)
from nscolors.colors import colors, ESC, CSI, SEP, RESET_STYLE
from nscolors.fg import FG
from nscolors.bg import BG
from nscolors.direct import DIRECT
from nscolors.cursor import CURSOR
from nscolors.progress import Progress
from nscolors.tables import Table

# or namespace import
import nscolors
nscolors.FG.red("hello")
```

Examples:

```python
from nscolors.fg import FG
from nscolors.bg import BG
from nscolors.direct import DIRECT

# simple foreground color
FG.red("This text is red")

# background and foreground
BG.blue("This has a blue background")
FG.white("White text")

# direct color (style + palette names)
DIRECT.color("Styled text", text_style="Normal", color="Green", bgcolor="Black")

# rgb
DIRECT.rgb("Truecolor text", R=200, G=100, B=50)

# progress bar
from nscolors.progress import Progress
for i in range(21):
    Progress.block(i, 20)

# cursor
from nscolors.cursor import CURSOR
CURSOR.goto(5, 10, "At row 5 col 10")

# table
from nscolors.tables import Table
from nscolors.fg import FG

t = Table(title="Sample")
t.add_column("Name", "Age")
t.add_row("Alice", "30")
t.add_row("Bob", "27")
t.print_table()
```

---

## API summary

Important modules / symbols exported by the package:

- `nscolors.colors`:
  - `ESC`, `CSI`, `SEP`, `RESET_STYLE` — low-level ANSI constants
  - `colors`, `BgColors`, `TextStyles`, `WinFGColors`, `WinBGColors` — color palettes (dicts)
- `nscolors.fg`:
  - `FG` class with static methods: `FG.red(text)`, `FG.green(text)`, etc.
- `nscolors.bg`:
  - `BG` class with static methods for backgrounds: `BG.blue(text)`, etc.
- `nscolors.direct`:
  - `DIRECT.color`, `DIRECT.rgb`, `DIRECT.color256`, `DIRECT.random_text_colored`, `DIRECT.animated_write`
- `nscolors.cursor`:
  - `CURSOR.goto`, `CURSOR.up`, `CURSOR.down`, `CURSOR.hide_cursor`, etc.
- `nscolors.progress`:
  - `Progress` with different predefined styles (`block`, `arabic`, `professional`, ...)
- `nscolors.tables`:
  - `Table` class that handles column widths while stripping ANSI sequences.
- `nscolors.core`:
  - `GetSystemInfo()`, `init()`, `LoadPalette()` and other helper utilities

---

## Notes & best practices

- Avoid `from nscolors import *` in your projects; prefer explicit imports or `import nscolors` to avoid namespace pollution.
- Currently `nscolors/__init__.py` calls `GetSystemInfo()` and `init()` and some modules load palettes at import time. That means importing the package may perform I/O and attempt Windows console setup immediately. This behavior is intentional in this version but consider the cost in short-running scripts.
- If you need to minimize import cost, import specific submodules only when required (e.g., only import `nscolors.tables` if you use tables).
- Palettes are stored in `nscolors/palettes/`. You can edit or extend those JSON/TXT files to customize available named colors.

---

## Compatibility

- Designed to work cross-platform with fallback to Windows WINAPI on older Windows releases.
- For modern rich rendering or advanced terminal features, consider using `rich` (which provides more features and polished output), but `nscolors` is intentionally dependency-free and lightweight.

---

## Contributing

Small, focused contributions are welcome. Suggested early PRs:

- Convert import-time palette loading to optional lazy-loading
- Replace `import *` usage across package with explicit exports (internal refactor)
- Add unit tests (pytest) for core functions like `LoadPalette`, `strip_ansi_codes` and color outputs
- Improve error messages and unify logging format

Please include a short description, test, and example for any new feature.

---

## License

As indicated in `pyproject.toml`, this project uses the MIT License. Include a `LICENSE` file in the repo if you plan to publish.

---

