from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import validate_telegram_init_data, extract_telegram_user_id
from app.services.user_service import UserService
from app.services.openai_service import OpenAIService
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class OnboardingAnswer(BaseModel):
    field: str
    value: str

class OnboardingStatusResponse(BaseModel):
    completed: bool
    current_step: Optional[str] = None

@router.get("/status")
async def get_onboarding_status(
    init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    db: AsyncSession = Depends(get_db)
):
    """Проверка статуса анкеты"""
    if not validate_telegram_init_data(init_data):
        raise HTTPException(status_code=401, detail="Invalid Telegram init data")
    
    telegram_id = extract_telegram_user_id(init_data)
    if not telegram_id:
        raise HTTPException(status_code=401, detail="Could not extract user ID")
    
    user_service = UserService(db)
    user = await user_service.get_by_telegram_id(telegram_id)
    
    if not user:
        return OnboardingStatusResponse(completed=False, current_step="welcome")
    
    return OnboardingStatusResponse(
        completed=user.onboarding_completed,
        current_step=None if user.onboarding_completed else "name"
    )

@router.post("/answer")
async def save_onboarding_answer(
    answer: OnboardingAnswer,
    init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    db: AsyncSession = Depends(get_db)
):
    """Сохранение ответа на вопрос анкеты"""
    if not validate_telegram_init_data(init_data):
        raise HTTPException(status_code=401, detail="Invalid Telegram init data")
    
    telegram_id = extract_telegram_user_id(init_data)
    if not telegram_id:
        raise HTTPException(status_code=401, detail="Could not extract user ID")
    
    user_service = UserService(db)
    user = await user_service.get_or_create(telegram_id)
    
    # Сохраняем ответ
    if answer.field == "name":
        user.first_name = answer.value
    elif answer.field == "age":
        try:
            user.age = int(answer.value)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid age")
    elif answer.field == "city":
        user.city = answer.value
    elif answer.field == "gender":
        user.gender = answer.value
    
    await db.commit()
    await db.refresh(user)
    
    # Определяем следующий шаг
    next_field = None
    if not user.first_name:
        next_field = "name"
    elif not user.age:
        next_field = "age"
    elif not user.city:
        next_field = "city"
    elif not user.gender:
        next_field = "gender"
    else:
        user.onboarding_completed = True
        await db.commit()
    
    return {"status": "saved", "next_field": next_field, "completed": user.onboarding_completed}

@router.get("/guess-gender")
async def guess_gender(
    name: str,
    init_data: str = Header(..., alias="X-Telegram-Init-Data")
):
    """Предположение пола по имени"""
    if not validate_telegram_init_data(init_data):
        raise HTTPException(status_code=401, detail="Invalid Telegram init data")
    
    openai_service = OpenAIService()
    guess = await openai_service.guess_gender(name)
    
    return {"gender": guess}
