import boto3
from botocore.exceptions import ClientError
from src.utils.error_utils import ValidationError
from src.module.auth.auth_schema import SignUpRequest


class CognitoService:
    _client = None
    _user_pool_id: str = None
    _client_id: str = None

    @classmethod
    def configure(cls, client_id: str, region: str):
        cls._client_id = client_id
        cls._client = boto3.client("cognito-idp", region_name=region)

    @classmethod
    def sign_up(cls, data: SignUpRequest) -> dict:

        if not cls._client:
            raise RuntimeError("CognitoService not configured. Call configure() first.")

        try:
            response = cls._client.sign_up(
                ClientId=cls._client_id,
                Username=data.email,
                Password=data.password,
                UserAttributes=[
                    {"Name": "email", "Value": data.email},
                    {"Name": "name", "Value": data.name},
                ],
            )
            print(response)
            return response
        except ClientError as e:
            message = e.response.get("Error", {}).get(
                "Message", "Something went wrong with Cognito."
            )
            raise ValidationError(message)
