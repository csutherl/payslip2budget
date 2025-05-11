import unittest
from unittest.mock import patch, MagicMock
from exporters.apihandlers.ynab import YNABAPIHandler
from models.ynab_transaction import YNABTransaction

class TestYNABAPIHandler(unittest.TestCase):

    def setUp(self):
        self.config = {
            "api_key": "fake_token",
            "budget_id": "fake_budget_id",
            "account_id": "fake_account_id"
        }
        self.handler = YNABAPIHandler(self.config)
        
        self.transactions = [
            YNABTransaction(date="2025-05-10", payee="Employer", memo="Salary", amount=123456, account_id="test_account")
        ]

    def test_init_sets_config_values(self):
        self.assertEqual(self.handler.api_key, "fake_token")
        self.assertEqual(self.handler.budget_id, "fake_budget_id")
        self.assertEqual(self.handler.account_id, "fake_account_id")

    def test_validate_config_raises_on_missing_fields(self):
        incomplete = {"api_key": "only_token"}
        with self.assertRaises(ValueError) as cm:
            YNABAPIHandler(incomplete)
        self.assertIn("Missing required YNAB configuration parameters.", str(cm.exception))

    @patch("exporters.apihandlers.ynab.requests.post")
    def test_send_transactions_posts_expected_payload(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"data": {"transaction_ids": ["123"]}}
        mock_post.return_value = mock_response

        result = self.handler.send_transactions(self.transactions)

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("Authorization", kwargs["headers"])
        self.assertIn("transactions", kwargs["json"])
        self.assertEqual(kwargs["json"]["transactions"][0]["amount"], 123456)
        self.assertEqual(result, {"data": {"transaction_ids": ["123"]}})

    @patch("exporters.apihandlers.ynab.requests.post")
    def test_send_transactions_raises_on_http_error(self, mock_post):
        mock_post.return_value.status_code = 401
        mock_post.return_value.text = "Unauthorized"

        with self.assertRaises(Exception) as cm:
            self.handler.send_transactions(self.transactions)

        self.assertIn("YNAB API call failed", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
