import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME")

DB_CONFIG = {
    "Driver": os.getenv("DB_Driver")
    "server": os.getenv("DB_SERVER"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}