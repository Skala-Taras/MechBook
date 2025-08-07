from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    URL_DB: str
    ELASTIC_HOST: str
    jwt_secret_key: str
    algorithm: str

    class Config:
        env_file = ".env"

settings = Settings()