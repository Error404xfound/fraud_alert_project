# Fraud Alert CLI

A Python command-line tool that checks transaction amounts and flags suspicious ones using:
- a hard rule threshold
- a z-score check against the overall transaction baseline

## Features
- Simple guided CLI flow
- Input validation for transaction count, sensitivity, and amount list
- Animated progress bar for analysis
- Clear summary of flagged transactions and reasons
- Transaction overview graph with highlighted suspicious points

## Project Structure
- `fraud_alert.py` main CLI app and detection flow
- `utils.py` shared input and terminal progress helpers

## Requirements
- Python 3.10+

## Dependencies
Install plotting support before running the app:

```bash
pip install matplotlib
```

## Run Locally
1. Open a terminal in this folder.
2. Run:

```bash
python fraud_alert.py
```

## Example Input
```text
How many transactions do you want to check?
(Enter a number greater than 0) : 5

How sensitive should the alert be? (Recommended: 3.5 for strict, 10.0+ for massive spikes)
(Enter a number greater than 0) : 3.5

Transactions: 100, 120, 140, 2200, 150
```

## Testing

Run the fraud-alert test suite:

```bash
pytest tests/test_fraud_alert.py
```

Run the utility test suite:

```bash
pytest tests/test_utils.py
```

Run all tests:

```bash
pytest
```

Or run with verbose output:

```bash
pytest -v
```

### Test Coverage

- **48 unit tests** total across both suites:
  - **21 tests** in `tests/test_fraud_alert.py` covering:
    - `check_rule_based()`: boundary and type-input behavior
    - `threshold_to_zscore()`: formula and zero-MAD behavior
    - `check_zscore()`: below/at/above-threshold and zero-MAD behavior
    - `detect_suspicious_transactions()`: no alerts, rule-only, z-score-only, zero-MAD, and indexing
    - `print_results()`: alert/no-alert output contracts
    - `show_graph()`: plotting call behavior via monkeypatch mocks
    - `main()`: orchestration flow with dependency stubs
  - **27 tests** in `tests/test_utils.py` covering:
  - `get_input()`: input capture, Ctrl+C handling, whitespace normalization
  - `progress_bar()`: output rendering, sleep behavior, edge cases
  - `prompt_positive_value()`: type coercion, validation retry loops
  - `prompt_transactions()`: list parsing, validation, count checking

All tests use mocking/monkeypatching where appropriate to avoid flaky I/O, timing, and GUI dependencies.

## Notes
- The app prints a terminal summary and then opens a matplotlib chart window.
- Alerts are produced by a fixed amount rule and a robust z-score check.

## Commit Scope Suggestion
If you are committing this project from a larger workspace, stage only this folder so the commit stays clean:

```bash
git add fraud_alert_cli
```

## Side Note
Fun fact: Originally, I started with AI-generated hackathon practice problems, then found this intermediate challenge and thought it looked fun, so I turned it into a CLI! (plus some other stuff)
Hope you think you find it as cool as I did :D
