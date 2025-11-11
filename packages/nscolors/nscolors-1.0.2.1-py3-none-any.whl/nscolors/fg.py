from .core import AllStatic, handle, kernel32, mode, csbi, logger
from .colors import ESC, CSI, RESET_STYLE, WinFGColors


class FG(metaclass=AllStatic):

    def _print_fg(text : str, ansicode, wincolor, AP : bool = True) -> str:
        try:
            text_str = str(text) if text is not None else ""
            if mode == "ANSI":
                colored_text = ESC + CSI + ansicode + text_str + ESC + RESET_STYLE
                if AP:
                    print(colored_text)
                    return ""
                else:
                    return colored_text
            elif mode == "WINAPI":
                if handle is None or kernel32 is None:
                    raise RuntimeError("[Error: system not ready]")
                issuccess = kernel32.SetConsoleTextAttribute(handle, WinFGColors[wincolor])
                if issuccess:
                    print(text_str, end="", flush=True)
                    kernel32.SetConsoleTextAttribute(handle, csbi.wAttributes)
                else:
                    raise RuntimeError("[Unexpected error]")
        except (ValueError, TypeError) as e:
            error_msg = "[Value Error: " + str(e) + "]"
            logger.error(error_msg)
            return ""
            
        except (OSError, WindowsError) as e:
            error_msg = "[System Error: " + str(e) + "]"
            logger.error(error_msg)
            return ""
            
        except KeyError as e:
            error_msg = "[Color '" + str(wincolor) + "' not found]"
            logger.error(error_msg)
            return ""
            
        except Exception as e:
            error_msg = "[Unexpected: " + str(type(e).__name__) + "]"
            logger.error(error_msg)
            return ""


    def black(text : str, AP : bool = True) -> str: return FG._print_fg(text, "0;30m", "Black", AP)
    def red(text : str, AP : bool = True) -> str: return FG._print_fg(text, "0;31m", "Red", AP)
    def green(text : str, AP : bool = True) -> str: return FG._print_fg(text, "0;32m", "Green", AP)
    def yellow(text : str, AP : bool = True) -> str: return FG._print_fg(text, "0;33m", "Yellow", AP)
    def blue(text : str, AP : bool = True) -> str: return FG._print_fg(text, "0;34m", "Blue", AP)
    def magenta(text : str, AP : bool = True) -> str: return FG._print_fg(text, "0;35m", "Magenta", AP)
    def cyan(text : str, AP : bool = True) -> str: return FG._print_fg(text, "0;36m", "Cyan", AP)
    def white(text : str, AP : bool = True) -> str: return FG._print_fg(text, "0;37m", "White", AP)
    def intense_black(text: str, AP : bool = True) -> str: return FG._print_fg(text, "0;90m", "Intense Black", AP)
    def intense_red(text: str, AP : bool = True) -> str: return FG._print_fg(text, "0;91m", "Intense Red", AP)
    def intense_green(text: str, AP : bool = True) -> str: return FG._print_fg(text, "0;92m", "Intense Green", AP)
    def intense_yellow(text: str, AP : bool = True) -> str: return FG._print_fg(text, "0;93m", "Intense Yellow", AP)
    def intense_blue(text: str, AP : bool = True) -> str: return FG._print_fg(text, "0;94m", "Intense Blue", AP)
    def intense_magenta(text: str, AP : bool = True) -> str: return FG._print_fg(text, "0;95m", "Intense Magenta", AP)
    def intense_cyan(text: str, AP : bool = True) -> str: return FG._print_fg(text, "0;96m", "Intense Cyan", AP)
    def intense_white(text: str, AP : bool = True) -> str: return FG._print_fg(text, "0;97m", "Intense White", AP)


__fg_all__ = ["FG"]