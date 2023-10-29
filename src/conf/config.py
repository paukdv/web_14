from pydantic_settings import BaseSettings
from pydantic import EmailStr


class Settings(BaseSettings):
    sqlalchemy_database_url: str
    secret_key_jwt: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: EmailStr
    mail_port: int
    mail_server: str
    redis_host: str = "localhost"
    redis_port: int = 6379

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: int

    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
