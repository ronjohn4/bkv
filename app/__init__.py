from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
import logging
from logging.handlers import RotatingFileHandler
import os
from config import Config


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
bootstrap = Bootstrap()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # bag.url_map.strict_slashes = False

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)

    from app.audit import bp as audit_bp
    app.register_blueprint(audit_bp, url_prefix='/audit', template_folder='/audit/templates')

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth', template_folder='/auth/templates')

    from app.bag import bp as app_bp
    app.register_blueprint(app_bp, url_prefix='/bag', template_folder='/bag/templates')

    from app.key import bp as key_bp
    app.register_blueprint(key_bp, url_prefix='/key', template_folder='/key/templates')

    from app.instance import bp as instance_bp
    app.register_blueprint(instance_bp, url_prefix='/instance', template_folder='/instance/templates')

    from app.keyval import bp as keyval_bp
    app.register_blueprint(keyval_bp, url_prefix='/keyval', template_folder='/keyval/templates')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp, url_prefix='/', template_folder='/main/templates')

    if app.config['LOG_TO_STDOUT']:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
    else:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/bkv.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('bkv startup')
    return app


app = create_app()


from app import models
