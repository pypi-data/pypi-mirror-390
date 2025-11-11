from .core import AllStatic, kernel32, handle, mode, csbi, logger
from .colors import ESC, CSI, RESET_STYLE, WinBGColors



class BG(metaclass=AllStatic):

    def _print_bg(text : str, ansicode, wincolor, AP : bool = True) -> str:
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
                issuccess = kernel32.SetConsoleTextAttribute(handle, WinBGColors[wincolor])
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


    def black(text : str = "", AP : bool = True) -> str: return BG._print_bg(text, "40m", "Black", AP)
    def red(text : str = "", AP : bool = True) -> str: return BG._print_bg(text, "41m", "Red", AP)
    def green(text : str = "", AP : bool = True) -> str: return BG._print_bg(text, "42m", "Green", AP)
    def yellow(text : str = "", AP : bool = True) -> str: return BG._print_bg(text, "43m", "Yellow", AP)
    def blue(text : str = "", AP : bool = True) -> str: return BG._print_bg(text, "44m", "Blue", AP)
    def magenta(text : str = "", AP : bool = True) -> str: return BG._print_bg(text, "45m", "Magenta", AP)
    def cyan(text : str = "", AP : bool = True) -> str: return BG._print_bg(text, "46m", "Cyan", AP)
    def white(text : str = "", AP : bool = True) -> str: return BG._print_bg(text, "47m", "White", AP)
    def intense_black(text: str = "", AP : bool = True) -> str: return BG._print_bg(text, "100m", "Intense Black", AP)
    def intense_red(text: str = "", AP : bool = True) -> str: return BG._print_bg(text, "101m", "Intense Red", AP)
    def intense_green(text: str = "", AP : bool = True) -> str: return BG._print_bg(text, "102m", "Intense Green", AP)
    def intense_yellow(text: str = "", AP : bool = True) -> str: return BG._print_bg(text, "103m", "Intense Yellow", AP)
    def intense_blue(text: str = "", AP : bool = True) -> str: return BG._print_bg(text, "104m", "Intense Blue", AP)
    def intense_magenta(text: str = "", AP : bool = True) -> str: return BG._print_bg(text, "105m", "Intense Magenta", AP)
    def intense_cyan(text: str = "", AP : bool = True) -> str: return BG._print_bg(text, "106m", "Intense Cyan", AP)
    def intense_white(text: str = "", AP : bool = True) -> str: return BG._print_bg(text, "107m", "Intense White", AP)





__bg_all__ = ["BG"]
