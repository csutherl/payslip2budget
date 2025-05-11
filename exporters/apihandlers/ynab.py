import requests

class YNABAPIHandler(APIHandlerBase):
    def send_transactions(self, transactions):
        token = self.config.get("token")
        budget_id = self.config.get("budget_id")
        account_id = self.config.get("account_id")

        if not all([token, budget_id, account_id]):
            raise ValueError("Missing YNAB configuration parameters.")

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        ynab_transactions = []
        for txn in transactions:
            amount = -int(float(txn["Outflow"]) * 1000) if txn["Outflow"] else int(float(txn["Inflow"]) * 1000)
            ynab_txn = {
                "account_id": account_id,
                "date": txn["Date"],
                "amount": amount,
                "payee_name": txn["Payee"],
                "memo": txn["Memo"],
                "cleared": "cleared"
            }
            ynab_transactions.append(ynab_txn)

        data = {"transactions": ynab_transactions}
        response = requests.post(
            f"https://api.youneedabudget.com/v1/budgets/{budget_id}/transactions",
            headers=headers,
            json=data
        )

        if response.status_code == 201:
            print("Transactions successfully imported to YNAB.")
        else:
            print(f"Failed to import transactions to YNAB: {response.status_code} - {response.text}")
