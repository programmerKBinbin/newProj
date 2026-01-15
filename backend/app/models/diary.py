from sqlalchemy import Column, BigInteger, String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Diary(Base):
    __tablename__ = "diaries"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    clone_id = Column(BigInteger, ForeignKey("clones.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Контент
    content_text = Column(Text, nullable=False)
    audio_file_path = Column(String(500), nullable=True)
    audio_duration_seconds = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    
    # Анализ
    analysis_result = Column(JSON, nullable=True)
    
    # Векторное представление (будет добавлено после установки pgvector)
    # content_embedding = Column(VECTOR(1536))
    
    # Метаданные
    created_at = Column(DateTime, server_default=func.now())
    analyzed_at = Column(DateTime, nullable=True)
    analysis_version = Column(String(50), nullable=True)
    
    # Relationships
    user = relationship("User", backref="diaries")
    clone = relationship("Clone", backref="diaries")
