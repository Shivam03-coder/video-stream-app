from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.session import get_session
from src.module.auth.schema import SignUpRequest
from src.module.auth.service import AuthService

auth_router = APIRouter(tags=["Auth"])


@auth_router.post("/sign_up")
async def register(user_data: SignUpRequest, db: AsyncSession = Depends(get_session)):
    return await AuthService.sign_up(user_data, db)
