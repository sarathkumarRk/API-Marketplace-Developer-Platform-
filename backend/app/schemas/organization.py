from datetime import datetime
from pydantic import BaseModel


class OrganizationCreate(BaseModel):
    name: str
    owner_id: int


class OrganizationResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime | None = None

    class Config:
        from_attributes = True