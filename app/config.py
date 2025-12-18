# app/config.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # project root (Apple_CLI/)

class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'apple_cli.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
