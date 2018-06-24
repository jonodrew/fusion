from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_sendgrid import SendGrid
from flask_assets import Environment, Bundle
from os.path import abspath, join

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page'
# bootstrap = Bootstrap()
mail = SendGrid()
# assets = Environment()


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    # bootstrap.init_app(app)
    mail.init_app(app)
    # assets.init_app(app)
    # with app.app_context():
    #     assets.directory =  '/node_modules'

    """these are blueprints - a way of making a Flask application more modular and re-usable"""
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.matching import bp as matching_bp
    app.register_blueprint(matching_bp, url_prefix='/matching')

    return app


from app import models
