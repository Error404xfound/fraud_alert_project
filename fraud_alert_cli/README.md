# Fraud Alert CLI

A Python command-line tool that checks transaction amounts and flags suspicious ones using:
- a hard rule threshold
- a z-score check against the overall transaction baseline

## Features
- Simple guided CLI flow
- Input validation for transaction count, sensitivity, and amount list
- Animated progress bar for analysis
- Clear summary of flagged transactions and reasons

## Project Structure
- `fraud_alert.py` main CLI app and detection flow
- `utils.py` shared input and terminal progress helpers

## Requirements
- Python 3.10+

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

How sensitive should the alert be? (Recommended: 3.0 - higher means fewer alerts)
(Enter a number greater than 0) : 2.5

Transactions: 100, 120, 140, 2200, 150
```

## Commit Scope Suggestion
If you are committing this project from a larger workspace, stage only this folder so the commit stays clean:

```bash
git add fraud_alert_cli
```

## Side Note
Fun fact: Originally, I started with AI-generated hackathon practice problems, then found this intermediate challenge and thought it looked fun, so I turned it into a CLI! (plus some other stuff)
Hope you think you find it as cool as I did :D
