"""CLI tool to flag suspicious transactions using rule and z-score checks."""

import statistics
import matplotlib.pyplot as plt
from utils import ( 
    progress_bar, 
    prompt_positive_value, 
    prompt_transactions
)


RULE_THRESHOLD = 1000.00
WELCOME_BANNER_WIDTH = 60
PROGRESS_DURATION = 1.6


def check_rule_based(amount):
    """Hard threshold check for obviously high transaction values."""
    return amount > RULE_THRESHOLD

def show_graph(transactions, alerted_details, threshold_amount):
    """Generate a scatter plot of transactions with alerts highlighted."""
    plt.figure(figsize=(10, 5))
    
    # Plot all transactions as blue dots
    indices = list(range(1, len(transactions) + 1))
    plt.scatter(indices, transactions, color='blue', label='Normal')

    # Highlight suspicious ones in red
    if alerted_details:
        alert_indices = [item[0] for item in alerted_details]
        alert_amounts = [item[1] for item in alerted_details]
        plt.scatter(alert_indices, alert_amounts, color='red', label='Suspicious')

    # Add the Rule Threshold line
    plt.axhline(y=RULE_THRESHOLD, color='orange', linestyle='--', label='Rule Threshold')
    plt.axhline(y=threshold_amount, color='purple', linestyle='--', label='Z-score Threshold')
    plt.title("Transaction Analysis Overview")
    plt.xlabel("Transaction Number")
    plt.ylabel("Amount ($)")
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.show()

def threshold_to_zscore(threshold, overall_median, overall_mad):
    """Convert a robust z-score threshold to the corresponding transaction amount."""
    if overall_mad == 0:
        return overall_median + threshold # If no variability, just add the threshold to the median.
    
    threshold_amount = overall_median + ((threshold * overall_mad) / 0.6745)
    return threshold_amount 
    
def check_zscore(amount, median, mad, threshold):
    """Flag transactions whose z-score exceeds the selected sensitivity."""
    if mad == 0:
        return False, None, None 
    z = (0.6745 * (amount - median)) / mad

    if z > threshold:
        return True, z, f"Z-score={z:.2f} > threshold={threshold:.2f}"

    return False, z, None

def detect_suspicious_transactions(transactions, threshold):
    """Run the detection rules and return alert totals and details."""
    alerts = 0
    alerted_transactions = []
    alerted_details = []

    # Global baseline for z-score checks.
    overall_median = statistics.median(transactions)
    deviations = [abs(x - overall_median) for x in transactions]
    overall_mad = statistics.median(deviations)

    for i, transaction in enumerate(transactions):
        reasons = []

        if check_rule_based(transaction):
            reasons.append(f"Rule: amount ({transaction:.2f}) > {RULE_THRESHOLD:.0f}")

        z_flagged, z_value, z_reason = check_zscore(transaction, overall_median, overall_mad, threshold)
        if z_flagged:
            reasons.append(z_reason)

        if reasons:
            alerts += 1
            txn_number = i + 1 # Transaction numbers are 1-indexed for user-friendly reporting.
            alerted_transactions.append(txn_number)
            alerted_details.append((txn_number, transaction, reasons))

    return alerts, alerted_transactions, alerted_details, overall_median, overall_mad

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
        "(Recommended: 3.5 for strict, 10.0+ for massive spikes)\n"
        "(Enter a number greater than 0) : ",
        float,
        "Please enter a number (e.g. 3.5).",
    )

    transactions = prompt_transactions(n)

    print()
    progress_bar(duration=PROGRESS_DURATION)

    alerts, alerted_transactions, alerted_details, overall_median, overall_mad = detect_suspicious_transactions(transactions, t)
    threshold_amount = threshold_to_zscore(t, overall_median, overall_mad)
    print_results(alerts, alerted_transactions, alerted_details)
    show_graph(transactions, alerted_details, threshold_amount)


if __name__ == "__main__":
    main()