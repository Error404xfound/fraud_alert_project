import pytest
from fraud_alert import (
    check_rule_based, 
    check_zscore,
    detect_suspicious_transactions,
    main,
    print_results,
    show_graph,
    threshold_to_zscore
)

# Test cases for check_rule_based
def test_check_rule_based_below_threshold():
    assert not check_rule_based(999.99)


def test_check_rule_based_at_threshold():
    assert not check_rule_based(1000.00)


def test_check_rule_based_above_threshold():
    assert check_rule_based(1000.01)


def test_check_rule_based_accepts_float_input():
    assert check_rule_based(1500.75)


def test_check_rule_based_accepts_integer_input():
    assert check_rule_based(2000)


# Test cases for threshold_to_zscore
def test_threshold_to_zscore_formula_path():
    threshold_amount = threshold_to_zscore(3, 100, 20)
    expected_amount = 100 + ((3 * 20) / 0.6745)
    assert threshold_amount == pytest.approx(expected_amount)


def test_threshold_to_zscore_zero_mad_path():
    threshold_amount = threshold_to_zscore(3, 100, 0)
    assert threshold_amount == 103


# Test cases for check_zscore
def test_check_zscore_below_threshold():
    flagged, z_value, reason = check_zscore(110, 100, 20, 3)
    assert not flagged
    assert z_value < 3
    assert reason is None


def test_check_zscore_at_threshold_not_flagged():
    amount = 100 + (3 * 20 / 0.6745)
    flagged, z_value, reason = check_zscore(amount, 100, 20, 3)
    assert z_value == pytest.approx(3.0)
    assert not flagged
    assert reason is None


def test_check_zscore_above_threshold_flagged():
    amount = 100 + (3.1 * 20 / 0.6745)
    flagged, z_value, reason = check_zscore(amount, 100, 20, 3)
    assert flagged
    assert z_value > 3
    assert "Z-score=" in reason


def test_check_zscore_zero_mad():
    flagged, z_value, reason = check_zscore(110, 100, 0, 3)
    assert not flagged
    assert z_value is None
    assert reason is None


# Test cases for detect_suspicious_transactions
def test_detect_suspicious_transactions_no_alerts():
    alerts, alerted_transactions, alerted_details, median, mad = detect_suspicious_transactions([100, 150, 200], 3)
    assert alerts == 0
    assert alerted_transactions == []
    assert alerted_details == []
    assert median == 150
    assert mad == 50


def test_detect_suspicious_transactions_rule_only_alert():
    alerts, alerted_transactions, alerted_details, _, _ = detect_suspicious_transactions([100, 150, 2000], 100)
    assert alerts == 1
    assert alerted_transactions == [3]
    reasons = alerted_details[0][2]
    assert any("Rule: amount (2000.00) > 1000" in reason for reason in reasons)
    assert all("Z-score=" not in reason for reason in reasons)


def test_detect_suspicious_transactions_zscore_only_alert():
    alerts, alerted_transactions, alerted_details, _, _ = detect_suspicious_transactions([100, 150, 300], 1)
    assert alerts == 1
    assert alerted_transactions == [3]
    reasons = alerted_details[0][2]
    assert any("Z-score=" in reason for reason in reasons)
    assert all("Rule:" not in reason for reason in reasons)


def test_detect_suspicious_transactions_zero_mad():
    alerts, alerted_transactions, alerted_details, median, mad = detect_suspicious_transactions([100, 100, 100], 1)
    assert alerts == 0
    assert alerted_transactions == []
    assert alerted_details == []
    assert median == 100
    assert mad == 0


def test_detect_suspicious_transactions_returns_1_indexed_transaction_numbers():
    alerts, alerted_transactions, alerted_details, _, _ = detect_suspicious_transactions([100, 150, 2000, 2500], 3)
    assert alerts == 2
    assert alerted_transactions == [3, 4]
    assert alerted_details[0][0] == 3
    assert alerted_details[1][0] == 4


# Test cases for print_results
def test_print_results_no_alerts(capsys):
    print_results(0, [], [])
    captured = capsys.readouterr()
    assert "Total suspicious transactions detected: 0" in captured.out
    assert "No suspicious activity detected. All transactions look normal!" in captured.out


def test_print_results_with_alerts(capsys):
    alerted_transactions = [3, 5]
    alerted_details = [
        (3, 2000.00, ["Rule: amount (2000.00) > 1000", "Z-score=4.00 > threshold=3.00"]),
        (5, 2500.00, ["Rule: amount (2500.00) > 1000"]),
    ]
    print_results(2, alerted_transactions, alerted_details)
    captured = capsys.readouterr()
    assert "Total suspicious transactions detected: 2" in captured.out
    assert "Transaction number(s) flagged: 3, 5" in captured.out
    assert "Transaction 3: 2000.00" in captured.out
    assert "Rule: amount (2000.00) > 1000" in captured.out
    assert "Z-score=4.00 > threshold=3.00" in captured.out
    assert "Transaction 5: 2500.00" in captured.out
    assert "Total flagged spending amount: 4500.00" in captured.out


