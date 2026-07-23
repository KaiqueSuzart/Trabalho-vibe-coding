import os

from flask import Flask

from config import Config
from models import db

STATUS_LABELS = {
    "livre": "Livre",
    "reservada": "Reservada",
    "ocupada": "Ocupada",
    "manutencao": "Manutenção",
    "aberta": "Aberta",
    "fechamento_solicitado": "Fechamento pedido",
    "fechada": "Fechada",
    "recebido": "Recebido",
    "preparando": "Em preparo",
    "em preparo": "Em preparo",
    "pronto": "Pronto",
    "entregue": "Entregue",
    "cancelado": "Cancelado",
    "cancelada": "Cancelada",
    "pendente": "Pendente",
    "confirmada": "Confirmada",
    "checkin": "Check-in",
    "concluida": "Concluída",
    "pago": "Pago",
    "cobrar_entrega": "Cobrar na entrega",
    "online": "Online",
    "na_entrega": "Na entrega",
    "na_conta": "Na conta",
    "pix": "PIX",
    "dinheiro": "Dinheiro",
    "cartao": "Cartão",
}


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    from routes.admin import admin_bp
    from routes.api import api_bp
    from routes.auth import auth_bp
    from routes.barraca import barraca_bp
    from routes.kitchen import kitchen_bp
    from routes.public import public_bp
    from routes.waiter import waiter_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(waiter_bp, url_prefix="/garcom")
    app.register_blueprint(kitchen_bp, url_prefix="/cozinha")
    app.register_blueprint(barraca_bp, url_prefix="/barraca")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.template_filter("label")
    def status_label(value):
        if value is None:
            return ""
        key = str(value)
        return STATUS_LABELS.get(key, key.replace("_", " ").capitalize())

    @app.context_processor
    def inject_globals():
        from flask import has_request_context, session as flask_session

        if not has_request_context():
            return {"current_user_name": None, "current_role": None, "day_pin": app.config.get("DAY_PIN", "1234")}

        return {
            "current_user_name": flask_session.get("user_name"),
            "current_role": flask_session.get("role"),
            "day_pin": app.config.get("DAY_PIN", "1234"),
        }

    with app.app_context():
        # No Vercel o schema já foi criado via seed; create_all no cold start
        # atrasa/quebra a function (pooler transaction mode).
        if not os.environ.get("VERCEL"):
            from migrate import ensure_schema

            try:
                ensure_schema()
            except Exception as exc:
                app.logger.exception("Falha ao preparar schema: %s", exc)

    @app.errorhandler(404)
    def _json_404(err):
        """Sob /api, um 404 sempre volta como JSON (contrato do enunciado)."""
        from flask import request

        if request.path.startswith("/api/"):
            return {"erro": True, "mensagem": "Recurso não encontrado."}, 404
        return err

    @app.get("/health")
    def health():
        """Diagnóstico rápido de deploy (sem senha)."""
        uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        using_pg = uri.startswith("postgresql")
        host = ""
        if "@" in uri:
            host = uri.split("@", 1)[1].split("/", 1)[0]
        db_ok = False
        db_err = None
        if using_pg:
            try:
                from sqlalchemy import text

                db.session.execute(text("select 1"))
                db.session.commit()
                db_ok = True
            except Exception as exc:
                db.session.rollback()
                db_err = f"{type(exc).__name__}: {str(exc)[:240]}"
        payload = {
            "ok": db_ok if using_pg else True,
            "vercel": bool(os.environ.get("VERCEL")),
            "database": "postgres" if using_pg else "sqlite",
            "database_configured": bool(
                os.environ.get("DATABASE_URL") or os.environ.get("SUPABASE_DB_URL")
            ),
            "db_host": host,
            "db_ping": db_ok,
            "db_error": db_err,
        }
        return payload, (200 if payload["ok"] else 503)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
