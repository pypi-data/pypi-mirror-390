from .core import flatten, logger
from .fg import FG
import re

class Table:
    def __init__(self, 
                title="", justify="left",
                col_separator="|", row_separator="=",
                title_color=FG.white, col_color=FG.white,
                row_color=FG.white, col_separator_color=FG.white,
                row_separator_color=FG.white, cell_padding=0, row_height=1,
                # Borders (user can customize)
                top_left="+", top_right="+",
                bottom_left="+", bottom_right="+",
                horizontal="-", vertical="|",
                cross="+", left_cross="+",
                right_cross="+", top_cross="+",
                bottom_cross="+"):
        self.title = title
        self.justify = justify
        self.columns = []
        self.rows = []
        self.col_widths = []
        self.total_width = 0
        self.cell_padding = cell_padding
        self.row_height = max(1, row_height)

        # Colors
        self.title_color = title_color
        self.col_color = col_color
        self.row_color = row_color
        self.col_separator_color = col_separator_color
        self.row_separator_color = row_separator_color

        # Separator characters
        self.col_separator = col_separator
        self.row_separator = row_separator

        # Borders
        self.tl = top_left
        self.tr = top_right
        self.bl = bottom_left
        self.br = bottom_right
        self.h  = horizontal
        self.v  = vertical
        self.cross = cross
        self.lc = left_cross
        self.rc = right_cross
        self.tc = top_cross
        self.bc = bottom_cross

    def __str__(self):
        return f"<Table: {len(self.columns)} cols, {len(self.rows)} rows>"

    # --------------------------
    # Core Utilities
    # --------------------------
    def strip_ansi_codes(self, text) -> str:
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', str(text))

    def calcul_col_width(self) -> None:
        if not self.columns and not self.rows:
            return
        num_cols = max(len(self.columns), len(self.rows[0]) if self.rows else 0)
        self.col_widths = [0] * num_cols
        
        # Columns width
        for j in range(len(self.columns)):
            length = len(self.strip_ansi_codes(self.columns[j]))
            if length > self.col_widths[j]:
                self.col_widths[j] = length

        # Rows width
        for i in range(len(self.rows)):
            for j in range(len(self.rows[i])):
                length = len(self.strip_ansi_codes(self.rows[i][j]))
                if length > self.col_widths[j]:
                    self.col_widths[j] = length

        padding_length = len(self.cell_padding) if isinstance(self.cell_padding, str) else self.cell_padding
        if padding_length > 0:
            self.col_widths = [w + 2 * padding_length for w in self.col_widths]

    def complet_rows(self) -> None:
        for row in self.rows:
            while len(row) < len(self.columns):
                row.append("")

    def complet_columns(self, needed) -> None:
        for _ in range(needed):
            self.columns.append("")

    def add_column(self, *col) -> None:
        flat_col = flatten(col)
        self.columns.extend(flat_col)
        self.complet_rows()
        self.calcul_col_width()

    def add_row(self, *row) -> None:
        flat_row = flatten(row)
        if len(flat_row) > len(self.columns):
            self.complet_columns(len(flat_row) - len(self.columns))
        self.rows.append(flat_row)
        self.complet_rows()
        self.calcul_col_width()

    def reset_total_width(self) -> None:
        self.total_width = 0

    def calcul_total_width(self) -> None:
        if not self.col_widths:
            self.total_width = len(self.title) if self.title else 0
            return
        total_cols_width = sum(self.col_widths)
        separators_count = len(self.col_widths) + 1
        spaces_count = len(self.col_widths) * 2
        self.total_width = total_cols_width + separators_count + spaces_count - 1

    # --------------------------
    # Draw Utilities
    # --------------------------
    def draw_line(self, left, mid, right) -> None:
        line = left
        for i, w in enumerate(self.col_widths):
            line += self.h * (w + 2)
            if i < len(self.col_widths) - 1:
                line += mid
        line += right
        print(self.row_separator_color(line, AP=False))

    # --------------------------
    # Printing Table
    # --------------------------
    def print_table_title(self) -> None:
        if self.title:
            self.calcul_total_width()
            title_clean = self.strip_ansi_codes(self.title)
            spaces = max(0, (self.total_width - len(title_clean)) // 2)
            print(" " * spaces + self.title_color(self.title, AP=False) + "\n")

    def print_table(self) -> None:
        if not self.columns and not self.rows:
            print("[Info: No data to display]")
            return

        self.reset_total_width()
        self.calcul_col_width()
        self.calcul_total_width()
        self.print_table_title()

        # TOP BORDER
        self.draw_line(self.tl, self.tc, self.tr)

        # HEADER
        middle_line = self.row_height // 2
        for line_num in range(self.row_height):
            print(self.col_separator_color(self.v, AP=False), end="")
            for i, col in enumerate(self.columns):
                clean = self.strip_ansi_codes(col)
                if line_num == middle_line:
                    if self.justify == "center":
                        clean = clean.center(self.col_widths[i])
                    elif self.justify == "right":
                        clean = clean.rjust(self.col_widths[i])
                    else:
                        clean = clean.ljust(self.col_widths[i])
                else:
                    clean = " " * self.col_widths[i]
                print(" " + self.col_color(clean, AP=False) + " ", end="")
                print(self.col_separator_color(self.v, AP=False), end="")
            print()

        # HEADER SEPARATOR
        if self.rows:
            self.draw_line(self.lc, self.cross, self.rc)

        # ROWS
        for row_idx, row in enumerate(self.rows):
            for line_num in range(self.row_height):
                print(self.col_separator_color(self.v, AP=False), end="")
                for j, cell in enumerate(row):
                    clean = self.strip_ansi_codes(cell)
                    if line_num == middle_line:
                        if self.justify == "center":
                            clean = clean.center(self.col_widths[j])
                        elif self.justify == "right":
                            clean = clean.rjust(self.col_widths[j])
                        else:
                            clean = clean.ljust(self.col_widths[j])
                    else:
                        clean = " " * self.col_widths[j]
                    print(" " + self.row_color(clean, AP=False) + " ", end="")
                    print(self.col_separator_color(self.v, AP=False), end="")
                print()

            # SEPARATOR BETWEEN ROWS
            if row_idx < len(self.rows) - 1:
                self.draw_line(self.lc, self.cross, self.rc)

        # BOTTOM BORDER
        self.draw_line(self.bl, self.bc, self.br)

__tables_all__ = ["Table"]
