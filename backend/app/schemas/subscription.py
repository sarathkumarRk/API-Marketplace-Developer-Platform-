from datetime import datetime
from pydantic import BaseModel


class SubscriptionCreate(BaseModel):
    developer_id: int
    api_id: int
    plan_id: int


class SubscriptionResponse(BaseModel):
    id: int
    developer_id: int
    api_id: int
    plan_id: int
    stripe_subscription_id: str | None = None
    status: str
    started_at: datetime | None = None
    expires_at: datetime | None = None

    class Config:
        from_attributes = True