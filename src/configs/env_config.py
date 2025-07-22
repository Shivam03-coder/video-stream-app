from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    COGNITO_CLIENT_ID: str
    COGNITO_CLIENT_SECRET: str
    COGNITO_CLIENT_REGION: str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


env: Settings = Settings()
