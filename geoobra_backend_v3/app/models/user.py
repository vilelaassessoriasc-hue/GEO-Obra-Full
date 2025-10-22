from sqlalchemy import Column, Integer, String, Float, DateTime, func
from geoobra_backend_v3.app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(255), nullable=False, unique=False)  # sem índice único no schema atual
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    password_hash = Column(String(255), nullable=False)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
