from sqlalchemy import Column, Integer, DateTime, ForeignKey
from app.database import Base


class UsageSummary(Base):
    __tablename__ = "usage_summaries"

    id = Column(Integer, primary_key=True, index=True)
    developer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    api_id = Column(
        Integer,
        ForeignKey("apis.id"),
        nullable=False
    )
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)