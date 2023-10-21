import os
from datetime import timedelta

from dotenv import load_dotenv


load_dotenv(dotenv_path='.env')

IS_PROD = True if os.getenv("APP_ENV") == 'prod' else False

# PROJECT SETTINGS
PROJECT_TITLE = 'TTS'
PROJECT_DESCRIPTION = 'Telegram technical support by A.V.Kritsky'
PROJECT_VERSION = '0.0.1a'

# DATABASE SETTINGS
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# JWT
JWT_SECRET_CODE = os.getenv("JWT_SECRET_CODE")
JWT_TTL_ACCESS = timedelta(hours=3)
JWT_TTL_REFRESH = timedelta(days=7)
JWT_ALGORITHM = 'HS256'

# REDIS
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_DB_FOR_JWT = 7
REDIS_DB_FOR_CACHE = 8


if __name__ == '__main__':
    print(POSTGRES_URL)
