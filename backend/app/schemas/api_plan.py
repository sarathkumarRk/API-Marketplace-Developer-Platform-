from decimal import Decimal
from pydantic import BaseModel


class APIPlanCreate(BaseModel):
    api_id: int
    name: str
    price: Decimal
    requests_per_month: int
    requests_per_minute: int
    is_active: bool = True


class APIPlanResponse(BaseModel):
    id: int
    api_id: int
    name: str
    price: Decimal
    requests_per_month: int
    requests_per_minute: int
    is_active: bool

    class Config:
        from_attributes = True