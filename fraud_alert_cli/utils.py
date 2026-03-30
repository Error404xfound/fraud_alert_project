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

def prompt_positive_value(prompt, cast_type, invalid_type_message):
    """Prompt until a positive numeric value is provided."""
    while True:
        try:
            value = cast_type(get_input(prompt))
            if value > 0:
                return value
            print("Please enter a number greater than 0.")
        except ValueError:
            print(invalid_type_message)

def prompt_transactions(expected_count):
    """Prompt until the exact expected number of transaction values is entered."""
    print(f"\nEnter {expected_count} transaction amounts, separated by commas.")
    print("Example: 100.00, 200.50, 3000.00, 150.00, 175.00")

    while True:
        try:
            raw = get_input("\nTransactions: ")
            transactions = [float(x.strip()) for x in raw.split(",") if x.strip()] # Only include non-empty entries after stripping whitespace.

            if any(x <= 0 for x in transactions):
                print("All transaction amounts must be greater than 0. Please try again.")
                continue

            if len(transactions) == expected_count:
                return transactions
            print(f"You entered {len(transactions)} transaction(s). Please enter exactly {expected_count}.")
        except ValueError:
            print(
                "Some values were invalid. Please use numbers separated by commas "
                "(e.g. 100, 200, 300)."
            )