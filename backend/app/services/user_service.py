from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def get_or_create(self, telegram_id: int) -> User:
        user = await self.get_by_telegram_id(telegram_id)
        if not user:
            user = User(telegram_id=telegram_id)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
        return user
