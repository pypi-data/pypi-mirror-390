from platform import system, version, release
from ast import literal_eval
from json import load
import logging
import re

handle = None
kernel32 = None
csbi = None


logger = logging.getLogger("nscolors")

file_mode = None
pattern = re.compile(r"<(?P<tag>\w+)>(?P<body>.*?)</(?P=tag)>", re.DOTALL)

try:
    if system().lower() == "windows":
        from ctypes import Structure, c_short, c_ushort, byref, windll
        class COORD(Structure):
            _fields_ = [("X", c_short), ("Y", c_short)]

        class SMALL_RECT(Structure):
            _fields_ = [("Left", c_short), ("Top", c_short),
                        ("Right", c_short), ("Bottom", c_short)]

        class CONSOLE_SCREEN_BUFFER_INFO(Structure):
            _fields_ = [
                ("dwSize", COORD),
                ("dwCursorPosition", COORD),
                ("wAttributes", c_ushort),
                ("srWindow", SMALL_RECT),
                ("dwMaximumWindowSize", COORD)
            ]

        kernel32 = windll.kernel32
        STD_OUTPUT_HANDLE = -11
        handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        csbi = CONSOLE_SCREEN_BUFFER_INFO()

        if kernel32.GetConsoleScreenBufferInfo(handle, byref(csbi)):
            pass
        else:
            raise RuntimeError("Failed to get console info")
except Exception as e:
    raise RuntimeError("[Error: " + str(e) + "]")


class AllStatic(type):
    def __new__(cls, name, bases, dct):
        new_dict = {}
        for k, v in dct.items():
            if k.startswith("__") and k.endswith("__"):
                new_dict[k] = v
                continue
            if callable(v):
                new_dict[k] = staticmethod(v)
            elif isinstance(v, type):
                new_dict[k] = AllStatic(v.__name__, v.__bases__, dict(v.__dict__))
            else:
                new_dict[k] = v
        return super().__new__(cls, name, bases, new_dict)



mode = None
AllInfo = None

def GetSystemInfo() -> tuple:
    global mode, AllInfo
    info = {
        "system": system(),
        "release": release(),
        "version": version(),
    }
    
    if info["system"].lower() == "windows":
        rel = info["release"]
        try:
            rel_num = int(rel)
        except ValueError:
            mapping = {"XP": 5, "Vista": 6, "7": 7, "8": 8, "8.1": 8, "10": 10, "11": 11}
            rel_num = mapping.get(rel, 10)
        
        if rel_num >= 10:
            mode = "ANSI"
        else:
            mode = "WINAPI"
    else:
        mode = "ANSI"
    
    AllInfo = (mode, info)
    return AllInfo

def WinSetup() -> None:
    try:
        global kernel32, handle
        if AllInfo is None:
            GetSystemInfo()

        mode, info = AllInfo
        if mode == "ANSI" and info["system"].lower() == "windows":
            kernel32 = windll.kernel32
            handle = kernel32.GetStdHandle(-11)
        elif mode == "WINAPI":
            kernel32 = windll.kernel32
            handle = kernel32.GetStdHandle(-11)
    except Exception as e:
        logger.warning("Error: " + str(e) + "]")

def init() -> None:
    if AllInfo is None:
        GetSystemInfo()
    if kernel32 is None or handle is None:
        WinSetup()
    
    mode, info = AllInfo
    if mode == "ANSI" and info["system"].lower() == "windows":
        kernel32.SetConsoleMode(handle, 0x0004 | 0x0001 | 0x0002)


def LoadPalette(file_name) -> dict:
    try:
        global file_mode
        if file_name.endswith(".json"):
            file_mode = "json"
        elif file_name.endswith(".txt"):
            file_mode = "txt"
        with open(file_name, "r", encoding="utf-8") as file:
            if file_mode == "json":
                data = load(file)
                return data
            elif file_mode == "txt":
                data = literal_eval(file.read())
                ToHexDict = {}
                for key, value in data.items():
                    ToHexDict[key] = hex(value)
                return ToHexDict
    except Exception as e:
        raise RuntimeError("Error: " + str(e) + "]")


def flatten(items) -> list:
    result = []
    for item in items:
        if isinstance(item, (list, tuple)):
            result.extend(flatten(item))
        else:
            result.append(str(item))
    return result


def customizable_progress_method(progress : float, total : float, length : float ,start_char : str, end_char : str, filled_char : str, empty_char : str, filled_color, empty_color, label : str = "") -> None:
    try:
        points = "" if label == "" else " : "
        if total == 0:
            percent = 0
        else:
            percent = progress / total
        percent = max(0.0, min(percent, 1.0))
        filled = int(length*percent)
        bar = filled_color(filled_char, AP=False) * filled + empty_color(empty_char, AP=False) * (length - filled)
        print(label + points + start_char + bar + end_char + " " + str(int(percent*100)) + "%",end="\r", flush=True)
        if percent >= 1.0:
            print()
    except Exception as e:
        error_msg = "[Progress Error: " + str(e) + "]"
        logger.error(error_msg)


