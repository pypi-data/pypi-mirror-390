#!/usr/bin/env python3

# -- nercone-modern --------------------------------------------- #
# __main__.py on nercone-modern                                   #
# Made by DiamondGotCat, Licensed under MIT License               #
# Copyright (c) 2025 DiamondGotCat                                #
# ---------------------------------------------- DiamondGotCat -- #

import time
from nercone_modern.logging import ModernLogging
from nercone_modern.progressbar import ModernProgressBar

logger1 = ModernLogging("Main", display_level="DEBUG")
logger2 = ModernLogging("Sub", display_level="DEBUG")

try:
    logger1.log("This is a debug message", "DEBUG")
    logger1.log("This is a info message", "INFO")
    logger1.log("This is a info message", "INFO")
    logger1.log("This is a info message", "INFO")
    logger2.log("This is a info message", "INFO")
    logger1.log("This is a warning message", "WARNING")
    logger1.log("This is a error message", "ERROR")
    logger1.log("This is a critical error message", "CRITICAL")
    prompt_result = logger1.prompt("This is a Prompt. Let's try it: ")
    logger1.log(f"Answer is: {prompt_result}", "INFO")

    progress_bar1 = ModernProgressBar(total=100, process_name="Task 1", spinner_mode=False)
    progress_bar1.setMessage("WAITING")
    progress_bar2 = ModernProgressBar(total=200, process_name="Task 2", spinner_mode=True)
    progress_bar2.setMessage("WAITING")

    progress_bar1.start()
    progress_bar2.start()

    progress_bar1.setMessage("RUNNING")
    for i in range(100):
        time.sleep(0.05)
        progress_bar1.update()
    progress_bar1.setMessage("DONE")
    progress_bar1.finish()

    progress_bar2.spin_start()
    progress_bar2.setMessage("RUNNING (BACKGROUND)")
    for i in range(100):
        time.sleep(0.05)
        progress_bar2.update(2)
    progress_bar2.setMessage("DONE")
    progress_bar2.finish()
except KeyboardInterrupt:
    print()
    logger1.log("Aborted.", "INFO")
