from os import path
from .core import LoadPalette


ESC = "\x1B"
SEP = ";"
CSI = "["
RESET_STYLE = "[0m"


BASE_DIR = path.dirname(__file__)
ansi16_fg_colors_file_name = path.join(BASE_DIR, "palettes/ansi16_fg_palette.json")
ansi16_bg_colors_file_name = path.join(BASE_DIR, "palettes/ansi16_bg_palette.json")
text_styles_file_name  = path.join(BASE_DIR, "palettes/text_styles.json")
winapi_fg_colors_file_name = path.join(BASE_DIR, "palettes/winapi_fg_palette.txt")
winapi_bg_colors_file_name = path.join(BASE_DIR, "palettes/winapi_bg_palette.txt")


colors = LoadPalette(ansi16_fg_colors_file_name)
BgColors = LoadPalette(ansi16_bg_colors_file_name)
TextStyles = LoadPalette(text_styles_file_name)
WinFGColors = LoadPalette(winapi_fg_colors_file_name)
WinBGColors = LoadPalette(winapi_bg_colors_file_name)


random_color_choices = ["Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White", "Bright Black", "Bright Red", "Bright Green", "Bright Yellow", "Bright Blue", "Bright Magenta", "Bright Cyan", "Bright White"]


__colors_all__ = ["ESC", "SEP", "CSI", "colors", "TextStyles", "RESET_STYLE", "BgColors", "random_color_choices", "WinFGColors", "WinBGColors"]
