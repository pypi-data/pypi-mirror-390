from .core import AllStatic, mode, handle, kernel32, csbi, logger, pattern
from .colors import ESC, CSI, RESET_STYLE, SEP, WinBGColors, WinFGColors, TextStyles, colors, BgColors, random_color_choices
from time import sleep
from random import choice, randint



class DIRECT(metaclass=AllStatic):

    
    def color(text : str = "", text_style : str = "Normal", color : str = None , bgcolor : str = None, AP=True) -> str:
        try:
            text_str = str(text) if text is not None else ""
            if mode == "ANSI":
                if color == None and bgcolor == None:
                    if AP:
                        print(text_str)
                        return ""
                    else:
                        return text_str
                if bgcolor == None:
                    colored_text = ESC + CSI + str(TextStyles[text_style]) + SEP + colors[color] + "m" + text_str + ESC + RESET_STYLE
                else:
                    colored_text = ESC + CSI + str(TextStyles[text_style]) + colors[color] + SEP + BgColors[bgcolor] + "m" + text_str + ESC + RESET_STYLE
                if AP:
                    print(colored_text)
                    return ""
                else:
                    return colored_text
            elif mode == "WINAPI":
                issuccess = kernel32.SetConsoleTextAttribute(handle, WinFGColors[color] | WinBGColors[bgcolor])
                if issuccess:
                    print(text_str)
                    kernel32.SetConsoleTextAttribute(handle, csbi.wAttributes)
                    return ""
                else:
                    return ""
        except KeyError as e:
            error_msg = "[Invalid key: " + str(e) + "] "
            logger.error(error_msg)
            return ""
        except TypeError as e:
            error_msg = "[Error: " + str(e) + "] "
            logger.error(error_msg)
            return ""
        except Exception as e:
            error_msg = "[Error: " + str(e) + "] "
            logger.error(error_msg)
            return ""



    def rgb(text : str = "", text_style : str = "Normal", R = 0, G = 0, B = 0, BR = 0, BG = 0, BB = 0, AP=True) -> str:
        try:
            text_str = str(text) if text is not None else ""
            if mode == "ANSI":
                colored_text = ESC + CSI + str(TextStyles[text_style]) + SEP + "38;2" + SEP + str(R) + SEP + str(G) + SEP + str(B) + SEP + "48;2" + SEP + str(BR) + SEP + str(BG) + SEP + str(BB) + "m" + text_str + ESC + RESET_STYLE
                if AP:
                    print(colored_text)
                    return ""
                else:
                    return colored_text
            elif mode == "WINAPI":
                colored_text = "[Error: unsupported platform windows < 10]"
                return ""
        except KeyError as e:
            logger.warning("[Invalid key: " + str(e) + "]")
            return ""
        except TypeError as e:
            logger.error("[Error: " + str(e) + "]")
            return ""
        except Exception as e:
            logger.error("[Error: " + str(e) + "]")
            return ""

    def animated_write(text : str = "", delay : float = 0, fg = None, bg = None) -> str:
        try:
            for char in text:
                out = char
                if fg and not bg: out = fg(out, AP=False)
                if bg and not fg: out = bg(out, AP=False)
                if bg and fg:
                    fg_colored = fg(char, AP=False)
                    bg_colored = bg(char, AP=False)
                    fg_code = fg_colored.replace(char, "").replace(ESC + RESET_STYLE, "")
                    bg_code = bg_colored.replace(char, "").replace(ESC + RESET_STYLE, "")
                    out = fg_code + bg_code + char
                if fg is None and bg is None: out = char
                print(out, end="", flush=True)
                sleep(delay)
            print("\x1b[0m")
        except Exception:
            print("\x1b[0m")


    def random_text_colored(text : str = "", text_style : str = "Normal", AP=True) -> str:
        out = "".join(DIRECT.color(c, text_style, choice(random_color_choices)) for c in text)
        if AP:
            print(out)
            return ""
        else:
            return out


    def random_rgb_text(text: str = "", text_style: str = "Normal", AP=True) -> str:
        colored_chars = []
        for char in text:
            R, G, B = [randint(0, 255) for _ in range(3)]
            try:
                colored_char = DIRECT.rgb(char, text_style, R, G, B, AP=False)
                colored_chars.append(colored_char)
            except Exception:
                colored_chars.append(char)
        result = "".join(colored_chars)
        if AP:
            print(result)
            return ""
        else:
            return result
    


    def color256(text : str = "", text_style="Normal", fg_code=0, bg_code=0, AP=True) -> str:
        try:
            if not (0 <= fg_code <= 255):
                raise ValueError("Foreground color code must be 0-255, got " + fg_code)
            if not (0 <= bg_code <= 255):
                raise ValueError(f"Background color code must be 0-255, got " + bg_code)
            if mode == "ANSI":
                int(fg_code)
                int(bg_code)
                text_str = str(text) if text is not None else ""
                colored_text = ESC + CSI + str(TextStyles[text_style]) + SEP + "38;5;" + str(fg_code) + SEP + "48;5;" + str(bg_code) + "m" + text_str + ESC + RESET_STYLE
                if AP:
                    print(colored_text)
                    return ""
                else:
                    return colored_text
            else:
                logger.error("[Unsupported Platform windows < 10]")
        except (ValueError, TypeError):
            raise RuntimeError("Unsupported Code: " + str(fg_code) + ", " + str(bg_code))
        except KeyError as e:
            return ESC + CSI + str(TextStyles["Normal"]) + ESC + "38;5" + str(fg_code) + SEP + "48;5;" + str(bg_code) + "m" + text_str + ESC + RESET_STYLE
        except Exception as e:
            logger.error("Error in color256: " + str(e))
            if AP:
                print(text_str)
                return ""
            else:
                return text_str

    def sprint(text, AP=True) -> str:
        finale_result = ""
        last_end = 0
        result = []
        for m in pattern.finditer(text):
            start, end = m.span()
            result.append(text[last_end:start])
            color, content = m.group("tag").capitalize(), m.group("body")
            result.append(f"\x1b[{colors.get(color, '37')}m{content}\x1b[0m")
            last_end = end
        result.append(text[last_end:])
        for i in range(len(result)):
            finale_result += result[i]
        if AP:
            print(finale_result)
            return ""
        else:
            return finale_result

__direct_all__ = ["DIRECT"]