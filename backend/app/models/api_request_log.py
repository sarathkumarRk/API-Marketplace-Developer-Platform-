from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database import Base


class APIRequestLog(Base):
    __tablename__ = "api_request_logs"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(
        Integer,
        ForeignKey("apis.id"),
        nullable=False
    )
    api_version_id = Column(
        Integer,
        ForeignKey("api_versions.id"),
        nullable=False
    )
    developer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    endpoint_id = Column(
        Integer,
        ForeignKey("api_endpoints.id"),
        nullable=False
    )
    api_key_id = Column(
        Integer,
        ForeignKey("api_keys.id"),
        nullable=False
    )
    method = Column(String(20), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Integer)
    request_timestamp = Column(DateTime)