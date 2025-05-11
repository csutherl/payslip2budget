
from parsers import adp

def test_adp_parser_output():
    transactions = adp.parse("sample.pdf")
    assert isinstance(transactions, list)
    assert all(isinstance(tx, dict) for tx in transactions)
