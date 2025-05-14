import unittest
from datetime import date
from payslip2budget.models.ynab_transaction import YNABTransaction

class TestYNABTransaction(unittest.TestCase):
    def test_to_api_dict(self):
        txn = YNABTransaction(
            date="2025-05-10",
            payee="Acme Corp",
            memo="Salary",
            amount=1234560,
            account_id="abc123"
        )

        api_dict = txn.to_api_dict()
        self.assertEqual(api_dict["date"], "2025-05-10")
        self.assertEqual(api_dict["amount"], 1234560)
        self.assertEqual(api_dict["payee_name"], "Acme Corp")
        self.assertEqual(api_dict["memo"], "Salary")
        self.assertEqual(api_dict["account_id"], "abc123")
        self.assertEqual(api_dict["cleared"], "cleared")
        self.assertFalse(api_dict["approved"])
