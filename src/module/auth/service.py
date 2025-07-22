import boto3
import base64
import hashlib
import hmac
import bcrypt
from botocore.exceptions import ClientError
from fastapi import Cookie, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database.models.user_modle import User
from src.module.auth.schema import ConfirmSignUpRequest, SignUpRequest, LoginRequest
from src.configs.env_config import env
from src.common.exceptions import (
    BadRequestError,
    DatabaseError,
    InternalServerError,
    NotFoundError,
    ValidationError,
)


class AuthService:
    _client = None
    _client_id = None
    _client_secret = None
    _region = None

    @classmethod
    def _get_secret_hash(cls, username: str) -> str:
        message = username + cls._client_id

        digest = hmac.new(
            cls._client_secret.encode("utf-8"),
            msg=message.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()

        return base64.b64encode(digest).decode("utf-8")

    @staticmethod
    def _hash_password(password: str):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def _check_password(password: str, hashed: str):
        return bcrypt.checkpw(password, hashed)

    @classmethod
    def _ensure_client(cls):
        if cls._client is None:
            cls._client_id = env.COGNITO_CLIENT_ID
            cls._client_secret = env.COGNITO_CLIENT_SECRET
            cls._region = env.COGNITO_CLIENT_REGION or "ap-south-1"
            cls._client = boto3.client("cognito-idp", region_name=cls._region)

    @classmethod
    async def sign_up(cls, data: SignUpRequest, db: AsyncSession) -> dict:
        cls._ensure_client()

        try:
            query = await db.execute(select(User).where(User.email == data.email))
            existing_user = query.scalars().first()

            if existing_user:
                raise BadRequestError("User already exists")

            response = cls._client.sign_up(
                ClientId=cls._client_id,
                Username=data.email,
                Password=data.password,
                UserAttributes=[
                    {"Name": "email", "Value": data.email},
                    {"Name": "name", "Value": data.name},
                ],
                SecretHash=cls._get_secret_hash(data.email),
            )

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
            message = e.response.get("Error", {}).get(
                "Message", "Cognito sign-up failed."
            )
            raise DatabaseError(message)

    #   ========= VERIFY EMAIL =======

    @classmethod
    async def verify_email(cls, data: ConfirmSignUpRequest, db: AsyncSession) -> dict:
        cls._ensure_client()

        try:

            response = cls._client.confirm_sign_up(
                ClientId=cls._client_id,
                Username=data.email,
                ConfirmationCode=data.code,
                SecretHash=cls._get_secret_hash(data.email),
            )

            return {"message": "User email confirmed sucessfully"}

        except ClientError as e:
            message = e.response.get("Error", {}).get(
                "Message", "Cognito sign-up failed."
            )
            raise DatabaseError(message)

    #   ========= LOGIN =======

    @classmethod
    async def login(cls, data: LoginRequest, db: AsyncSession, res: Response) -> dict:
        cls._ensure_client()

        try:
            query = await db.execute(select(User).where(User.email == data.email))
            existing_user = query.scalars().first()

            if not existing_user:
                raise NotFoundError("User with this email not found")

            response = cls._client.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                ClientId=cls._client_id,
                AuthParameters={
                    "USERNAME": data.email,
                    "PASSWORD": data.password,
                    "SECRET_HASH": cls._get_secret_hash(data.email),
                },
            )

            auth_result = response.get("AuthenticationResult")

            if not auth_result:
                raise ValidationError("User login failed")

            access_token = auth_result.get("AccessToken")
            refresh_token = auth_result.get("RefreshToken")

            res.set_cookie("access_token", access_token, httponly=True, secure=True)
            res.set_cookie("refresh_token", refresh_token, httponly=True, secure=True)

            return {"message": "User logedin Successfully!"}

        except ClientError as e:
            message = e.response.get("Error", {}).get(
                "Message", "Cognito sign-up failed."
            )
            raise DatabaseError(message)

    @classmethod
    async def refresh_token(
        cls, refresh_token: Cookie(None), user_cognito_id: Cookie(None), res: Response
    ) -> dict:
        cls._ensure_client()

        try:
            response = cls._client.initiate_auth(
                AuthFlow="REFRESH_TOKEN_AUTH",
                ClientId=cls._client_id,
                AuthParameters={
                    "REFRESH_TOKEN": refresh_token,
                    "SECRET_HASH": cls._get_secret_hash(),
                },
            )

            auth_result = response.get("AuthenticationResult")

            if not auth_result:
                raise ValidationError("User login failed")

            access_token = auth_result.get("AccessToken")
            refresh_token = auth_result.get("RefreshToken")

            res.set_cookie("access_token", access_token, httponly=True, secure=True)
            res.set_cookie("refresh_token", refresh_token, httponly=True, secure=True)

            return {"message": "User Token Refresh Successfully!"}

        except ClientError as e:
            message = e.response.get("Error", {}).get(
                "Message", "Cognito sign-up failed."
            )
            raise DatabaseError(message)
