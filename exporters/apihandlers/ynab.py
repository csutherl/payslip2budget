import requests
from models.transaction_base import Transaction
from models.ynab_transaction import YNABTransaction
from exporters.apihandlers.apihandlerbase import APIHandlerBase

class YNABAPIHandler(APIHandlerBase):
    def __init__(self, config):
        super().__init__(config)
        self.api_key = self.config.get("api_key")
        self.budget_id = self.config.get("budget_id")
        self.account_id = self.config.get("account_id")
        self.base_url = "https://api.youneedabudget.com/v1"

        if not all([self.api_key, self.budget_id, self.account_id]):
            raise ValueError("Missing required YNAB configuration parameters.")

    def send_transactions(self, transactions: list[Transaction]):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        # TODO: Confirm that we can make a successful API call using configured credentials
        # hit /budgets/{budget_id} to confirm it exists, also check account_id
        # TODO: Make a request for all categories and cache locally
#        ynab_transactions = []
#        for txn in transactions:
#            # TODO: Check that the Category from the transaction is real, throw an error if not because I think ynab ignores it
#            # Grab Category ID and insert into the transaction data before sending
#            ynab_txn = {
#                "account_id": account_id,
#                "date": txn["Date"],
#                "amount": txn["Amount"],
#                "payee_name": txn["Payee"],
#                "memo": txn["Memo"],
#                "cleared": "cleared"
#            }
#            ynab_transactions.append(ynab_txn)

        ynab_transactions = [
            YNABTransaction(
                date=txn.date,
                payee=txn.payee,
                memo=txn.memo,
                amount=txn.amount,
                account_id=self.account_id,
            ).to_api_dict()
            for txn in transactions
        ]

        payload = {"transactions": ynab_transactions}
        response = requests.post(
            f"{self.base_url}/budgets/{self.budget_id}/transactions",
            headers=headers,
            json=payload
        )

        if response.status_code == 201:
            print("Transactions successfully imported to YNAB.")
            return response.json()
        else:
            #print(f"Failed to import transactions to YNAB: {response.status_code} - {response.text}")
            error_msg = (
                f"YNAB API call failed: {response.status_code} - {response.reason}\n"
                f"Response body: {response.text}"
            )
            raise RuntimeError(error_msg)
