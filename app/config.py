import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-use-32-plus-chars")
    JWT_SECRET = os.getenv("JWT_SECRET", "change-this-jwt-secret-key-use-32-plus-chars")
    JWT_EXPIRES_SECONDS = int(os.getenv("JWT_EXPIRES_SECONDS", "3600"))
    TEMP_TOKEN_EXPIRES_SECONDS = int(os.getenv("TEMP_TOKEN_EXPIRES_SECONDS", "30"))
    DATABASE_PATH = os.getenv("DATABASE_PATH", "auth.db")
