from pydantic import BaseModel


class APIEndpointCreate(BaseModel):
    api_version_id: int
    method: str
    path: str
    description: str | None = None
    authentication_required: bool = True


class APIEndpointResponse(BaseModel):
    id: int
    api_version_id: int
    method: str
    path: str
    description: str | None = None
    authentication_required: bool

    class Config:
        from_attributes = True