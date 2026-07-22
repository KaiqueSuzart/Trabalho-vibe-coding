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


def _with_sslmode(url: str) -> str:
    """Supabase/Vercel exige SSL; garante sslmode=require na URI."""
    if "sslmode=" in url:
        return url
    parsed = urlparse(url)
    q = parse_qs(parsed.query)
    q["sslmode"] = ["require"]
    return urlunparse(parsed._replace(query=urlencode(q, doseq=True)))


def _database_uri() -> str:
    url = (os.environ.get("DATABASE_URL") or os.environ.get("SUPABASE_DB_URL") or "").strip()
    # aspas acidentais no painel do Vercel
    if len(url) >= 2 and url[0] == url[-1] and url[0] in ("'", '"'):
        url = url[1:-1].strip()

    if url:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://") and "+psycopg2" not in url:
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return _with_sslmode(url)

    if os.environ.get("VERCEL"):
        raise RuntimeError(
            "DATABASE_URL não definida no Vercel. "
            "Settings → Environment Variables → "
            "postgresql://postgres.olsznvaungwnxdsbjprl:SENHA@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
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
            "connect_args": {
                "connect_timeout": 10,
                "sslmode": "require",
            },
        }
        if SQLALCHEMY_DATABASE_URI.startswith("postgresql")
        else {}
    )
    DAY_PIN = os.environ.get("DAY_PIN", "1234")
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