# Test cases for show_graph
def test_show_graph_without_alert_points(monkeypatch):
    calls = {"figure": 0, "scatter": 0, "axhline": 0, "show": 0}

    def fake_figure(*args, **kwargs):
        calls["figure"] += 1
        assert kwargs == {"figsize": (10, 5)}

    def fake_scatter(*args, **kwargs):
        calls["scatter"] += 1

    def fake_axhline(*args, **kwargs):
        calls["axhline"] += 1

    def fake_show():
        calls["show"] += 1

    monkeypatch.setattr("fraud_alert.plt.figure", fake_figure)
    monkeypatch.setattr("fraud_alert.plt.scatter", fake_scatter)
    monkeypatch.setattr("fraud_alert.plt.axhline", fake_axhline)
    monkeypatch.setattr("fraud_alert.plt.title", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("fraud_alert.plt.xlabel", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("fraud_alert.plt.ylabel", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("fraud_alert.plt.legend", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("fraud_alert.plt.grid", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("fraud_alert.plt.show", fake_show)

    show_graph([100, 150, 200], [], 500)

    assert calls["figure"] == 1
    assert calls["scatter"] == 1
    assert calls["axhline"] == 2
    assert calls["show"] == 1


def test_show_graph_with_alert_points(monkeypatch):
    calls = {"scatter": 0, "show": 0}

    def fake_scatter(*args, **kwargs):
        calls["scatter"] += 1

    def fake_show():
        calls["show"] += 1

    monkeypatch.setattr("fraud_alert.plt.figure", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("fraud_alert.plt.scatter", fake_scatter)
    monkeypatch.setattr("fraud_alert.plt.axhline", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("fraud_alert.plt.title", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("fraud_alert.plt.xlabel", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("fraud_alert.plt.ylabel", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("fraud_alert.plt.legend", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("fraud_alert.plt.grid", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("fraud_alert.plt.show", fake_show)

    alerted_details = [
        (3, 2000.00, ["Rule: amount (2000.00) > 1000"]),
        (4, 2500.00, ["Rule: amount (2500.00) > 1000"]),
    ]
    show_graph([100, 150, 2000, 2500], alerted_details, 1200)

    assert calls["scatter"] == 2
    assert calls["show"] == 1


# Test cases for main
def test_main_orchestrates_dependencies(monkeypatch, capsys):
    calls = {
        "prompt_positive_value": [],
        "prompt_transactions": [],
        "progress_bar": 0,
        "detect": [],
        "threshold": [],
        "print_results": [],
        "show_graph": [],
    }

    values = iter([5, 3.5])

    def fake_prompt_positive_value(prompt, cast_type, invalid_type_message):
        calls["prompt_positive_value"].append((prompt, cast_type, invalid_type_message))
        return next(values)

    def fake_prompt_transactions(n):
        calls["prompt_transactions"].append(n)
        return [100, 150, 2000, 150, 100]

    def fake_progress_bar(duration=3.0, steps=50):
        calls["progress_bar"] += 1

    def fake_detect(transactions, threshold):
        calls["detect"].append((transactions, threshold))
        return 1, [3], [(3, 2000.0, ["Rule: amount (2000.00) > 1000"])], 150, 50

    def fake_threshold_to_zscore(threshold, median, mad):
        calls["threshold"].append((threshold, median, mad))
        return 1172.35

    def fake_print_results(alerts, alerted_transactions, alerted_details):
        calls["print_results"].append((alerts, alerted_transactions, alerted_details))

    def fake_show_graph(transactions, alerted_details, threshold_amount):
        calls["show_graph"].append((transactions, alerted_details, threshold_amount))

    monkeypatch.setattr("fraud_alert.prompt_positive_value", fake_prompt_positive_value)
    monkeypatch.setattr("fraud_alert.prompt_transactions", fake_prompt_transactions)
    monkeypatch.setattr("fraud_alert.progress_bar", fake_progress_bar)
    monkeypatch.setattr("fraud_alert.detect_suspicious_transactions", fake_detect)
    monkeypatch.setattr("fraud_alert.threshold_to_zscore", fake_threshold_to_zscore)
    monkeypatch.setattr("fraud_alert.print_results", fake_print_results)
    monkeypatch.setattr("fraud_alert.show_graph", fake_show_graph)

    main()
    captured = capsys.readouterr()

    assert "Welcome to the Transaction Checker" in captured.out
    assert len(calls["prompt_positive_value"]) == 2
    assert calls["prompt_transactions"] == [5]
    assert calls["progress_bar"] == 1
    assert calls["detect"] == [([100, 150, 2000, 150, 100], 3.5)]
    assert calls["threshold"] == [(3.5, 150, 50)]
    assert calls["print_results"] == [(1, [3], [(3, 2000.0, ["Rule: amount (2000.00) > 1000"])])]
    assert calls["show_graph"] == [([100, 150, 2000, 150, 100], [(3, 2000.0, ["Rule: amount (2000.00) > 1000"])], 1172.35)]



