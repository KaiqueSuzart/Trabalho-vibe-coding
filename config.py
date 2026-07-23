import os
import re
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy.pool import NullPool

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

try:
    from dotenv import load_dotenv

    load_dotenv(Path(BASE_DIR) / ".env")
except ImportError:
    pass

# Região do projeto (confirmada pelo pooler que já funciona localmente)
SUPABASE_POOLER_HOST = os.environ.get(
    "SUPABASE_POOLER_HOST", "aws-0-us-east-1.pooler.supabase.com"
)


def _with_query(url: str, **params: str) -> str:
    parsed = urlparse(url)
    q = parse_qs(parsed.query)
    for key, value in params.items():
        q[key] = [value]
    return urlunparse(parsed._replace(query=urlencode(q, doseq=True)))


def _rewrite_direct_to_pooler(url: str) -> str:
    """
    Vercel não alcança db.*.supabase.co (IPv6).
    Reescreve Direct → Shared Pooler (IPv4), session :5432.
    """
    parsed = urlparse(url)
    host = parsed.hostname or ""
    m = re.match(r"^db\.([a-z0-9]+)\.supabase\.co$", host)
    if not m:
        return url

    ref = m.group(1)
    password = parsed.password or ""
    # user no Direct costuma ser "postgres"; no pooler é "postgres.<ref>"
    user = parsed.username or "postgres"
    if not user.startswith("postgres."):
        user = f"postgres.{ref}"

    # Remonta URI com pooler session (5432)
    netloc = f"{user}:{password}@{SUPABASE_POOLER_HOST}:5432"
    rewritten = urlunparse(
        (
            parsed.scheme,
            netloc,
            parsed.path or "/postgres",
            "",
            parsed.query,
            "",
        )
    )
    return rewritten


def _database_uri() -> str:
    url = (os.environ.get("DATABASE_URL") or os.environ.get("SUPABASE_DB_URL") or "").strip()
    if len(url) >= 2 and url[0] == url[-1] and url[0] in ("'", '"'):
        url = url[1:-1].strip()

    if url:
        if url.startswith("postgres://"):
            url = "postgresql+psycopg2://" + url[len("postgres://") :]
        elif url.startswith("postgresql+psycopg2://"):
            pass
        elif url.startswith("postgresql://"):
            url = "postgresql+psycopg2://" + url[len("postgresql://") :]

        # Corrige env antigo do Vercel (Direct IPv6)
        if os.environ.get("VERCEL"):
            url = _rewrite_direct_to_pooler(url)

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


def _secret_key() -> str:
    key = os.environ.get("SECRET_KEY", "").strip()
    if key:
        return key
    # Em produção a chave assina o cookie de sessão: sem ela, qualquer um que
    # conheça o valor commitado poderia forjar sessão de lojista. Exige env.
    if os.environ.get("VERCEL"):
        raise RuntimeError(
            "SECRET_KEY não definida no Vercel. Configure uma string secreta "
            "nas variáveis de ambiente (Production e Preview)."
        )
    # Fallback só para desenvolvimento local.
    return "dev-only-barraca-praia-local"


class Config:
    SECRET_KEY = _secret_key()
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
