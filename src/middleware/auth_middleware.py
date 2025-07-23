from fastapi import Cookie, Depends
from src.common.exceptions import InternalServerError, NotFoundError
from src.libs.aws.cognito_client import CognitoClient


class AuthMiddleware:
    _cognito_client = CognitoClient()

    @classmethod
    def _get_user_from_cognito_id(cls, access_token: str):
        try:
            return cls._cognito_client.get_user(access_token)
        except Exception:
            raise InternalServerError("Error fetching user from Cognito")

    @classmethod
    def get_current_user(cls, access_token: str = Cookie(None)):
        if not access_token:
            raise NotFoundError("Access token not found in cookies")
        return cls._get_user_from_cognito_id(access_token)
