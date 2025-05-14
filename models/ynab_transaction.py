from dataclasses import dataclass
from datetime import date
from typing import Optional
from models.transaction_base import Transaction

@dataclass(kw_only=True)
class YNABTransaction(Transaction):
    account_id: str
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    cleared: str = "uncleared"  # 'cleared', 'uncleared', or 'reconciled'
    approved: bool = False # True or False
    flag_color: Optional[str] = None  # e.g., "red", "orange", etc.
    import_id: Optional[str] = None
    payee_id: Optional[str] = None

    def to_api_dict(self) -> dict:
        return {
            "account_id": self.account_id,
            "date": self.date,
            "amount": self.amount,
            "payee_name": self.payee,
            "payee_id": self.payee_id,
            "memo": self.memo,
            "cleared": self.cleared,
            "approved": self.approved,
            "flag_color": self.flag_color,
            "category_id": self.category_id,
            "category_name": self.category_name,
            "import_id": self.import_id,
        }
