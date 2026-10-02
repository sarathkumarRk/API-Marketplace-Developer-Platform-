from datetime import datetime
from pydantic import BaseModel


class WebhookCreate(BaseModel):
    api_id: int
    event_type: str
    target_url: str
    secret: str
    is_active: bool = True


class WebhookResponse(BaseModel):
    id: int
    api_id: int
    event_type: str
    target_url: str
    is_active: bool

    class Config:
        from_attributes = True


class WebhookDeliveryResponse(BaseModel):
    id: int
    webhook_id: int
    event_id: str
    status: str
    response_code: int | None = None
    attempt_count: int
    delivered_at: datetime | None = None

    class Config:
        from_attributes = True