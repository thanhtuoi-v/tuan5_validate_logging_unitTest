from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URL: str
    REDIS_URL: str
    class Config:
        env_file = ".env"

settings = Settings()