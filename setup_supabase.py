"""
Cria tabelas no Postgres (Supabase) e popula dados demo.
Requer DATABASE_URL no arquivo .env

Uso:
  python setup_supabase.py
"""

from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")


def main():
    url = os.environ.get("DATABASE_URL") or os.environ.get("SUPABASE_DB_URL")
    if not url:
        print("ERRO: DATABASE_URL não configurada.")
        print()
        print("Como obter:")
        print("1) Supabase → Project Settings → Database")
        print("2) Copie a Connection string (URI) e troque [YOUR-PASSWORD]")
        print("3) Crie o arquivo .env (veja .env.example)")
        print()
        print("Sem a senha do banco, rode o SQL manualmente:")
        print("  supabase/schema.sql  →  SQL Editor → Run")
        raise SystemExit(1)

    # seed.py já faz drop/create + dados demo
    from seed import seed

    print("Conectando no Supabase Postgres...")
    seed()
    print()
    print("Pronto! Agora: python app.py")
    print("Login: admin/admin  |  garcom/garcom  |  PIN 1234")


if __name__ == "__main__":
    main()
