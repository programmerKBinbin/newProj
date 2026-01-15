from sqlalchemy import Column, BigInteger, String, Integer, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    city = Column(String(255), nullable=True)
    gender = Column(String(50), nullable=True)
    timezone = Column(String(50), nullable=True)
    language_code = Column(String(10), default="ru")
    is_premium = Column(Boolean, default=False)
    premium_until = Column(DateTime, nullable=True)
    onboarding_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
