
from formatters import ynab

def test_ynab_formatter_output():
    transactions = [
        {"date": "2025-05-01", "payee": "Employer", "category": "Taxes", "memo": "Federal Tax", "amount": -200},
        {"date": "2025-05-01", "payee": "Employer", "category": "Offset", "memo": "Net Pay Adjustment", "amount": 200}
    ]
    output = ynab.format(transactions)
    assert output.startswith("Date,Payee,Category")
    assert "Taxes" in output
