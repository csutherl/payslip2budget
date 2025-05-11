from dataclasses import dataclass
from datetime import date

@dataclass
class Transaction:
    date: date
    payee: str
    memo: str
    amount: float  # In dollars for base class
