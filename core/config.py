from pydantic import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/v1"
    PROJECT_NAME: str = "mychat"
    ORIGINS = ["*", ]
    openai_key: str
    claude_key: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

