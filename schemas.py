from pydantic import BaseModel
from typing import Optional

class TickerDataSchema(BaseModel):
    id: int
    ticker: str
    price: float
    timestamp: int

    class Config:
        orm_mode = True
