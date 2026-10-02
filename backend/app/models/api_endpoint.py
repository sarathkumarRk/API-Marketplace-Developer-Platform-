from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from app.database import Base


class APIEndpoint(Base):
    __tablename__ = "api_endpoints"

    id = Column(Integer, primary_key=True, index=True)
    api_version_id = Column(
        Integer,
        ForeignKey("api_versions.id"),
        nullable=False
    )
    method = Column(String(20), nullable=False)
    path = Column(String(255), nullable=False)
    description = Column(Text)
    authentication_required = Column(Boolean, default=True)