from .core import AllStatic, customizable_progress_method
from .fg import FG



class Progress(metaclass=AllStatic):

    def block(progress : float, total : float, length : float = 20, filled_color=FG.green, empty_color=FG.red, label="") -> None: customizable_progress_method(progress, total, length, "[", "]", "█", "░", filled_color, empty_color, label=label)

    def arabic(progress : float, total : float, length : float = 20, filled_color=FG.green, empty_color=FG.red, label="") -> None:  customizable_progress_method(progress, total, length, "⟨", "⟩", "■", "□", filled_color, empty_color, label=label)

    def professional(progress : float, total : float, length : float = 20, filled_color=FG.green, empty_color=FG.red, label="") -> None:  customizable_progress_method(progress, total, length, "|", "|", "▉", "▊", filled_color, empty_color, label=label)

    def minimal(progress : float, total : float, length : float = 20, filled_color=FG.green, empty_color=FG.red, label="") -> None:  customizable_progress_method(progress, total, length, "", "", "▪", "▫", filled_color, empty_color, label=label)

    def stars(progress : float, total : float, length : float = 20, filled_color=FG.green, empty_color=FG.red, label="") -> None:  customizable_progress_method(progress, total, length, "✨ ", " ✨", "⭐", "☆", filled_color, empty_color, label=label)

    def arrow(progress : float, total : float, length : float = 20, filled_color=FG.green, empty_color=FG.red, label="") -> None:  customizable_progress_method(progress, total, length, "> ", " <", "▶", "▷", filled_color, empty_color, label=label)

    def hearts(progress : float, total : float, length : float = 20, filled_color=FG.green, empty_color=FG.red, label="") -> None:  customizable_progress_method(progress, total, length, "❤️ ", " ❤️", "♥", "♡", filled_color, empty_color, label=label)








    def gradient(progress : float, total : float, length : float = 20, start_color=FG.red, middle_color=FG.yellow, end_color=FG.green, label=""):
        percent = progress / total
        if percent < 0.3:
            color = start_color
        elif percent < 0.7:
            color = middle_color
        else:
            color = end_color
        
        customizable_progress_method(progress, total, length, "[", "]","█", "░",  color, FG.white, label)







__progress_all__ = ["Progress"]