import requests
from payslip2budget.models.transaction_base import Transaction
from payslip2budget.models.ynab_transaction import YNABTransaction
from payslip2budget.exporters.apihandlers.apihandlerbase import APIHandlerBase

# This class is still a WIP and incomplete!
class YNABAPIHandler(APIHandlerBase):
    def __init__(self, config, dry_run: bool = False):
        super().__init__(config, dry_run)
        self.api_key = self.config.get("api_key")
        self.budget_id = self.config.get("budget_id")
        self.account_id = self.config.get("account_id")
        self.base_url = "https://api.youneedabudget.com/v1"

        if self.api_key is not None:
            self.headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

        self.cached_categories = {}
        self.cached_payees = {}

        if not all([self.api_key, self.budget_id, self.account_id]):
            raise ValueError("Missing required YNAB configuration parameters.")

    def send_transactions(self, transactions: list[Transaction]):
        """
        Send the list of transactions to API, but first fetch categories and and find
        the ID for categories for each transaction, then check account ID for validity.
        """
        # Cache categories
        self.fetch_and_cache_categories()
        # Create a list of categories used in transactions
        category_ids = self.extract_category_ids(transactions)

        # Confirm the account is valid
        self.confirm_account_id_validity()

        # Cache payees
        self.fetch_and_cache_payees()

        ynab_transactions = []
        for txn in transactions:
            category_tuple = self.get_category_tuple(txn["category"])
            payee_id = self.get_cached_payee_id(txn["payee"])

            ynab_txn = YNABTransaction(
                date=txn["date"],
                payee=txn["payee"],
                payee_id=payee_id,
                memo=txn["memo"],
                amount=txn["amount"],
                account_id=self.account_id,
                category_id=category_ids[category_tuple[1]],
                category_name=category_tuple[1],
            ).to_api_dict()

            ynab_transactions.append(ynab_txn)

        payload = {"transactions": ynab_transactions}

        # THe dryrun still does all the GETs, but returns before the POST so no changes are made
        if self.dry_run:
            print("[DRY RUN] Would send the following transactions:")
            print(json.dumps(transactions, indent=2))
            return

        response = requests.post(
            f"{self.base_url}/budgets/{self.budget_id}/transactions",
            headers=self.headers,
            json=payload
        )

        if response.status_code == 201:
            print("Transactions successfully imported to YNAB.")
            return response.json()
        else:
            error_msg = (
                f"YNAB API call failed: {response.status_code} - {response.reason}\n"
                f"Response body: {response.text}"
            )
            raise RuntimeError(error_msg)

    def fetch_and_cache_categories(self):
        """
        Fetch categories list from API endpoint and create a dict with the category groups,
        subcategories, and their IDs so that we can use them later.

        This method also confirms that the budget_id is valid (by making a request).
        """

        response = requests.get(
            f"{self.base_url}/budgets/{self.budget_id}/categories",
            headers=self.headers
        )

        if response.status_code != 200:
            raise RuntimeError(f"YNAB API call failed: {response.status_code} - {response.text}")

        data = response.json()["data"]["category_groups"]
        self.cached_categories = {}

        for category_group in data:
            group_name = category_group["name"]
            self.cached_categories[group_name] = {}

            for category in category_group["categories"]:
                category_name = category["name"]
                self.cached_categories[group_name][category_name] = category["id"]

    def extract_category_ids(self, transactions: list[Transaction]):
        """
        Grab the categories for each transaction and find their IDs, then return
        a list of categories and their IDs.
        """
        category_ids = {}

        for txn in transactions:
            if txn["Category"] is None:
                continue

            category_group, category_name = self.get_category_tuple(txn["Category"])

            print(type(self.cached_categories), self.cached_categories)
            print(category_group)
            print(category_name)
            # TODO When the category group doesn't exist, this fails
            category =  self.cached_categories.get(category_group).get(category_name)
            if category:
                category_ids[category_name] = category

        return category_ids

    def get_category_tuple(self, category_string):
        """
        Method to take a category listing, like Insurance:Medical and break it apart
        to return the category name of the subcategory.
        """
        category_parts = category_string.split(":")
        category_group = category_parts[0].strip()
        category_name = category_parts[1].strip() if len(category_parts) > 1 else category_group

        return (category_group, category_name)

    def confirm_account_id_validity(self):
        response = requests.get(
            f"{self.base_url}/budgets/{self.budget_id}/accounts/{self.account_id}",
            headers=self.headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            error_msg = (
                f"YNAB API call failed: {response.status_code} - {response.reason}\n"
                f"Response body: {response.text}"
            )
            raise RuntimeError(error_msg)

    def fetch_and_cache_payees(self):
        response = requests.get(
            f"{self.base_url}/budgets/{self.budget_id}/payees",
            headers=self.headers
        )

        if response.status_code != 200:
            raise RuntimeError(f"YNAB API failed: {response.status_code} - {response.text}")

        data = response.json()["data"]["payees"]
        self.cached_payees = {
            payee["name"].strip().lower(): payee["id"] for payee in data
        }

    def get_cached_payee_id(self, payee_name: str) -> str | None:
        if not self.cached_payees:
            return None

        normalized_name = payee_name.strip().lower()

        return self.cached_payees.get(normalized_name)
