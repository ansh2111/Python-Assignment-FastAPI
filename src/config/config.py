import os

from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings
from pydantic import BaseModel

env_files = ["local.env"]

config = Config()
for env_file in env_files:
    if os.path.exists(env_file):
        config = Config(env_file)

# Base
API_PREFIX = config("API_PREFIX", cast=str)
DEBUG = config("DEBUG", cast=bool)
APP_NAME = config("APP_NAME", cast=str)
VERSION = config("VERSION", cast=str, default="1.0.0")

# Scrapers settings
BASE_URL = config("BASE_URL", cast=str)
IMAGES_DOWNLOAD_PATH = config("IMAGES_DOWNLOAD_PATH", cast=str)
DB_PATH = config("DB_PATH", cast=str)

RETRY_COUNT = config("RETRY_COUNT", cast=int)
RETRY_INTERVAL_SECS = config("RETRY_INTERVAL_SECS", cast=int)

