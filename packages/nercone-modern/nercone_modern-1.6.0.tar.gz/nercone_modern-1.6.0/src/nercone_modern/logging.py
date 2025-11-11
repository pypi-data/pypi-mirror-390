#!/usr/bin/env python3

# -- nercone-modern --------------------------------------------- #
# logging.py on nercone-modern                                    #
# Made by DiamondGotCat, Licensed under MIT License               #
# Copyright (c) 2025 DiamondGotCat                                #
# ---------------------------------------------- DiamondGotCat -- #

ModernLoggingLevels = ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]
MAX_LOG_LEVEL_WIDTH = max(len(level) for level in ModernLoggingLevels)
LEVEL_ALIASES = {
    "D": "DEBUG",
    "DEBUG": "DEBUG",
    "I": "INFO",
    "INFO": "INFO",
    "INFORMATION": "INFO",
    "W": "WARN",
    "WARN": "WARN",
    "WARNING": "WARN",
    "E": "ERROR",
    "ERROR": "ERROR",
    "C": "CRITICAL",
    "CRITICAL": "CRITICAL"
}

_last_process = None
_last_level = None
_max_proc_width = 0

def normalize_level(level: str) -> str:
    level = level.strip().upper()
    return LEVEL_ALIASES.get(level, level)

def is_higher_priority(level_a: str, level_b: str) -> bool:
    a = normalize_level(level_a)
    b = normalize_level(level_b)
    try:
        return ModernLoggingLevels.index(a) >= ModernLoggingLevels.index(b)
    except ValueError:
        raise ValueError(f"Unknown log level: {level_a} or {level_b}")

class ModernLogging:
    def __init__(self, process_name: str = "App", display_level: str = "INFO", filepath: str | None = None):
        self.process_name = process_name
        self.display_level = display_level
        self.filepath = filepath
        global _max_proc_width
        _max_proc_width = max(_max_proc_width, len(process_name))

    def log(self, message: str = "", level_text: str = "INFO", level_color: str | None = None):
        if not is_higher_priority(level_text, self.display_level):
            return
        global _last_process, _last_level
        log_line = self.make(message=message, level_text=level_text, level_color=level_color)
        print(log_line)
        _last_process = self.process_name
        _last_level = normalize_level(level_text.strip().upper())
        if self.filepath:
            with open(self.filepath, "a") as f:
                f.write(f"{log_line}\n")

    def prompt(self, message: str = "", level_text: str = "INFO", level_color: str | None = None, ignore_kbdinterrupt: bool = True, default: str | None = None, choices: list[str] | None = None, show_choices: bool = True) -> str:
        if not is_higher_priority(level_text, self.display_level):
            return
        global _last_process, _last_level
        if default:
            message += f" ({default})"
        if choices and show_choices:
            message += f" [{'/'.join(choices)}]"
        if not message.endswith(" "):
            message += " "
        log_line = self.make(message=message, level_text=level_text, level_color=level_color)
        print(log_line, end="")
        _last_process = self.process_name
        _last_level = normalize_level(level_text.strip().upper())
        answer = ""
        try:
            answer = input()
        except KeyboardInterrupt:
            if ignore_kbdinterrupt:
                print()
            else:
                raise
        if answer.strip() == "" and default is not None:
            if choices:
                selected_default = self._select_choice(default, choices)
                if selected_default is not None:
                    answer = default
            else:
                answer = default
        if self.filepath:
            with open(self.filepath, "a") as f:
                f.write(f"{log_line}{answer}\n")
        if choices:
            selected = self._select_choice(answer, choices)
            if selected is not None:
                return selected
            else:
                while True:
                    log_line = self.make(message=f"Invalid selection. Please select from: {'/'.join(choices)}", level_text=level_text, level_color=level_color)
                    print(log_line, end="")
                    if self.filepath:
                        with open(self.filepath, "a") as f:
                            f.write(f"{log_line}{answer}\n")
                    log_line = self.make(message=message, level_text=level_text, level_color=level_color)
                    print(log_line, end="")
                    try:
                        answer = input()
                    except KeyboardInterrupt:
                        if ignore_kbdinterrupt:
                            print()
                        else:
                            raise
                    if self.filepath:
                        with open(self.filepath, "a") as f:
                            f.write(f"{log_line}{answer}\n")
                    if answer.strip() == "" and default is not None:
                        if choices:
                            selected_default = self._select_choice(default, choices)
                            if selected_default is not None:
                                return default
                        else:
                            return default
                    selected = self._select_choice(answer, choices)
                    if selected is not None:
                        return selected

    def _select_choice(self, answer: str, choices: list[str]) -> str | None:
        if answer in choices:
            return answer
        stripped = answer.strip()
        if stripped in choices:
            return stripped
        lower_map = {c.lower(): c for c in choices}
        if answer.lower() in lower_map:
            return lower_map[answer.lower()]
        if stripped.lower() in lower_map:
            return lower_map[stripped.lower()]
        return None

    def make(self, message: str = "", level_text: str = "INFO", level_color: str | None = None):
        level_text = normalize_level(level_text.strip().upper())
        show_proc = (self.process_name != _last_process)
        show_level = show_proc or (level_text != _last_level)

        if not level_color:
            if level_text == "DEBUG":
                level_color = 'gray'
            elif level_text == "INFO":
                level_color = 'blue'
            elif level_text == "WARN":
                level_color = 'yellow'
            elif level_text == "ERROR":
                level_color = 'red'
            elif level_text == "CRITICAL":
                level_color = 'red'
            else:
                level_color = 'blue'

        return self._make(message, level_text, level_color, show_proc, show_level)

    def _make(self, message: str, level_text: str, level_color: str, show_proc: bool, show_level: bool):
        global _max_proc_width
        level_width = max(MAX_LOG_LEVEL_WIDTH, len(level_text))

        proc_part = self.process_name if show_proc else ""
        proc_part = proc_part.ljust(_max_proc_width) if proc_part else " " * _max_proc_width

        if show_level:
            level_part = f"{self._color(level_color)}{level_text.ljust(level_width)} |{self._color('reset')}"
        else:
            level_part = (" " * level_width) + f"{self._color(level_color)} |{self._color('reset')}"

        return f"{proc_part} {level_part} {str(message)}"

    def _color(self, color_name: str = "reset"):
        if color_name == "cyan":
            return self._color_by_code(36)
        elif color_name == "magenta":
            return self._color_by_code(35)
        elif color_name == "yellow":
            return self._color_by_code(33)
        elif color_name == "green":
            return self._color_by_code(32)
        elif color_name == "red":
            return self._color_by_code(31)
        elif color_name == "blue":
            return self._color_by_code(34)
        elif color_name == "white":
            return self._color_by_code(37)
        elif color_name == "black":
            return self._color_by_code(30)
        elif color_name in ("gray", "grey"):
            return self._color_by_code(90)
        elif color_name == "reset":
            return self._color_by_code(0)
        else:
            return ""

    def _color_by_code(self, color_code: int | str = 0):
        return f"\033[{color_code}m"
