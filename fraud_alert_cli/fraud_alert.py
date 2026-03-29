"""CLI tool to flag suspicious transactions using rule and z-score checks."""

import statistics
from utils import get_input, progress_bar


RULE_THRESHOLD = 1000.0
WELCOME_BANNER_WIDTH = 60
PROGRESS_DURATION = 1.6


def check_rule_based(amount):
    """Hard threshold check for obviously high transaction values."""
    return amount > RULE_THRESHOLD


def check_zscore(amount, mean, sigma, threshold):
    """Flag transactions whose z-score exceeds the selected sensitivity."""
    if sigma == 0:
        return False, None, None

    z = (amount - mean) / sigma
    if z > threshold:
        return True, z, f"Z-score={z:.2f} > threshold={threshold:.2f}"

    return False, z, None


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
            transactions = [float(x.strip()) for x in raw.split(",") if x.strip()]
            if len(transactions) == expected_count:
                return transactions
            print(f"You entered {len(transactions)} transaction(s). Please enter exactly {expected_count}.")
        except ValueError:
            print(
                "Some values were invalid. Please use numbers separated by commas "
                "(e.g. 100, 200, 300)."
            )


def detect_suspicious_transactions(transactions, threshold):
    """Run the detection rules and return alert totals and details."""
    alerts = 0
    alerted_transactions = []
    alerted_details = []

    # Global baseline for z-score checks.
    overall_mean = statistics.mean(transactions)
    overall_sigma = statistics.pstdev(transactions)

    for i, transaction in enumerate(transactions):
        reasons = []

        if check_rule_based(transaction):
            reasons.append(f"Rule: amount ({transaction:.2f}) > {RULE_THRESHOLD:.0f}")

        z_flagged, z_value, z_reason = check_zscore(transaction, overall_mean, overall_sigma, threshold)
        if z_flagged:
            reasons.append(z_reason)

        if reasons:
            alerts += 1
            txn_number = i + 1
            alerted_transactions.append(txn_number)
            alerted_details.append((txn_number, transaction, reasons))

    return alerts, alerted_transactions, alerted_details


def print_results(alerts, alerted_transactions, alerted_details):
    """Print the final report in the existing terminal UI format."""
    print("\n" + "=" * WELCOME_BANNER_WIDTH)
    print(f"\nTotal suspicious transactions detected: {alerts}")

    if alerted_transactions:
        print(f"Transaction number(s) flagged: {', '.join(map(str, alerted_transactions))}")
        print("Flagged transaction amount(s):")
        for txn_number, txn_amount, reasons in alerted_details:
            print(f"  - Transaction {txn_number}: {txn_amount:.2f}")
            for reason in reasons:
                print(f"      ↳ {reason}")

        total_flagged_spending = sum(amount for _, amount, _ in alerted_details)
        print(f"Total flagged spending amount: {total_flagged_spending:.2f}")
        print("\nNote: These transactions were unusually high compared to overall activity.")
        print("      Consider reviewing them for potential fraud or errors.")
    else:
        print("\nNo suspicious activity detected. All transactions look normal!")

    print("\n" + "=" * WELCOME_BANNER_WIDTH)


def main():
    """Drive input collection, analysis, and final reporting."""
    print("=" * WELCOME_BANNER_WIDTH)
    print("   Welcome to the Transaction Checker      ")
    print("=" * WELCOME_BANNER_WIDTH)

    n = prompt_positive_value(
        "\nHow many transactions do you want to check?\n"
        "(Enter a number greater than 0) : ",
        int,
        "Please enter a whole number (e.g. 5).",
    )

    t = prompt_positive_value(
        "\nHow sensitive should the alert be? "
        "(Recommended: 3.0 - higher means fewer alerts)\n"
        "(Enter a number greater than 0) : ",
        float,
        "Please enter a number (e.g. 3.0).",
    )

    transactions = prompt_transactions(n)

    print()
    progress_bar(duration=PROGRESS_DURATION)

    alerts, alerted_transactions, alerted_details = detect_suspicious_transactions(transactions, t)
    print_results(alerts, alerted_transactions, alerted_details)


if __name__ == "__main__":
    main()