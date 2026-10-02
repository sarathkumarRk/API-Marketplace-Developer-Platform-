from datetime import datetime
from pydantic import BaseModel


class APIVersionCreate(BaseModel):
    api_id: int
    version: str
    base_url: str
    status: str


class APIVersionResponse(BaseModel):
    id: int
    api_id: int
    version: str
    base_url: str
    status: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True