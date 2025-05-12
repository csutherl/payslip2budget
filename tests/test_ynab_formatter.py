
from formatters import ynab

def test_ynab_formatter_output():
    transactions = [
        {"Date": "2025-05-01", "Payee": "Employer", "Category": "Taxes", "Memo": "Federal Tax", "Amount": -200},
        {"Date": "2025-05-01", "Payee": "Employer", "Category": "Offset", "Memo": "Net Pay Adjustment", "Amount": 200}
    ]
    output = ynab.format(transactions)
    assert output.startswith("Date,Payee,Category")
    assert "Taxes" in output
