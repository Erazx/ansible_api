from flask import Flask
from celery import Celery
# from flask_mail import Mail
from config import config, Config
from werkzeug.contrib.fixers import ProxyFix
from logconfig.logconfig import init_logging


# mail = Mail()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # mail.init_app(app)
    init_logging(app.config['APP_LOG_DIR'])
    app.wsgi_app = ProxyFix(app.wsgi_app)
    celery.conf.update(app.config)

    # routes and errorhandlers 
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
