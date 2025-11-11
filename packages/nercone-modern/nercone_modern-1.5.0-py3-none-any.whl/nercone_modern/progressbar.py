#!/usr/bin/env python3

# -- nercone-modern --------------------------------------------- #
# progressbar.py on nercone-modern                                #
# Made by DiamondGotCat, Licensed under MIT License               #
# Copyright (c) 2025 DiamondGotCat                                #
# ---------------------------------------------- DiamondGotCat -- #

import sys
import threading

class ModernProgressBar:
    _active_bars = []
    _last_rendered = False
    _lock = threading.RLock()

    def __init__(self, total: int, process_name: str, spinner_mode=False):
        self.total = total
        self.spinner_mode = spinner_mode
        self.current = 0
        self.process_name = process_name.strip()
        self.index = len(ModernProgressBar._active_bars)
        ModernProgressBar._active_bars.append(self)
        self.log_lines = 0
        self.step = 0
        self.spinner_step = 0
        self.message = "No Message"
        self._spinner_thread = None
        self._spinner_stop_event = threading.Event()
        self._spinner_ready = False
        self._initial_render()

    def _initial_render(self):
        print()

    def spinner(self, enabled: bool = True):
        if self.spinner_mode == enabled:
            return
        self.spinner_mode = enabled
        if not self._spinner_ready:
            self._render(advance_spinner=False)
            return
        if enabled:
            self._start_spinner_thread_if_needed()
        else:
            self._stop_spinner_thread()
            self._render(advance_spinner=False)

    def spin_start(self):
        if self._spinner_ready and self.spinner_mode:
            return
        self._spinner_ready = True
        self.spinner_mode = True
        self.spinner_step = 0
        self._start_spinner_thread_if_needed()
        self._render(advance_spinner=False)

    def setMessage(self, message: str = ""):
        self.message = message

    def start(self):
        self._render(advance_spinner=False)
        self._start_spinner_thread_if_needed()

    def update(self, amount=1):
        if self._should_spin():
            self._render(advance_spinner=False)
            return
        self.current += amount
        if self.current > self.total:
            self.current = self.total
        self._render(advance_spinner=False)

    def finish(self):
        self.current = self.total
        self.spinner_mode = False
        self._spinner_ready = False
        self._stop_spinner_thread()
        self._render(final=True, advance_spinner=False)

    def makeModernLogging(self, process_name: str = None):
        from .logging import ModernLogging
        if not process_name:
            process_name = self.process_name
        return ModernLogging(process_name)

    def logging(self, message: str = "", level: str = "INFO", modernLogging=None):
        with ModernProgressBar._lock:
            self.log_lines = 0
            if modernLogging is None:
                modernLogging = self.makeModernLogging(self.process_name)
            result = modernLogging._make(message, level)
            if self.log_lines > 0:
                move_up = self.log_lines
            else:
                move_up = len(ModernProgressBar._active_bars) - self.index
            sys.stdout.write(f"\033[{move_up}A")
            sys.stdout.write("\033[K")
            print(result)
            self.log_lines += 1
            self._render(advance_spinner=False)

    def _start_spinner_thread_if_needed(self):
        if not self._should_spin():
            return
        if self._spinner_thread and self._spinner_thread.is_alive():
            return
        self._spinner_stop_event = threading.Event()
        self._spinner_thread = threading.Thread(target=self._spinner_worker, daemon=True)
        self._spinner_thread.start()

    def _stop_spinner_thread(self):
        if self._spinner_thread and self._spinner_thread.is_alive():
            self._spinner_stop_event.set()
            self._spinner_thread.join()
        self._spinner_thread = None

    def _spinner_worker(self):
        while not self._spinner_stop_event.wait(0.05):
            if not self._should_spin():
                continue
            self._render()

    def _render(self, final: bool = False, advance_spinner: bool = True):
        with ModernProgressBar._lock:
            progress = self.current / self.total if self.total else 0
            bar = self._progress_bar(progress, advance_spinner=advance_spinner and self._should_spin())
            percentage_value = int(round(min(max(progress, 0), 1) * 100))
            percentage = f"{percentage_value:3d}%"
            total_width = max(len(str(self.total)), 1)
            if final:
                status = "(DONE)"
            elif self.spinner_mode and self._spinner_ready:
                status = "(RUNN)"
            else:
                status = f"({self.current:>{total_width}}/{self.total})"
            line = f"({self._color('gray')}{bar}{self._color('reset')}) {self.process_name} - {'....' if self.spinner_mode else percentage} {status} | {self.message}"
            total_move_up = self.log_lines + (len(ModernProgressBar._active_bars) - self.index)
            if total_move_up > 0:
                sys.stdout.write(f"\033[{total_move_up}A")
            sys.stdout.write("\r")
            sys.stdout.write("\033[K")
            sys.stdout.write(line)
            sys.stdout.write("\n")
            down_lines = max(total_move_up - 1, 0)
            if down_lines > 0:
                sys.stdout.write(f"\033[{down_lines}B")
            sys.stdout.flush()

    def _progress_bar(self, progress: int, advance_spinner: bool = True):
        bar_length = 20
        if not self._should_spin():
            empty_bar = "-"
            if self.current == self.total:
                center_bar = ""
            else:
                center_bar = "-"
            filled_bar = "-"
            if self.current <= 0 and not self._spinner_ready:
                return f"{self._color('gray')}{empty_bar * (bar_length + 1)}"
            if self.current == self.total:
                filled_length = int(progress * bar_length) + 1
            else:
                filled_length = int(progress * bar_length)
            return f"{self._color('blue')}{filled_bar * filled_length}{self._color('cyan')}{center_bar}{self._color('gray')}{empty_bar * (bar_length - filled_length)}"
        else:
            if self.current <= 0 and not self._spinner_ready:
                return f"{self._color('gray')}{'-' * (bar_length + 1)}"
            spinner_symbol_length = 1
            spinner_end_bar_length = bar_length - self.spinner_step
            spinner_start_bar_length = bar_length - spinner_end_bar_length
            if advance_spinner:
                self.spinner_step = (self.spinner_step + 1) % (bar_length + 1)
            return f"{self._color('gray')}{'-' * spinner_start_bar_length}{self._color('blue')}{'-' * spinner_symbol_length}{self._color('gray')}{'-' * spinner_end_bar_length}"

    def _should_spin(self):
        return self.spinner_mode and self._spinner_ready

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
