from sqlalchemy import Column, BigInteger, String, Integer, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class CloneMemory(Base):
    __tablename__ = "clone_memories"
    
    id = Column(BigInteger, primary_key=True, index=True)
    clone_id = Column(BigInteger, ForeignKey("clones.id", ondelete="CASCADE"), nullable=False, index=True)
    source_diary_id = Column(BigInteger, ForeignKey("diaries.id", ondelete="SET NULL"), nullable=True)
    
    # Тип и содержимое
    memory_type = Column(String(50), nullable=False)  # fact, preference, experience, relationship, goal, fear
    memory_content = Column(Text, nullable=False)
    memory_context = Column(Text, nullable=True)
    
    # Важность
    importance_score = Column(Numeric(3, 2), default=0.5)
    confidence_score = Column(Numeric(3, 2), default=0.5)
    
    # Векторное представление (будет добавлено после установки pgvector)
    # memory_embedding = Column(VECTOR(1536))
    
    # Метаданные
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_used_at = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)
    
    # Relationships
    clone = relationship("Clone", backref="memories")
    source_diary = relationship("Diary", backref="memories")
