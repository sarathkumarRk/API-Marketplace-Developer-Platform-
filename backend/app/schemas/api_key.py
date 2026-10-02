from datetime import datetime
from pydantic import BaseModel


class APIKeyCreate(BaseModel):
    developer_id: int
    subscription_id: int
    expires_at: datetime | None = None


class APIKeyResponse(BaseModel):
    id: int
    developer_id: int
    subscription_id: int
    key_prefix: str
    is_active: bool
    created_at: datetime | None = None
    last_used_at: datetime | None = None
    expires_at: datetime | None = None
    full_key: str | None = None

    class Config:
        from_attributes = True