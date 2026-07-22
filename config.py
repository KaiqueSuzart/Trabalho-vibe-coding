import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "barraca-praia-faculdade-2026")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "barraca.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DAY_PIN = os.environ.get("DAY_PIN", "1234")
