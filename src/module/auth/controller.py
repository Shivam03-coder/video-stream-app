from fastapi import APIRouter, Cookie, HTTPException, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.session import get_session
from src.module.auth.schema import SignUpRequest, ConfirmSignUpRequest, LoginRequest
from src.module.auth.service import AuthService

auth_router = APIRouter(tags=["Auth"])


@auth_router.post("/sign_up")
async def register(user_data: SignUpRequest, db: AsyncSession = Depends(get_session)):
    return await AuthService.sign_up(user_data, db)


@auth_router.post("/verify_email")
async def register(
    user_data: ConfirmSignUpRequest, db: AsyncSession = Depends(get_session)
):
    return await AuthService.verify_email(user_data, db)


@auth_router.post("/login")
async def register(
    user_data: LoginRequest,
    res: Response,
    db: AsyncSession = Depends(get_session),
):
    return await AuthService.login(user_data, db, res)


@auth_router.post("/refresh_token")
async def register(
    refresh_token: str = Cookie(None),
    user_cognito_id: str = Cookie(None),
    res: Response = None,
):
    return await AuthService.refresh_token(refresh_token, user_cognito_id, res)
