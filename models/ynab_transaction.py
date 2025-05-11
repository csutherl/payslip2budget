from dataclasses import dataclass
from datetime import date
from typing import Optional
from models.transaction_base import Transaction

@dataclass
class YNABTransaction(Transaction):
    account_id: str
    category_id: Optional[str] = None
    cleared: str = "uncleared"  # 'cleared', 'uncleared', or 'reconciled'
    approved: bool = False # True or False
    flag_color: Optional[str] = None  # e.g., "red", "orange", etc.
    import_id: Optional[str] = None

    def to_api_dict(self) -> dict:
        return {
            "account_id": self.account_id,
            "date": self.date,
            "amount": self.amount,
            "payee_name": self.payee,
            "memo": self.memo,
            "cleared": self.cleared,
            "approved": self.approved,
            "flag_color": self.flag_color,
            "category_id": self.category_id,
            "import_id": self.import_id,
        }
