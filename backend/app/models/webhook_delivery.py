from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database import Base


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(
        Integer,
        ForeignKey("webhooks.id"),
        nullable=False
    )
    event_id = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    response_code = Column(Integer)
    attempt_count = Column(Integer, default=0)
    delivered_at = Column(DateTime)