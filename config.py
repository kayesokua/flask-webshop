from os import environ, path
from dotenv import load_dotenv
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config():
    SECRET_KEY = environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    pass

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    WTF_CSRF_ENABLED = True
    STRIPE_SECRET_KEY = environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_ENDPOINT_SECRET = environ.get('STRIPE_ENDPOINT_SECRET')
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI_DEV')
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    STRIPE_SECRET_KEY = environ.get('STRIPE_SECRET_KEY_DEV')
    STRIPE_PUBLISHABLE_KEY = environ.get('STRIPE_PUBLISHABLE_KEY_DEV')
    STRIPE_ENDPOINT_SECRET = environ.get('STRIPE_ENDPOINT_SECRET_DEV')

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    STRIPE_SECRET_KEY = environ.get('STRIPE_SECRET_KEY_TEST')
    STRIPE_PUBLISHABLE_KEY = environ.get('STRIPE_PUBLISHABLE_KEY_TEST')
    STRIPE_ENDPOINT_SECRET = environ.get('STRIPE_ENDPOINT_SECRET_TEST')
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI_TEST')