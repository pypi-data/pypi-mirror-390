class ModernColor:
    def ansi_color_by_code(color_code: int | str = 0):
        return f"\033[{color_code}m"

    def ansi_color(color_name: str = "reset"):
        if color_name == "reset":
            return ModernColor.ansi_color_by_code(0)
        elif color_name == "black":
            return ModernColor.ansi_color_by_code(30)
        elif color_name == "red":
            return ModernColor.ansi_color_by_code(31)
        elif color_name == "green":
            return ModernColor.ansi_color_by_code(32)
        elif color_name == "yellow":
            return ModernColor.ansi_color_by_code(33)
        elif color_name == "blue":
            return ModernColor.ansi_color_by_code(34)
        elif color_name == "magenta":
            return ModernColor.ansi_color_by_code(35)
        elif color_name == "cyan":
            return ModernColor.ansi_color_by_code(36)
        elif color_name == "white":
            return ModernColor.ansi_color_by_code(37)
        elif color_name in ("gray", "grey"):
            return ModernColor.ansi_color_by_code(90)
        else:
            return ""

    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"
