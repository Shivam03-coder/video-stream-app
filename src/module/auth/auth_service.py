import boto3
from botocore.exceptions import ClientError
from src.utils.error_utils import ValidationError
from src.module.auth.auth_schema import SignUpRequest
from src.configs.env_config import env
from src.module.auth.auth_helper import AuthHelper


class AuthService:
    _client = None
    _client_id = None
    _client_secret = None
    _region = None

    @classmethod
    def _ensure_client(cls):
        if cls._client is None:
            cls._client_id = env.COGNITO_CLIENT_ID
            cls._client_secret = env.COGNITO_CLIENT_SECRET
            cls._region = env.COGNITO_CLIENT_REGION or "ap-south-1"
            cls._client = boto3.client("cognito-idp", region_name=cls._region)

    @classmethod
    def sign_up(cls, data: SignUpRequest) -> dict:
        cls._ensure_client()

        try:
            secret_hash = AuthHelper.get_secret_hash(
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
            return response
        except ClientError as e:
            message = e.response.get("Error", {}).get(
                "Message", "Cognito sign-up failed."
            )
            raise ValidationError(message)
