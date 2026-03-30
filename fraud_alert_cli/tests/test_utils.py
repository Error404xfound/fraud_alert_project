import pytest
from utils import (
    get_input, 
    progress_bar,
    prompt_positive_value,
    prompt_transactions
)

# Test cases for get_input
def test_get_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "Hello World")
    assert get_input("Enter something: ") == "Hello World"

def test_get_input_ctrl_c(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: (_ for _ in ()).throw(KeyboardInterrupt))

    with pytest.raises(SystemExit):
        get_input("Enter something: ")

    captured = capsys.readouterr()
    assert "Program cancelled." in captured.out


def test_get_input_whitespace(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "   Hello World   ")
    assert get_input("Enter something: ") == "Hello World"


# Test cases for progress_bar
def test_progress_bar(capsys):
    progress_bar(duration=0.1, steps=5)  # Use shorter duration and fewer steps for testing
    captured = capsys.readouterr()
    assert "Analysing transactions... 100%" in captured.out
    assert "[" in captured.out and "]" in captured.out


def test_progress_bar_sleep_calls(monkeypatch):
    sleep_calls = []

    def fake_sleep(seconds):
        sleep_calls.append(seconds)

    monkeypatch.setattr("utils.time.sleep", fake_sleep)

    duration = 0.5
    steps = 5
    progress_bar(duration=duration, steps=steps)

    assert len(sleep_calls) == steps + 1
    assert all(s == pytest.approx(duration / steps) for s in sleep_calls)


def test_progress_bar_with_zero_duration(capsys):
    progress_bar(duration=0, steps=5)
    captured = capsys.readouterr()
    assert "Analysing transactions... 100%" in captured.out
    assert "[" in captured.out and "]" in captured.out


def test_progress_bar_with_one_step(capsys):
    progress_bar(duration=0.1, steps=1)
    captured = capsys.readouterr()
    assert "Analysing transactions... 100%" in captured.out
    assert "[" in captured.out and "]" in captured.out


def test_progress_bar_with_many_steps(capsys):
    progress_bar(duration=0.1, steps=100)
    captured = capsys.readouterr()
    assert "Analysing transactions... 100%" in captured.out
    assert "[" in captured.out and "]" in captured.out


def test_progress_bar_zero_division():
    with pytest.raises(ZeroDivisionError):
        progress_bar(duration=0.1, steps=0)


# Test cases for prompt_positive_value
def test_prompt_positive_value_accepts_valid_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "10")
    assert prompt_positive_value("Enter a positive number: ", float, "Invalid input") == 10.0


def test_prompt_positive_value_retries_until_valid(monkeypatch):
    inputs = iter(["abc", "-5", "0", "15"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    assert prompt_positive_value("Enter a positive number: ", float, "Invalid input") == 15.0


def test_prompt_positive_value_handles_float_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "3.5")
    assert prompt_positive_value("Enter a positive number: ", float, "Invalid input") == 3.5


def test_prompt_positive_value_handles_integer_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "5")
    assert prompt_positive_value("Enter a positive number: ", int, "Invalid input") == 5


def test_prompt_positive_value_whitespace_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "  20  ")
    assert prompt_positive_value("Enter a positive number: ", float, "Invalid input") == 20.0


def test_prompt_positive_value_zero_input(monkeypatch):
    inputs = iter(["0", "10"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    assert prompt_positive_value("Enter a positive number: ", float, "Invalid input") == 10.0


def test_prompt_positive_value_rejects_float_when_int_expected(monkeypatch):
    inputs = iter(["3.5", "5"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    assert prompt_positive_value("Enter a positive number: ", int, "Invalid input") == 5



# Test cases for prompt_transactions
def test_prompt_transactions_accepts_valid_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "100.00, 200.50, 3000.00")
    transactions = prompt_transactions(3)
    assert transactions == [100.00, 200.50, 3000.00]


def test_prompt_transactions_retries_until_valid(monkeypatch):
    inputs = iter(
        [
            "100.00, -50.00, 3000.00",  # Contains a negative value
            "100.00, abc, 3000.00",  # Contains a non-numeric value
            "100.00, 200.50",  # Not enough transactions
            " ",  # Empty input
            "100.00, 200.50, 3000.00",  # Valid input
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    transactions = prompt_transactions(3)
    assert transactions == [100.00, 200.50, 3000.00]


def test_prompt_transactions_handles_zero(monkeypatch):
    inputs = iter([
        "0, 100.00, 200.50",
        "100.00, 200.50, 3000.00",
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    transactions = prompt_transactions(3)
    assert transactions == [100.00, 200.50, 3000.00]


def test_prompt_transactions_negative_values(monkeypatch):
    inputs = iter([
        "100.00, -50.00, 3000.00",
        "100.00, 200.50, 3000.00",
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    transactions = prompt_transactions(3)
    assert transactions == [100.00, 200.50, 3000.00]


def test_prompt_transactions_non_numeric_values(monkeypatch):
    inputs = iter([
        "100.00, abc, 3000.00",
        "100.00, 200.50, 3000.00",
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    transactions = prompt_transactions(3)
    assert transactions == [100.00, 200.50, 3000.00]


def test_prompt_transactions_insufficient_values(monkeypatch):
    inputs = iter([
        "100.00, 200.50",
        "100.00, 200.50, 3000.00",
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    transactions = prompt_transactions(3)
    assert transactions == [100.00, 200.50, 3000.00]


def test_prompt_transactions_excess_values(monkeypatch):
    inputs = iter([
        "100.00, 200.50, 3000.00, 400.00",
        "100.00, 200.50, 3000.00",
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    transactions = prompt_transactions(3)
    assert transactions == [100.00, 200.50, 3000.00]


def test_prompt_transactions_empty_input(monkeypatch):
    inputs = iter([
        " ",
        "100.00, 200.50, 3000.00",
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    transactions = prompt_transactions(3)
    assert transactions == [100.00, 200.50, 3000.00]


def test_prompt_transactions_handles_whitespace(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "  100.00 , 200.50 , 3000.00  ")
    transactions = prompt_transactions(3)
    assert transactions == [100.00, 200.50, 3000.00]


def test_prompt_transactions_ignores_empty_entries(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "100.00, , 200.50, , 3000.00")
    transactions = prompt_transactions(3)
    assert transactions == [100.00, 200.50, 3000.00]


def test_prompt_transactions_handles_large_numbers(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "1000000.00, 2000000.50, 3000000.00")
    transactions = prompt_transactions(3)
    assert transactions == [1000000.00, 2000000.50, 3000000.00]


