import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    cloud_name:str
    api_key:str
    api_secret:str

    class Config:
        env_file = ".env"


settings = Settings()
#headers = {"Authorization": f"Bearer {settings.api_token}"}