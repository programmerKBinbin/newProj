from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import validate_telegram_init_data, extract_telegram_user_id
from app.services.user_service import UserService
from app.services.diary_service import DiaryService
from app.services.openai_service import OpenAIService
from pydantic import BaseModel
from typing import Optional
import os
from app.core.config import settings

router = APIRouter()

class DiaryCreateText(BaseModel):
    text: str

class DiaryResponse(BaseModel):
    id: int
    content_text: str
    created_at: str
    analyzed_at: Optional[str] = None

@router.post("", response_model=DiaryResponse)
async def create_diary(
    init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    text: Optional[str] = None,
    audio: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    """Создание дневника (текст или аудио)"""
    if not validate_telegram_init_data(init_data):
        raise HTTPException(status_code=401, detail="Invalid Telegram init data")
    
    telegram_id = extract_telegram_user_id(init_data)
    if not telegram_id:
        raise HTTPException(status_code=401, detail="Could not extract user ID")
    
    user_service = UserService(db)
    user = await user_service.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    diary_service = DiaryService(db)
    openai_service = OpenAIService()
    
    # Обработка текста или аудио
    diary_text = None
    audio_path = None
    
    if audio:
        # Сохраняем аудио файл
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        audio_path = os.path.join(settings.UPLOAD_DIR, f"{user.id}_{audio.filename}")
        with open(audio_path, "wb") as f:
            content = await audio.read()
            f.write(content)
        
        # Транскрипция
        diary_text = await openai_service.transcribe_audio(audio_path)
    elif text:
        diary_text = text
    else:
        raise HTTPException(status_code=400, detail="Either text or audio must be provided")
    
    # Создание дневника
    diary = await diary_service.create_diary(
        user_id=user.id,
        content_text=diary_text,
        audio_file_path=audio_path
    )
    
    # Анализ дневника (в фоне через Celery в будущем)
    try:
        analysis_result = await openai_service.analyze_diary(diary_text)
        await diary_service.update_analysis(diary.id, analysis_result)
    except Exception as e:
        # Логируем ошибку, но не прерываем создание дневника
        print(f"Error analyzing diary: {e}")
    
    return DiaryResponse(
        id=diary.id,
        content_text=diary.content_text,
        created_at=diary.created_at.isoformat(),
        analyzed_at=diary.analyzed_at.isoformat() if diary.analyzed_at else None
    )

@router.get("")
async def get_diaries(
    init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка дневников пользователя"""
    if not validate_telegram_init_data(init_data):
        raise HTTPException(status_code=401, detail="Invalid Telegram init data")
    
    telegram_id = extract_telegram_user_id(init_data)
    if not telegram_id:
        raise HTTPException(status_code=401, detail="Could not extract user ID")
    
    user_service = UserService(db)
    user = await user_service.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    diary_service = DiaryService(db)
    diaries = await diary_service.get_user_diaries(user.id)
    
    return [
        DiaryResponse(
            id=d.id,
            content_text=d.content_text,
            created_at=d.created_at.isoformat(),
            analyzed_at=d.analyzed_at.isoformat() if d.analyzed_at else None
        )
        for d in diaries
    ]
