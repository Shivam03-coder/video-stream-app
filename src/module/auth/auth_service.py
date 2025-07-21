from ...services.cognito_service import CognitoService
from src.configs.env_config import env
from .auth_schema import SignUpRequest


class AuthService:
    @classmethod
    def initialize(cls):
        CognitoService.configure(
            client_id=env.COGNITO_CLIENT_ID, region=env.COGNITO_CLIENT_REGION
        )

    @staticmethod
    def sign_up(data: SignUpRequest):
        return CognitoService.sign_up(data)
