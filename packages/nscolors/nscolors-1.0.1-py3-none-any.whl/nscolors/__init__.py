from .core import GetSystemInfo, init, AllStatic, handle, kernel32, mode, csbi, LoadPalette, flatten, customizable_progress_method, mouvement_creator_method, logger, __core_all__

AllInfo = GetSystemInfo()
init()

from .fg import __fg_all__, FG
from .bg import __bg_all__, BG
from .direct import __direct_all__, DIRECT
from .colors import ESC, SEP, CSI, colors, TextStyles, RESET_STYLE, BgColors, random_color_choices, WinFGColors, WinBGColors, __colors_all__
from .progress import __progress_all__, Progress
from .cursor import __cursor_all__, CURSOR
from .tables import __tables_all__, Table


__all__ = __colors_all__ + __core_all__ + __bg_all__ + __fg_all__ + __direct_all__ + __progress_all__ + __cursor_all__ + __tables_all__ + ["AllInfo"]
__name__ = "nscolors"
__author__ = "NullSpecter404"
__version__ = "1.0.0"