from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database import Base


class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(
        Integer,
        ForeignKey("apis.id"),
        nullable=False
    )
    event_type = Column(String(100), nullable=False)
    target_url = Column(String(255), nullable=False)
    secret = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)