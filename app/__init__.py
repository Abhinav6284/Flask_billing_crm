from flask import Flask
from config import Config
from extensions import db, migrate, login_manager, bcrypt, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.crm import crm_bp
    from app.routes.products import products_bp
    from app.routes.billing import billing_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(crm_bp, url_prefix='/customers')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(billing_bp, url_prefix='/invoices')

    return app
