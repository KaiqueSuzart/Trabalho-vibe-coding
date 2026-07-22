import os
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy.pool import NullPool

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

try:
    from dotenv import load_dotenv

    load_dotenv(Path(BASE_DIR) / ".env")
except ImportError:
    pass


def _with_query(url: str, **params: str) -> str:
    parsed = urlparse(url)
    q = parse_qs(parsed.query)
    for key, value in params.items():
        q[key] = [value]
    return urlunparse(parsed._replace(query=urlencode(q, doseq=True)))


def _database_uri() -> str:
    url = (os.environ.get("DATABASE_URL") or os.environ.get("SUPABASE_DB_URL") or "").strip()
    if len(url) >= 2 and url[0] == url[-1] and url[0] in ("'", '"'):
        url = url[1:-1].strip()

    if url:
        # Normaliza esquemas comuns
        if url.startswith("postgres://"):
            url = "postgresql+psycopg2://" + url[len("postgres://") :]
        elif url.startswith("postgresql+psycopg2://"):
            pass
        elif url.startswith("postgresql://"):
            url = "postgresql+psycopg2://" + url[len("postgresql://") :]

        # SSL obrigatório no Supabase/Vercel
        if "sslmode=" not in url:
            url = _with_query(url, sslmode="require")
        return url

    if os.environ.get("VERCEL"):
        raise RuntimeError(
            "DATABASE_URL não definida no Vercel. "
            "Use o pooler: "
            "postgresql://postgres.REF:SENHA@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require"
        )

    return "sqlite:///" + os.path.join(BASE_DIR, "barraca.db")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "barraca-praia-faculdade-2026")
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = (
        {
            "poolclass": NullPool,
            "pool_pre_ping": True,
            "connect_args": {"connect_timeout": 15},
        }
        if SQLALCHEMY_DATABASE_URI.startswith("postgresql")
        else {}
    )
    DAY_PIN = os.environ.get("DAY_PIN", "1234")
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
