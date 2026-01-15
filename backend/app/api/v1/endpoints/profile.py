from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import validate_telegram_init_data, extract_telegram_user_id
from app.services.user_service import UserService
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ProfileResponse(BaseModel):
    telegram_id: int
    first_name: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None
    gender: Optional[str] = None

@router.get("", response_model=ProfileResponse)
async def get_profile(
    init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    db: AsyncSession = Depends(get_db)
):
    """Получение профиля пользователя"""
    if not validate_telegram_init_data(init_data):
        raise HTTPException(status_code=401, detail="Invalid Telegram init data")
    
    telegram_id = extract_telegram_user_id(init_data)
    if not telegram_id:
        raise HTTPException(status_code=401, detail="Could not extract user ID")
    
    user_service = UserService(db)
    user = await user_service.get_by_telegram_id(telegram_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return ProfileResponse(
        telegram_id=user.telegram_id,
        first_name=user.first_name,
        age=user.age,
        city=user.city,
        gender=user.gender
    )
