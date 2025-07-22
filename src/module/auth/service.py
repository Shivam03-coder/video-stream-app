import boto3
import base64
import hashlib
import hmac
import bcrypt
from botocore.exceptions import ClientError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database.models.user_modle import User
from src.module.auth.schema import SignUpRequest
from src.configs.env_config import env
from src.common.exceptions import BadRequestError, DatabaseError, InternalServerError


class AuthService:
    _client = None
    _client_id = None
    _client_secret = None
    _region = None

    @staticmethod
    def _get_secret_hash(username: str, client_id: str, client_secret: str) -> str:
        message = username + client_id
        digest = hmac.new(
            client_secret.encode("utf-8"),
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

            secret_hash = cls._get_secret_hash(
                username=data.email,
                client_id=cls._client_id,
                client_secret=cls._client_secret,
            )

            response = cls._client.sign_up(
                ClientId=cls._client_id,
                Username=data.email,
                Password=data.password,
                UserAttributes=[
                    {"Name": "email", "Value": data.email},
                    {"Name": "name", "Value": data.name},
                ],
                SecretHash=secret_hash,
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
