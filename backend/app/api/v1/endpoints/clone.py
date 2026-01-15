from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import validate_telegram_init_data, extract_telegram_user_id
from app.services.user_service import UserService
from app.services.clone_service import CloneService
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class CloneResponse(BaseModel):
    id: int
    personality_profile: dict
    accuracy_score: float
    diaries_count: int
    status: str

class CloneAskRequest(BaseModel):
    question: str

class CloneAskResponse(BaseModel):
    answer: str

@router.get("", response_model=CloneResponse)
async def get_clone(
    init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    db: AsyncSession = Depends(get_db)
):
    """Получение данных клона пользователя"""
    if not validate_telegram_init_data(init_data):
        raise HTTPException(status_code=401, detail="Invalid Telegram init data")
    
    telegram_id = extract_telegram_user_id(init_data)
    if not telegram_id:
        raise HTTPException(status_code=401, detail="Could not extract user ID")
    
    user_service = UserService(db)
    user = await user_service.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    clone_service = CloneService(db)
    clone = await clone_service.get_user_clone(user.id)
    
    if not clone:
        raise HTTPException(status_code=404, detail="Clone not found. Create your first diary to create a clone.")
    
    return CloneResponse(
        id=clone.id,
        personality_profile=clone.personality_profile or {},
        accuracy_score=float(clone.accuracy_score or 0),
        diaries_count=clone.diaries_count or 0,
        status=clone.status
    )

@router.post("/ask", response_model=CloneAskResponse)
async def ask_clone(
    request: CloneAskRequest,
    init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    db: AsyncSession = Depends(get_db)
):
    """Задать вопрос клону"""
    if not validate_telegram_init_data(init_data):
        raise HTTPException(status_code=401, detail="Invalid Telegram init data")
    
    telegram_id = extract_telegram_user_id(init_data)
    if not telegram_id:
        raise HTTPException(status_code=401, detail="Could not extract user ID")
    
    user_service = UserService(db)
    user = await user_service.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    clone_service = CloneService(db)
    clone = await clone_service.get_user_clone(user.id)
    
    if not clone:
        raise HTTPException(status_code=404, detail="Clone not found")
    
    answer = await clone_service.ask_clone(clone.id, request.question)
    
    return CloneAskResponse(answer=answer)
