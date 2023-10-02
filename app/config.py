import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cloud_name:str
    api_key:str
    api_secret:str

    class Config:
        env_file = ".env"


settings = Settings()
#headers = {"Authorization": f"Bearer {settings.api_token}"}