def mouvement_creator_method(step, direction, text, x=None, y=None) -> None:
    global csbi
    try:
        step_int = int(step)
        step_int = max(1, step_int)
    except (ValueError, TypeError):
        logger.warning("[Unsupported Value: " + str(step) + "]")
        return

    try:
        xi = yi = None
        if x is not None and y is not None:
            try:
                xi = int(x)
                yi = int(y)
            except (ValueError, TypeError):
                logger.warning("Invalid cursor coordinates: x=" + str(x) + ", y=" + str(y) + ". Falling back to relative movement.")
                xi = yi = None


        if xi is not None and yi is not None:
            if mode == "ANSI":
                row = max(0, yi) + 1
                col = max(0, xi) + 1
                try:
                    print("\x1b[" + str(row) + ";" + str(col) + "H", end="", flush=True)
                except Exception:

                    pass

                try:
                    if 'kernel32' in globals() and kernel32 is not None and 'SetConsoleCursorPosition' in dir(kernel32):
                        try:
                            coord = COORD(xi, yi)
                            kernel32.SetConsoleCursorPosition(handle, coord)
                        except Exception:
                            pass
                except Exception:
                    pass

                if text:
                    print(text, end="", flush=True)
                return

            elif mode == "WINAPI":
                try:
                    try:
                        kernel32.GetConsoleScreenBufferInfo(handle, byref(csbi))
                    except Exception:
                        pass

                    try:
                        max_x = int(csbi.dwSize.X) - 1
                        max_y = int(csbi.dwSize.Y) - 1
                    except Exception:
                        max_x = None
                        max_y = None

                    if max_x is not None and max_y is not None:
                        if xi < 0 or yi < 0 or xi > max_x or yi > max_y:
                            logger.warning("Cursor coords out of range: (" + str(xi) + "," + str(yi) + "). Clamping to buffer bounds.")
                            xi = max(0, min(xi, max_x))
                            yi = max(0, min(yi, max_y))

                    coord = COORD(xi, yi)
                    res = kernel32.SetConsoleCursorPosition(handle, coord)
                    if not res:
                        logger.warning("SetConsoleCursorPosition failed for (" + str(xi) + "," + str(yi) + ").")
                except Exception as e:
                    logger.warning("WINAPI cursor positioning failed: " + str(e))

                if text:
                    print(text, end="", flush=True)
                return

        if mode == "ANSI":
            try:
                print("\x1b[" + str(step_int) + str(direction), end="", flush=True)
            except Exception:
                pass
            if text:
                print(text, end="", flush=True)
            return

        elif mode == "WINAPI":
            try:
                try:
                    kernel32.GetConsoleScreenBufferInfo(handle, byref(csbi))
                except Exception:
                    pass


                try:
                    cur = csbi.dwCursorPosition
                    cur_x = int(cur.X)
                    cur_y = int(cur.Y)
                except Exception:

                    cur_x = 0
                    cur_y = 0

                new_x = cur_x
                new_y = cur_y
                d = str(direction)
                if d == "A":
                    new_y = cur_y - step_int
                elif d == "B":
                    new_y = cur_y + step_int
                elif d == "C":
                    new_x = cur_x + step_int
                elif d == "D":
                    new_x = cur_x - step_int
                else:
                    pass

                try:
                    max_x = int(csbi.dwSize.X) - 1
                    max_y = int(csbi.dwSize.Y) - 1
                except Exception:
                    max_x = None
                    max_y = None

                if max_x is not None and max_y is not None:
                    new_x = max(0, min(new_x, max_x))
                    new_y = max(0, min(new_y, max_y))

                coord = COORD(new_x, new_y)
                res = kernel32.SetConsoleCursorPosition(handle, coord)
                if not res:
                    logger.warning("SetConsoleCursorPosition failed for (" + str(new_x) + "," + str(new_y) + ").")
            except Exception as e:
                logger.error("[Cursor Error: " + str(e) + "]")

            if text:
                print(text, end="", flush=True)
            return

    except Exception as e:
        error_msg = "[Cursor Error: " + str(e) + "]"
        logger.error(error_msg)





__core_all__ = ["AllStatic", "handle", "kernel32", "mode", "AllInfo", "GetSystemInfo", "init", "csbi", "LoadPalette", "flatten", "customizable_progress_method", "mouvement_creator_method", "logger"]



