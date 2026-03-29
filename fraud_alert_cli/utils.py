"""Shared terminal helpers used by CLI scripts in this folder."""

import random
import string
import time


def get_input(prompt):
    """Read user input and handle Ctrl+C gracefully."""
    while True:
        try:
            return input(prompt).strip()
        except KeyboardInterrupt:
            print("\nProgram cancelled.")
            exit()


def progress_bar(duration=3.0, steps=50):
    """Render the animated analysis bar used in terminal tools."""
    bar_width = 44

    for i in range(steps + 1):
        percent = int((i / steps) * 100)
        filled = int((i / steps) * bar_width)
        # Keep random noise on the unfilled side for the same visual style.
        unfilled = "".join(
            random.choice(string.digits + string.punctuation)
            for _ in range(bar_width - filled)
        )
        bar = "=" * filled + unfilled

        print(f"\r Analysing transactions... {percent:>3}% ")
        print(f"[{bar}]", end="\033[A\r")
        time.sleep(duration / steps)

    print("\r Analysing transactions... 100% ")
    print(f"[{'=' * bar_width}]")
