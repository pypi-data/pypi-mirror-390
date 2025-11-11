from typing import Union
from .color import ModernColor

class ModernText:
    def __init__(self, content="", color: str = ModernColor.WHITE):
        self.content = content
        if not color.startswith("\033"):
            color = getattr(ModernColor, color.upper(), ModernColor.WHITE)
        self.color = color

    def __add__(self, other: Union[str, "ModernText"]):
        if isinstance(other, ModernText):
            if self.color == other.color:
                return ModernText(self.content + other.content, self.color)
            else:
                combined = f"{self.color}{self.content}{ModernColor.RESET}{other.color}{other.content}"
                return ModernText(combined, ModernColor.RESET)
        elif isinstance(other, str):
            return ModernText(self.content + other, self.color)
        else:
            raise TypeError(f"Unsupported operand type(s) for +: 'ModernText' and '{type(other).__name__}'")

    def __str__(self):
        return f"{self.color}{self.content}{ModernColor.RESET}"
