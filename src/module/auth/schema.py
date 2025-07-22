from pydantic import BaseModel


class SignUpRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ConfirmSignUpRequest(BaseModel):
    email: str
    code: str
