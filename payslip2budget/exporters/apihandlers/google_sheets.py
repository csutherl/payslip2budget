import json
from payslip2budget.exporters.apihandlers.apihandlerbase import APIHandlerBase
from payslip2budget.exporters.apihandlers.google_sheets_auth import get_sheets_service
from googleapiclient.errors import HttpError # Added import
# Assuming Transaction is a TypedDict or similar, import if necessary
# from payslip2budget.models.transaction_base import Transaction # Adjust import as per actual Transaction type

class GoogleSheetsAPIHandler(APIHandlerBase):
    def __init__(self, config, dry_run: bool = False):
        super().__init__(config, dry_run)
        self.spreadsheet_id = self.config.get("spreadsheet_id")
        self.worksheet_name = self.config.get("worksheet_name", "Transactions") # Default worksheet name
        self.write_mode = self.config.get("write_mode", "append").lower()
        
        if not self.spreadsheet_id:
            raise ValueError("Missing required Google Sheets configuration: 'spreadsheet_id'")

        # Path to credentials.json can be made configurable if needed
        # For now, assume it's in the default location expected by google_sheets_auth.py
        # or that google_sheets_auth.py is configured to find it.
        # If `credentials_json_path` is in config, it can be passed to get_sheets_service
        self.credentials_path = self.config.get("credentials_json_path", "credentials.json")
        self.service = get_sheets_service(self.credentials_path)

    def send_transactions(self, transactions: list[dict]): # Replace dict with actual Transaction type if available
        """
        Sends the list of transactions to the configured Google Sheet.
        """
        if not self.service:
            print("Google Sheets API service not available. Cannot send transactions.")
            return

        # Check if worksheet exists and create if not
        try:
            spreadsheet_info = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
            sheet_exists = any(sheet['properties']['title'] == self.worksheet_name for sheet in spreadsheet_info.get('sheets', []))

            if not sheet_exists:
                if self.dry_run:
                    print(f"[DRY RUN] Worksheet '{self.worksheet_name}' does not exist. Would attempt to create it.")
                else:
                    print(f"Worksheet '{self.worksheet_name}' does not exist. Attempting to create it...")
                    add_sheet_request_body = {
                        'requests': [{
                            'addSheet': {
                                'properties': {
                                    'title': self.worksheet_name
                                }
                            }
                        }]
                    }
                    self.service.spreadsheets().batchUpdate(
                        spreadsheetId=self.spreadsheet_id,
                        body=add_sheet_request_body
                    ).execute()
                    print(f"Worksheet '{self.worksheet_name}' created successfully.")
            
        except HttpError as e:
            print(f"An API error occurred while checking/creating worksheet '{self.worksheet_name}': {e}")
            # If we can't ensure sheet exists, maybe we should not proceed further.
            # Or, the append operation later will fail and be caught by the existing try-except.
            # For now, let's print the error and let it try to append. The user will see the append error.
            # A more robust solution might be to re-raise or return if sheet creation fails when it's needed.
            pass # Or handle more gracefully

        header = ["Date", "Payee", "Category", "Amount", "Memo"]
        rows_to_send = [header]

        for txn in transactions:
            # Ensure the order of values matches the header
            # Amount might need specific formatting (e.g., as a number, not string)
            # For now, assuming direct mapping from transaction dict keys
            amount = txn.get("Amount") # Or txn["Amount"] if always present
            # YNAB exporter converts amount to milliunits and expects specific keys.
            # Here, we assume 'Amount' is the key from the parser.
            # The original Transaction model might have 'Inflow'/'Outflow' or just 'Amount'.
            # For simplicity, let's assume 'Amount' is a float/decimal.
            # If 'Outflow' in txn and txn['Outflow'] is not None:
            if 'Outflow' in txn and txn['Outflow'] is not None:
                amount = float(txn['Outflow']) * -1
            elif 'Inflow' in txn and txn['Inflow'] is not None:
                amount = float(txn['Inflow'])
            else:
                # Fallback if neither Inflow/Outflow, or if Amount is directly there
                amount = float(txn.get("Amount", 0.0))


            rows_to_send.append([
                txn.get("Date", ""),
                txn.get("Payee", ""),
                txn.get("Category", ""),
                amount,
                txn.get("Memo", "")
            ])

        if self.dry_run:
            print("[DRY RUN] Would send the following data to Google Sheet:")
            print(f"Spreadsheet ID: {self.spreadsheet_id}")
            print(f"Worksheet Name: {self.worksheet_name}")
            for row in rows_to_send:
                print(row)
            # Simulate successful dry run message
            print(f"Successfully wrote {len(rows_to_send) -1} transactions to Google Sheet '{self.worksheet_name}' (dry run).")
            return

        body = {
            "values": rows_to_send
        }
        try:
            if self.write_mode == "overwrite":
                if self.dry_run:
                    print(f"[DRY RUN] Would clear worksheet '{self.worksheet_name}' before writing new data.")
                else:
                    print(f"Clearing worksheet '{self.worksheet_name}' (overwrite mode)...")
                    self.service.spreadsheets().values().clear(
                        spreadsheetId=self.spreadsheet_id,
                        range=self.worksheet_name # Clears the entire sheet
                    ).execute()
                    print(f"Worksheet '{self.worksheet_name}' cleared.")

                # For overwrite, we write all rows (including header) starting at A1
                if self.dry_run:
                    print(f"[DRY RUN] Would write {len(rows_to_send)} rows (including header) to '{self.worksheet_name}'.")
                else:
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.spreadsheet_id,
                        range=f"{self.worksheet_name}!A1",
                        valueInputOption="USER_ENTERED",
                        body=body
                    ).execute()
            else: # append mode (default)
                if self.dry_run:
                     print(f"[DRY RUN] Would append {len(rows_to_send)} rows (including header if sheet is empty) to '{self.worksheet_name}'.")
                else:
                    # Check if sheet is empty to decide whether to include header
                    # This is a simplified check; a more robust way might be to get the sheet's content
                    # or rely on the `append` behavior with `INSERT_ROWS`.
                    # For now, if it's append, and we are sending rows, it implies a header might be needed
                    # if the sheet was just created or is empty.
                    # The `append` operation with `INSERT_ROWS` should handle this correctly.
                    # If the sheet is truly empty, it appends at A1. If it has content, it appends after.
                    # Header is included in rows_to_send, so it will be written if sheet is empty.
                    # If sheet is not empty, and header is first in rows_to_send, it will write it again.
                    # This needs refinement: only write header if sheet is empty OR if header is not present.
                    # For now, the provided code *always* includes header in rows_to_send.
                    # A better approach for "append" would be to send only data rows if header exists.
                    # However, to keep change minimal to current structure:
                    
                    # If appending, we might not want to re-add header if it's already there.
                    # The current code always includes header in rows_to_send.
                    # For true append, we should only send data rows if header already exists.
                    # This simplified version will append all rows_to_send.
                    self.service.spreadsheets().values().append(
                        spreadsheetId=self.spreadsheet_id,
                        range=f"{self.worksheet_name}!A1", 
                        valueInputOption="USER_ENTERED",
                        insertDataOption="INSERT_ROWS", # Inserts new rows for the data
                        body=body
                    ).execute()
            
            num_rows_written = len(rows_to_send) -1 # Excluding header
            # The success message needs to be more accurate based on operation
            if self.write_mode == "overwrite":
                 print(f"Successfully overwrote worksheet '{self.worksheet_name}' with {num_rows_written} transactions.")
            else:
                 print(f"Successfully appended {num_rows_written} transactions to Google Sheet '{self.worksheet_name}'.")
            # The result object structure might differ between update and append
            # For simplicity, generic success is printed. Specific cell count might not be relevant for clear+update.

        except HttpError as e: # Changed to HttpError for more specific catch
            print(f"An API error occurred while sending data to Google Sheets: {e}")
            if e.resp.status == 401:
               print("Authentication error. Token might be expired or revoked. Try deleting token.json and re-authenticating.")
            # Handle other specific errors like 404 for spreadsheet not found, 400 for bad request etc.
        except Exception as e: # Catch any other unexpected errors
            print(f"An unexpected error occurred: {e}")
