from sqlalchemy import Column, BigInteger, String, Integer, Numeric, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Clone(Base):
    __tablename__ = "clones"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Профиль личности (JSONB)
    personality_profile = Column(JSON, nullable=False, default={})
    
    # Векторное представление (будет добавлено после установки pgvector)
    # personality_embedding = Column(VECTOR(1536))
    
    # Статистика
    accuracy_score = Column(Numeric(5, 2), default=0.00)
    diaries_count = Column(Integer, default=0)
    last_diary_at = Column(DateTime, nullable=True)
    total_words_analyzed = Column(Integer, default=0)
    
    # Состояние
    status = Column(String(50), default="creating")  # creating, active, paused, deleted
    training_stage = Column(String(50), default="initial")  # initial, learning, mature
    
    # Метаданные
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_trained_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", backref="clones")
