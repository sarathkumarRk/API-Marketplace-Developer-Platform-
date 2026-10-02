from datetime import datetime
from pydantic import BaseModel


class UsageSummaryResponse(BaseModel):
    id: int
    developer_id: int
    api_id: int
    period_start: datetime | None = None
    period_end: datetime | None = None
    total_requests: int
    successful_requests: int
    failed_requests: int

    class Config:
        from_attributes = True