import os
from pathlib import Path

from sqlalchemy.pool import NullPool

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Carrega .env local (não versionado)
try:
    from dotenv import load_dotenv

    load_dotenv(Path(BASE_DIR) / ".env")
except ImportError:
    pass


def _database_uri() -> str:
    url = os.environ.get("DATABASE_URL") or os.environ.get("SUPABASE_DB_URL")
    if url:
        # SQLAlchemy 2 + postgres
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://") and "+psycopg2" not in url:
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    # No Vercel o filesystem é read-only: SQLite quebra a function
    if os.environ.get("VERCEL"):
        raise RuntimeError(
            "DATABASE_URL não está definida no Vercel. "
            "Project Settings → Environment Variables → adicione DATABASE_URL do Supabase."
        )

    return "sqlite:///" + os.path.join(BASE_DIR, "barraca.db")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "barraca-praia-faculdade-2026")
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Serverless (Vercel): sem pool persistente entre invocações
    # NullPool só no Postgres (SQLite local não precisa / conflita com alguns drivers)
    SQLALCHEMY_ENGINE_OPTIONS = (
        {
            "poolclass": NullPool,
            "pool_pre_ping": True,
            "connect_args": {"connect_timeout": 10},
        }
        if SQLALCHEMY_DATABASE_URI.startswith("postgresql")
        else {}
    )
    DAY_PIN = os.environ.get("DAY_PIN", "1234")
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
