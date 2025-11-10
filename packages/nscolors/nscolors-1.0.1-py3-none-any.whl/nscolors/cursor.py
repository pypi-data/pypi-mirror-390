from .core import AllStatic, logger
from .core import mouvement_creator_method

class CURSOR(metaclass=AllStatic):
    def up(step=1, text: str = "") -> None: 
        mouvement_creator_method(step, "A", text)
    
    def down(step=1, text: str = "") -> None: 
        mouvement_creator_method(step, "B", text)
    
    def right(step=1, text: str = "") -> None: 
        mouvement_creator_method(step, "C", text)
    
    def left(step=1, text: str = "") -> None: 
        mouvement_creator_method(step, "D", text)
    
    def save_position() -> None: 
        print("\x1b[s", end="", flush=True)
    
    def restore_position() -> None: 
        print("\x1b[u", end="", flush=True)
    
    def clear_screen() -> None: 
        print("\x1b[2J", end="", flush=True)
    
    def home() -> None: 
        print("\x1b[H", end="", flush=True)
    
    def goto(row=0, col=0, text: str = "") -> None:

        try:
            row_int = max(0, int(row))
            col_int = max(0, int(col))
            mouvement_creator_method(0, "", text, x=col_int, y=row_int)
        except (ValueError, TypeError):
            mouvement_creator_method(0, "", text, x=0, y=0)
        except Exception as e:
            logger.error("[Goto Error: " + str(e) + "]")
    
    def hide_cursor() -> None:
        try:
            print("\x1b[?25l", end="", flush=True)
        except Exception as e:
            logger.error("[Hide Cursor Error: " + str(e) + "]")
    
    def show_cursor() -> None:
        try:
            print("\x1b[?25h", end="", flush=True)
        except Exception as e:
            logger.error("[Show Cursor Error: " + str(e) + "]")
    
    def clear_line() -> None:
        try:
            print("\x1b[2K", end="", flush=True)
        except Exception as e:
            logger.error("[Clear Line Error: " + str(e) + "]")

__cursor_all__ = ["CURSOR"]