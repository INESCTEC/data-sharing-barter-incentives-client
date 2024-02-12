from typing import List, Optional
from pydantic import BaseModel


class TransactionSchema(BaseModel):
    transaction_id: str
    timestamp: str
    confirmed: bool



