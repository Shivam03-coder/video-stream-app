import bcrypt
from botocore.client import ClientError
from fastapi import Cookie, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.common.exceptions import (
    BadRequestError,
    DatabaseError,
    InternalServerError,
    NotFoundError,
    ValidationError,
)
from src.database.models.user_modle import User
from src.libs.aws.cognito_client import CognitoClient
from src.module.auth.schema import ConfirmSignUpRequest, LoginRequest, SignUpRequest


class AuthService:
    _cognito_client = CognitoClient()

    @staticmethod
    def _hash_password(password: str):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def _check_password(password: str, hashed: str):
        return bcrypt.checkpw(password, hashed)

    @classmethod
    async def sign_up(cls, data: SignUpRequest, db: AsyncSession) -> dict:
        try:
            query = await db.execute(select(User).where(User.email == data.email))
            existing_user = query.scalars().first()

            if existing_user:
                raise BadRequestError("User already exists")

            response = cls._cognito_client.sign_up(data.email, data.password, data.name)

            cognito_sub = response.get("UserSub")
            if not cognito_sub:
                raise InternalServerError("Cognito did not return a valid user sub")

            hashed_password = cls._hash_password(data.password)

            new_user = User(
                name=data.name,
                email=data.email,
                cognito_sub=cognito_sub,
                password=hashed_password,
            )

            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)

            return {
                "message": "User Account Created Successfully! Please verify your email!"
            }

        except ClientError as e:
            raise DatabaseError(
                e.response.get("Error", {}).get("Message", "Cognito sign-up failed.")
            )

    @classmethod
    async def verify_email(cls, data: ConfirmSignUpRequest, db: AsyncSession) -> dict:
        try:
            cls._cognito_client.confirm_sign_up(data.email, data.code)
            return {"message": "User email confirmed successfully"}
        except ClientError as e:
            raise DatabaseError(
                e.response.get("Error", {}).get("Message", "Email verification failed.")
            )

    @classmethod
    async def login(cls, data: LoginRequest, db: AsyncSession, res: Response) -> dict:
        try:
            query = await db.execute(select(User).where(User.email == data.email))
            existing_user = query.scalars().first()

            if not existing_user:
                raise NotFoundError("User with this email not found")

            response = cls._cognito_client.initiate_auth(data.email, data.password)
            auth_result = response.get("AuthenticationResult")

            if not auth_result:
                raise ValidationError("User login failed")

            res.set_cookie(
                "access_token",
                auth_result.get("AccessToken"),
                httponly=True,
                secure=True,
            )
            res.set_cookie(
                "refresh_token",
                auth_result.get("RefreshToken"),
                httponly=True,
                secure=True,
            )

            return {"message": "User logged in Successfully!"}

        except ClientError as e:
            raise DatabaseError(
                e.response.get("Error", {}).get("Message", "Login failed.")
            )

    @classmethod
    async def refresh_token(
        cls,
        refresh_token: str = Cookie(None),
        user_cognito_id: str = Cookie(None),
        res: Response = None,
    ) -> dict:
        try:
            response = cls._cognito_client.refresh_token(refresh_token, user_cognito_id)
            auth_result = response.get("AuthenticationResult")

            if not auth_result:
                raise ValidationError("Token refresh failed")

            res.set_cookie(
                "access_token",
                auth_result.get("AccessToken"),
                httponly=True,
                secure=True,
            )
            return {"message": "User Token Refreshed Successfully!"}
        except ClientError as e:
            raise DatabaseError(
                e.response.get("Error", {}).get("Message", "Token refresh failed.")
            )
