import unittest
from unittest.mock import patch, MagicMock
from payslip2budget.exporters.apihandlers.ynab import YNABAPIHandler
from payslip2budget.models.ynab_transaction import YNABTransaction
from tests.utils.fixtures import load_json_fixture

class TestYNABAPIHandler(unittest.TestCase):

    def setUp(self):
        self.config = {
            "api_key": "fake_token",
            "budget_id": "fake_budget_id",
            "account_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        }
        self.handler = YNABAPIHandler(self.config)
        
        self.transactions = [{"Date": "2025-05-10", "Payee": "Employer", "Category": "Insurance:Medical", "Memo": "Salary", "Amount": 123456}]
        self.payee_dne_transactions = [{"Date": "2025-05-10", "Payee": "Employer 2", "Category": "Insurance:Medical", "Memo": "Salary", "Amount": 123456}]
        self.category_dne_transactions = [{"Date": "2025-05-10", "Payee": "Employer", "Category": "Taxes", "Memo": "Salary", "Amount": 123456}]

        self.test_categories_response_data = load_json_fixture("test_categories_response_data.json")
        self.test_account_response_data = load_json_fixture("test_account_response_data.json")
        self.test_payees_response_data = load_json_fixture("test_payees_response_data.json")

        self.transaction_categories_list = {
            "Insurance": {
                "Medical": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
            }
        }

    def test_init_sets_config_values(self):
        self.assertEqual(self.handler.api_key, "fake_token")
        self.assertEqual(self.handler.budget_id, "fake_budget_id")
        self.assertEqual(self.handler.account_id, "3fa85f64-5717-4562-b3fc-2c963f66afa6")

    def test_validate_config_raises_on_missing_fields(self):
        incomplete = {"api_key": "only_token"}
        with self.assertRaises(ValueError) as cm:
            YNABAPIHandler(incomplete)
        self.assertIn("Missing required YNAB configuration parameters.", str(cm.exception))

    def mock_requests_get(url, *args, **kwargs):
        mock_response = MagicMock()
        mock_response.status_code = 200
        if "categories" in url:
            mock_response.json.return_value = load_json_fixture("test_categories_response_data.json")
        elif "accounts" in url:
            mock_response.json.return_value = load_json_fixture("test_account_response_data.json")
        elif "payees" in url:
            mock_response.json.return_value = load_json_fixture("test_payees_response_data.json")
        else:
            mock_response.status_code = 404
            mock_response.text = "Not Found"

        return mock_response

    @patch("payslip2budget.exporters.apihandlers.ynab.requests.post")
    @patch("payslip2budget.exporters.apihandlers.ynab.requests.get", side_effect=mock_requests_get)
    def test_send_transactions_posts_expected_payload(self, mock_get, mock_post):
        mock_post_response = MagicMock()
        mock_post_response.status_code = 201
        mock_post_response.json.return_value = {"data": {"transaction_ids": ["123"]}}
        mock_post.return_value = mock_post_response

        result = self.handler.send_transactions(self.transactions)

        assert mock_get.call_count == 3

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("Authorization", kwargs["headers"])
        self.assertIn("transactions", kwargs["json"])
        self.assertEqual(kwargs["json"]["transactions"][0]["amount"], 123456)
        self.assertEqual(result, {"data": {"transaction_ids": ["123"]}})

    @patch("payslip2budget.exporters.apihandlers.ynab.requests.post")
    @patch("payslip2budget.exporters.apihandlers.ynab.requests.get", side_effect=mock_requests_get)
    def test_send_transactions_posts_payee_dne_payload(self, mock_get, mock_post):
        mock_post_response = MagicMock()
        mock_post_response.status_code = 201
        mock_post_response.json.return_value = {"data": {"transaction_ids": ["123"]}}
        mock_post.return_value = mock_post_response

        result = self.handler.send_transactions(self.payee_dne_transactions)

        assert mock_get.call_count == 3

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("Authorization", kwargs["headers"])
        self.assertIn("transactions", kwargs["json"])
        self.assertEqual(kwargs["json"]["transactions"][0]["amount"], 123456)
        self.assertEqual(result, {"data": {"transaction_ids": ["123"]}})

    @patch("payslip2budget.exporters.apihandlers.ynab.requests.post")
    def test_send_transactions_raises_on_http_error(self, mock_post):
        mock_post.return_value.status_code = 401
        mock_post.return_value.text = "Unauthorized"

        with self.assertRaises(Exception) as cm:
            self.handler.send_transactions(self.transactions)

        self.assertIn("YNAB API call failed", str(cm.exception))

    @patch("payslip2budget.exporters.apihandlers.ynab.requests.get")
    def test_get_categories_request(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.test_categories_response_data
        mock_get.return_value = mock_response

        self.handler.fetch_and_cache_categories()

        # Validate the internal cache
        assert self.handler.cached_categories == self.transaction_categories_list

        # Confirm the API call was made correctly
        mock_get.assert_called_once()

    @patch("payslip2budget.exporters.apihandlers.ynab.requests.get")
    def test_confirm_account_id_validity(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.test_account_response_data
        mock_get.return_value = mock_response

        result = self.handler.confirm_account_id_validity()

        # Validate the internal cache
        assert result == self.test_account_response_data

        # Confirm the API call was made correctly
        mock_get.assert_called_once()

    def test_get_cached_payee_id_case_insensitive(self):
        self.handler.cached_payees = {"test": "payee123"}

        assert self.handler.get_cached_payee_id("Test") == "payee123"
        assert self.handler.get_cached_payee_id("Unknown") is None

if __name__ == '__main__':
    unittest.main()
