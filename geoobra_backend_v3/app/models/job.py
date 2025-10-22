from sqlalchemy import Column, Integer, String, Float, DateTime, func
from geoobra_backend_v3.app.db.session import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(2000), nullable=True)
    company_id = Column(Integer, nullable=False)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    radius_km = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
