# app/__init__.py
from flask import Flask

from app.db import db

# Blueprints
from app.route.user_bp import user_bp
from app.route.portfolio_bp import portfolio_bp
from app.route.security_bp import security_bp


def create_app(config_class):
    """
    Application factory.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Init extensions
    db.init_app(app)

    # Optional: friendly root route so / doesn't look broken
    @app.get("/")
    def home():
        return {"message": "Apple_CLI API running"}, 200

    # Register blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(security_bp)

    # Create tables (development convenience).
    # IMPORTANT: import models so SQLAlchemy registers them before create_all()
    with app.app_context():
        from app.domain.user import User  # noqa: F401
        from app.domain.portfolio import Portfolio  # noqa: F401
        from app.domain.security import Security  # noqa: F401
        from app.domain.investment import Investment  # noqa: F401
        from app.domain.transactions import Transaction  # noqa: F401

        db.create_all()

    return app
