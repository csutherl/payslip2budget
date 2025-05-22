import unittest
from unittest.mock import patch, MagicMock
import json

# Assuming APIHandlerBase and GoogleSheetsAPIHandler are in these locations
from payslip2budget.exporters.apihandlers.apihandlerbase import APIHandlerBase
from payslip2budget.exporters.apihandlers.google_sheets import GoogleSheetsAPIHandler

# Example transaction data (adjust structure if your actual Transaction type is different)
MOCK_TRANSACTIONS = [
    {"Date": "2024-07-01", "Payee": "Employer", "Category": "Income", "Inflow": 1000.0, "Outflow": None, "Memo": "Salary"},
    {"Date": "2024-07-01", "Payee": "Coffee Shop", "Category": "Food", "Inflow": None, "Outflow": 5.0, "Memo": "Latte"},
    {"Date": "2024-07-02", "Payee": "Groceries", "Category": "Food", "Amount": -75.0, "Memo": "Weekly shop"}, # Using Amount directly
]

MOCK_CONFIG_VALID = {
    "type": "google_sheets",
    "spreadsheet_id": "test_spreadsheet_id",
    "worksheet_name": "TestSheet",
    "credentials_json_path": "dummy_credentials.json" 
}

MOCK_CONFIG_MISSING_SPREADSHEET_ID = {
    "type": "google_sheets",
    "worksheet_name": "TestSheet",
    "credentials_json_path": "dummy_credentials.json"
}

class TestGoogleSheetsAPIHandler(unittest.TestCase):

    @patch('payslip2budget.exporters.apihandlers.google_sheets.get_sheets_service')
    def test_init_success(self, mock_get_sheets_service):
        mock_service = MagicMock()
        mock_get_sheets_service.return_value = mock_service
        
        handler = GoogleSheetsAPIHandler(MOCK_CONFIG_VALID, dry_run=False)
        
        self.assertEqual(handler.spreadsheet_id, "test_spreadsheet_id")
        self.assertEqual(handler.worksheet_name, "TestSheet")
        self.assertEqual(handler.credentials_path, "dummy_credentials.json")
        self.assertEqual(handler.service, mock_service)
        mock_get_sheets_service.assert_called_once_with("dummy_credentials.json")

    def test_init_missing_spreadsheet_id(self):
        with self.assertRaises(ValueError) as context:
            GoogleSheetsAPIHandler(MOCK_CONFIG_MISSING_SPREADSHEET_ID, dry_run=False)
        self.assertTrue("Missing required Google Sheets configuration: 'spreadsheet_id'" in str(context.exception))

    @patch('payslip2budget.exporters.apihandlers.google_sheets.get_sheets_service')
    def test_send_transactions_dry_run(self, mock_get_sheets_service, mock_stdout=None): # mock_stdout for later if needed
        mock_service = MagicMock()
        mock_get_sheets_service.return_value = mock_service
        
        handler = GoogleSheetsAPIHandler(MOCK_CONFIG_VALID, dry_run=True)
        
        # Capture print output
        with patch('builtins.print') as mocked_print:
            handler.send_transactions(MOCK_TRANSACTIONS)

        # Check if dry run message is printed
        self.assertTrue(any("[DRY RUN]" in call.args[0] for call in mocked_print.call_args_list))
        # Check if spreadsheet ID and worksheet name are mentioned
        self.assertTrue(any(MOCK_CONFIG_VALID["spreadsheet_id"] in call.args[0] for call in mocked_print.call_args_list))
        self.assertTrue(any(MOCK_CONFIG_VALID["worksheet_name"] in call.args[0] for call in mocked_print.call_args_list))

        # Check if data rows are printed (simplified check)
        # Expected header + data rows
        expected_rows_in_dry_run = [
            ["Date", "Payee", "Category", "Amount", "Memo"],
            ["2024-07-01", "Employer", "Income", 1000.0, "Salary"],
            ["2024-07-01", "Coffee Shop", "Food", -5.0, "Latte"],
            ["2024-07-02", "Groceries", "Food", -75.0, "Weekly shop"],
        ]
        
        printed_rows_str = []
        for call_args in mocked_print.call_args_list:
            # Assuming each row is printed in its own print call and looks like a list
            if isinstance(call_args.args[0], list):
                 printed_rows_str.append(call_args.args[0])
        
        self.assertEqual(printed_rows_str, expected_rows_in_dry_run)
        
        # Ensure the API was NOT called
        mock_service.spreadsheets.assert_not_called()


    @patch('payslip2budget.exporters.apihandlers.google_sheets.get_sheets_service')
    def test_send_transactions_success(self, mock_get_sheets_service):
        mock_service_instance = MagicMock()
        mock_spreadsheets_values = MagicMock()
        mock_append_result = MagicMock()
        
        # Setup the mock service chain
        mock_get_sheets_service.return_value = mock_service_instance
        mock_service_instance.spreadsheets.return_value.values.return_value.append.return_value = mock_append_result
        mock_append_result.execute.return_value = {"updates": {"updatedCells": 15}} # Example response

        handler = GoogleSheetsAPIHandler(MOCK_CONFIG_VALID, dry_run=False)
        
        with patch('builtins.print') as mocked_print: # To check success message
            handler.send_transactions(MOCK_TRANSACTIONS)

        expected_header = ["Date", "Payee", "Category", "Amount", "Memo"]
        expected_rows_to_send = [
            expected_header,
            ["2024-07-01", "Employer", "Income", 1000.0, "Salary"],
            ["2024-07-01", "Coffee Shop", "Food", -5.0, "Latte"],
            ["2024-07-02", "Groceries", "Food", -75.0, "Weekly shop"],
        ]

        # Verify the append call
        mock_service_instance.spreadsheets().values().append.assert_called_once_with(
            spreadsheetId=MOCK_CONFIG_VALID["spreadsheet_id"],
            range=f"{MOCK_CONFIG_VALID['worksheet_name']}!A1",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": expected_rows_to_send}
        )
        mock_append_result.execute.assert_called_once()
        
        # Check for success print message
        self.assertTrue(any(f"Successfully wrote {len(MOCK_TRANSACTIONS)} transactions" in call.args[0] for call in mocked_print.call_args_list))


    @patch('payslip2budget.exporters.apihandlers.google_sheets.get_sheets_service')
    def test_send_transactions_api_error(self, mock_get_sheets_service):
        mock_service_instance = MagicMock()
        mock_get_sheets_service.return_value = mock_service_instance
        # Simulate an API error
        mock_service_instance.spreadsheets.return_value.values.return_value.append.return_value.execute.side_effect = Exception("API Error")

        handler = GoogleSheetsAPIHandler(MOCK_CONFIG_VALID, dry_run=False)

        with patch('builtins.print') as mocked_print:
            handler.send_transactions(MOCK_TRANSACTIONS)
        
        self.assertTrue(any("An error occurred while sending data to Google Sheets: API Error" in call.args[0] for call in mocked_print.call_args_list))

    @patch('payslip2budget.exporters.apihandlers.google_sheets.get_sheets_service')
    def test_send_transactions_no_service(self, mock_get_sheets_service):
        mock_get_sheets_service.return_value = None # Simulate service init failure

        handler = GoogleSheetsAPIHandler(MOCK_CONFIG_VALID, dry_run=False)
        
        with patch('builtins.print') as mocked_print:
            handler.send_transactions(MOCK_TRANSACTIONS)
        
        self.assertTrue(any("Google Sheets API service not available" in call.args[0] for call in mocked_print.call_args_list))


if __name__ == "__main__":
    unittest.main()
