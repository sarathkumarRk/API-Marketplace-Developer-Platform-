from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

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
    plan_id = Column(
        Integer,
        ForeignKey("api_plans.id"),
        nullable=False
    )
    stripe_subscription_id = Column(String(255))
    status = Column(String(50), nullable=False)
    started_at = Column(DateTime)
    expires_at = Column(DateTime)