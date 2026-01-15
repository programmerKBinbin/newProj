from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.diary import Diary
from app.models.clone import Clone
from datetime import datetime

class DiaryService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_diary(self, user_id: int, content_text: str, audio_file_path: str = None) -> Diary:
        # Получаем или создаем клон
        clone_result = await self.db.execute(
            select(Clone).where(Clone.user_id == user_id)
        )
        clone = clone_result.scalar_one_or_none()
        
        if not clone:
            # Создаем клон при первом дневнике
            clone = Clone(user_id=user_id, status="creating")
            self.db.add(clone)
            await self.db.flush()
        
        # Создаем дневник
        diary = Diary(
            user_id=user_id,
            clone_id=clone.id,
            content_text=content_text,
            audio_file_path=audio_file_path,
            word_count=len(content_text.split())
        )
        
        self.db.add(diary)
        
        # Обновляем статистику клона
        clone.diaries_count = (clone.diaries_count or 0) + 1
        clone.last_diary_at = datetime.utcnow()
        clone.total_words_analyzed = (clone.total_words_analyzed or 0) + diary.word_count
        
        await self.db.commit()
        await self.db.refresh(diary)
        
        return diary
    
    async def update_analysis(self, diary_id: int, analysis_result: dict):
        diary = await self.db.get(Diary, diary_id)
        if diary:
            diary.analysis_result = analysis_result
            diary.analyzed_at = datetime.utcnow()
            diary.analysis_version = "gpt-4"
            await self.db.commit()
    
    async def get_user_diaries(self, user_id: int) -> list[Diary]:
        result = await self.db.execute(
            select(Diary)
            .where(Diary.user_id == user_id)
            .order_by(Diary.created_at.desc())
        )
        return list(result.scalars().all())
