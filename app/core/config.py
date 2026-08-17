from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Carrega as configurações a partir do arquivo .env.
    Nunca deixe SECRET_KEY ou DATABASE_URL fixos no código em produção.
    """
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
