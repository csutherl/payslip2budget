from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass(kw_only=True)
class Transaction:
    date: date
    payee: str
    category: Optional[str] = None
    memo: str
    amount: float  # In dollars for base class
