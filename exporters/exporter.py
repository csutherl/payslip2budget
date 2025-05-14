import json
import os
from exporters.apihandlers.ynab import YNABAPIHandler

class TransactionExporter:
    def __init__(self, config_path=None, dry_run: bool = False):
        self.config = {}
        self.dry_run = dry_run
        self.api_handler = None

        if config_path:
            self.load_config(config_path)

    def load_config(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, 'r') as f:
            self.config = json.load(f)

        api_config = self.config.get("api", {})
        api_type = api_config.get("type")

        if api_type == "ynab":
            self.api_handler = YNABAPIHandler(api_config, self.dry_run)
        else:
            raise ValueError(f"Unsupported API type: {api_type}")

    def export(self, transactions, destination='stdout'):
        if destination == 'stdout':
            self._export_to_stdout(transactions)
        elif destination.endswith('.csv'):
            self._export_to_csv(transactions, destination)
        elif destination == 'api':
            if not self.api_handler:
                raise ValueError("API handler not configured.")
            self.api_handler.send_transactions(transactions)
        else:
            raise ValueError(f"Unsupported export destination: {destination}")

    def _export_to_stdout(self, transactions):
        for txn in transactions:
            print(json.dumps(txn, indent=2))

    def _export_to_csv(self, transactions, filepath):
        import csv

        fieldnames = ["Date", "Payee", "Category", "Memo", "Outflow", "Inflow"]
        try:
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(transactions)
            print(f"Transactions saved to {filepath}")
        except IOError as e:
            print(f"Error saving CSV: {e}")
