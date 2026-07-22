from flask import Flask

from config import Config
from models import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    from routes.admin import admin_bp
    from routes.api import api_bp
    from routes.auth import auth_bp
    from routes.kitchen import kitchen_bp
    from routes.public import public_bp
    from routes.waiter import waiter_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(waiter_bp, url_prefix="/garcom")
    app.register_blueprint(kitchen_bp, url_prefix="/cozinha")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.context_processor
    def inject_globals():
        from flask import session as flask_session

        return {
            "current_user_name": flask_session.get("user_name"),
            "current_role": flask_session.get("role"),
        }

    with app.app_context():
        from migrate import ensure_schema

        ensure_schema()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
