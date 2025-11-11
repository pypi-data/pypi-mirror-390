# NSColors

A cross‑platform terminal styling library for Python with **no external
dependencies**.\
It provides **colors, tables, progress bars, cursor control, formatted
printing, and rich text tags** --- all lightweight and customizable.

------------------------------------------------------------------------

## ✅ Features

### 🎨 Colors (FG / BG)

-   Foreground and background colors (standard + bright).
-   Custom tags like: `<red>text</red>` or `<bg-blue>text</bg-blue>`.
-   Works on Linux, macOS, and Windows without extra dependencies.

### 🖨 DIRECT --- Smart Text Printing

The `DIRECT` module allows advanced styled printing using BBCode‑like
tags.

#### **DIRECT.sprint(text: str)**

Smart print that parses tags inside a string.

**Example:**

``` python
from nscolors import DIRECT

DIRECT.sprint("Hello <red>Red Text</red> and <green>Green Text</green>!")
```

**Supported tags:** - `<red>…</red>` - `<green>…</green>` -
`<blue>…</blue>` - `<yellow>…</yellow>` - `<magenta>…</magenta>` -
`<cyan>…</cyan>` - `<white>…</white>` - `<black>…</black>` -
Nested tags supported.

------------------------------------------------------------------------

## 📌 DIRECT --- Methods Overview

### ✅ `DIRECT.color(text, text_style, color, bgcolor, AP)`

Returns text wrapped in ANSI color codes.

### ✅ `DIRECT.random_text_colored(text, text_style, AP)`

Random color output (useful for fancy progress bars).

### ✅ `DIRECT.sprint(text, AP)`

Prints parsed text directly.

------------------------------------------------------------------------

## 🧭 Cursor Module

The `cursor` module gives you full control over terminal positioning.

### ✅ Methods

  Method                   Description
  ------------------------ -----------------------------------
  `cursor.move_up(n, text)`      Move cursor *n* lines up
  `cursor.move_down(n, text)`    Move down
  `cursor.move_left(n, text)`    Move left
  `cursor.move_right(n, text)`   Move right
  `cursor.goto(x, y, text)`      Move to absolute position
  `cursor.save()`          Save current cursor position
  `cursor.restore()`       Restore previously saved position
  `cursor.clear()`         Clear entire screen
  `cursor.clear_line()`    Clear current line

**Example:**

``` python
from nscolors import cursor

cursor.move_up(2, "Placed text")
cursor.move_right(10, "Placed text")
```

------------------------------------------------------------------------

## 📊 Table Module

Highly customizable table generator.

### ✅ Table Features

-   Custom borders
-   Custom separators
-   Padding control
-   Title with color and alignment
-   Row height customization
-   Full border & margin customization

### ✅ Example

``` python
from nscolors import Table, FG

table = Table(
    title="Example Table",
    justify="center",
    col_separator="|",
    row_separator="=",
    title_color=FG.green,
    col_color=FG.cyan,
    row_color=FG.yellow,
    cell_padding=1
)

table.add_row(["Name", "Age", "Country"]) or table.add_row("Name", "Age", "Country") or table.add_row(("Name", "Age", "Country"))
table.add_row(["Jhon", "18", "USA"]) or table.add_row("Jhon", "18", "USA") or table.add_row(("Jhon", "18", "USA"))

table.render()
```

### ✅ Border & Margin Customization

You can modify:

-   `col_separator` → border between columns\
-   `row_separator` → border between rows\
-   `cell_padding` → space around each cell\
-   `row_height` → number of lines per row\
-   `*_color` → colors for each part

------------------------------------------------------------------------

## ⏳ Progress Bars

A set of customizable progress bar generators.

### ✅ Example

``` python
from nscolors import Progress

core.customizable_progress_method(
    progress=40,
    total=100,
    length=30,
    start_char="[",
    end_char="]",
    filled_char="=",
    empty_char=".",
    filled_color="green",
    empty_color="red",
    label="Loading"
)
```

### ✅ Features

-   Full control over characters
-   Full color customization
-   Labels
-   Dynamic update capability

------------------------------------------------------------------------

## 🛠 Installation

``` bash
pip install nscolors
```

------------------------------------------------------------------------

## 📚 Basic Usage

``` python
from nscolors import FG, DIRECT

DIRECT.sprint("<green>Hello World!</green>")
FG.red("this is red")
BG.green("this is green background")
red_text = FG.red("this is red", AP=False)
green_back = BG.green("this is green background", AP=False)
```

## Note

- AP ---> Auto Print
- if True (print text directly) if False (return colored text)

------------------------------------------------------------------------

## 🧱 Project Structure

-   `FG.py` --- Foreground colors\
-   `BG.py` --- Background colors\
-   `DIRECT.py` --- Tag printing engine\
-   `cursor.py` --- Terminal cursor control\
-   `Table.py` --- Table generator\
-   `Progress.py` --- Progress bars

------------------------------------------------------------------------

## ✅ Future Improvements

-   Adding themes\
-   Auto column width detection\
-   Table highlighting

------------------------------------------------------------------------

## 🏁 Final Notes

NSColors is built to be:

✅ Lightweight\
✅ Dependency-free\
✅ Beginner-friendly\
✅ Highly customizable

Perfect for CLI tools, dashboards, renderers, and hacking utilities.

------------------------------------------------------------------------

## 💬 Author

**NullSpecter404**\
GitHub: *(https://github.com/NullSpecter404/nscolors-project)*

------------------------------------------------------------------------
