from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.clone import Clone
from app.models.memory import CloneMemory
from app.services.openai_service import OpenAIService
import json

class CloneService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.openai_service = OpenAIService()
    
    async def get_user_clone(self, user_id: int) -> Clone | None:
        result = await self.db.execute(
            select(Clone).where(Clone.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def ask_clone(self, clone_id: int, question: str) -> str:
        """Получить ответ от клона на вопрос"""
        clone = await self.db.get(Clone, clone_id)
        if not clone:
            raise ValueError("Clone not found")
        
        # Получаем релевантные воспоминания
        memories_result = await self.db.execute(
            select(CloneMemory)
            .where(CloneMemory.clone_id == clone_id)
            .order_by(CloneMemory.importance_score.desc())
            .limit(10)
        )
        memories = list(memories_result.scalars().all())
        
        # Формируем системный промпт
        memories_text = "\n".join([f"- {m.memory_content}" for m in memories])
        
        system_prompt = f"""Ты - ИИ-клон пользователя. Твоя задача - общаться и думать как этот человек.

ПРОФИЛЬ ЛИЧНОСТИ:
{json.dumps(clone.personality_profile, ensure_ascii=False, indent=2)}

ВАЖНЫЕ ФАКТЫ О ПОЛЬЗОВАТЕЛЕ:
{memories_text}

СТИЛЬ ОБЩЕНИЯ:
- Используй слова и фразы, которые использует пользователь
- Отражай его эмоциональные паттерны
- Думай как он думает
- Реагируй как он реагирует

ПОМНИ:
- Ты не просто имитируешь, ты понимаешь его ценности и мотивации
- Используй конкретные факты из его жизни
- Будь последовательным в характере"""
        
        response = await self.openai_service.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content
