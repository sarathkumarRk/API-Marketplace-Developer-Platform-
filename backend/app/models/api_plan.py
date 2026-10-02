from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey

from app.database import Base


class APIPlan(Base):
    __tablename__ = "api_plans"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, ForeignKey("apis.id"), nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(Float, default=0, nullable=False)
    requests_per_month = Column(Integer, nullable=False)
    requests_per_minute = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)