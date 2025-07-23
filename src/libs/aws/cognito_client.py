# src/common/aws/cognito_client.py

import base64
import hashlib
import hmac
import boto3
from src.configs.env_config import env


class CognitoClient:
    def __init__(self):
        self.client_id = env.COGNITO_CLIENT_ID
        self.client_secret = env.COGNITO_CLIENT_SECRET
        self.region = env.COGNITO_CLIENT_REGION or "ap-south-1"
        self.client = boto3.client("cognito-idp", region_name=self.region)

    def get_secret_hash(self, username: str) -> str:
        message = username + self.client_id
        digest = hmac.new(
            self.client_secret.encode("utf-8"),
            msg=message.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        return base64.b64encode(digest).decode("utf-8")

    def sign_up(self, email: str, password: str, name: str):
        return self.client.sign_up(
            ClientId=self.client_id,
            Username=email,
            Password=password,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "name", "Value": name},
            ],
            SecretHash=self.get_secret_hash(email),
        )

    def confirm_sign_up(self, email: str, code: str):
        return self.client.confirm_sign_up(
            ClientId=self.client_id,
            Username=email,
            ConfirmationCode=code,
            SecretHash=self.get_secret_hash(email),
        )

    def initiate_auth(self, email: str, password: str):
        return self.client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=self.client_id,
            AuthParameters={
                "USERNAME": email,
                "PASSWORD": password,
                "SECRET_HASH": self.get_secret_hash(email),
            },
        )

    def refresh_token(self, refresh_token: str, user_cognito_id: str):
        return self.client.initiate_auth(
            AuthFlow="REFRESH_TOKEN_AUTH",
            ClientId=self.client_id,
            AuthParameters={
                "REFRESH_TOKEN": refresh_token,
                "SECRET_HASH": self.get_secret_hash(user_cognito_id),
            },
        )

    def get_user(self, access_token: str):
        resp = self.client.get_user(AccessToken=access_token)
        return {attr["Name"]: attr["Value"] for attr in resp.get("UserAttributes", [])}
