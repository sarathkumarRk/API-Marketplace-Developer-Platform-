from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey

from app.database import Base


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)

    developer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    subscription_id = Column(
        Integer,
        ForeignKey("subscriptions.id"),
        nullable=False
    )

    key_hash = Column(String(255), nullable=False)
    key_prefix = Column(String(100), nullable=False)

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    last_used_at = Column(DateTime, nullable=True)

    expires_at = Column(DateTime, nullable=True)