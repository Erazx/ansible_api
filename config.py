import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guress string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@mail.example.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
    API_SIGN_KEY = "secret_sign_key"
    API_WHITE_IP_LIST = ('127.0.0.1', '192.168.1.1')
    ANSIBLE_PLAYBOOKS_DIR = os.path.join(basedir, 'ansible_playbooks')
    APP_LOG_DIR = os.path.join(basedir, 'logs')
    ANSIBLE_CONTROL_HOST = "192.168.1.101"
    ELK_REDIS_BROKER_HOST = "192.168.1.120"
    ELK_REDIS_BROKER_PORT = 6379
    ELK_MESSAGE_TYPE = 'ansible'
    ELK_LOGSTASH_KEY = 'ansible'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.example.com'
    MAIL_PORT = 25
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'example@example.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your-password-for-email'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig,
}
