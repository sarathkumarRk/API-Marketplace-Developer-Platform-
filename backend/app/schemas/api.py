from datetime import datetime
from pydantic import BaseModel


class APICreate(BaseModel):
    organization_id: int
    name: str
    slug: str
    description: str | None = None
    category: str | None = None
    status: str


class APIResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    slug: str
    description: str | None = None
    category: str | None = None
    status: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True