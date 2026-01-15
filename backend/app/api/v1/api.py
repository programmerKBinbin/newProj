from fastapi import APIRouter
from app.api.v1.endpoints import onboarding, diaries, clone, profile

api_router = APIRouter()

api_router.include_router(onboarding.router, prefix="/onboarding", tags=["onboarding"])
api_router.include_router(diaries.router, prefix="/diaries", tags=["diaries"])
api_router.include_router(clone.router, prefix="/clone", tags=["clone"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
