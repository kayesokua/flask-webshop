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
    TWILIO_ACCOUNT_SID = environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_SERVICE = environ.get('TWILIO_SERVICE')

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI_DEV')
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    STRIPE_SECRET_KEY = environ.get('STRIPE_SECRET_KEY_DEV')
    STRIPE_PUBLISHABLE_KEY = environ.get('STRIPE_PUBLISHABLE_KEY_DEV')
    STRIPE_ENDPOINT_SECRET = environ.get('STRIPE_ENDPOINT_SECRET_DEV')
    TWILIO_ACCOUNT_SID = environ.get('TWILIO_ACCOUNT_SID_DEV')
    TWILIO_AUTH_TOKEN = environ.get('TWILIO_AUTH_TOKEN_DEV')
    TWILIO_SERVICE = environ.get('TWILIO_SERVICE_DEV')

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    STRIPE_SECRET_KEY = environ.get('STRIPE_SECRET_KEY_TEST')
    STRIPE_PUBLISHABLE_KEY = environ.get('STRIPE_PUBLISHABLE_KEY_TEST')
    STRIPE_ENDPOINT_SECRET = environ.get('STRIPE_ENDPOINT_SECRET_TEST')
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI_TEST')
    TWILIO_ACCOUNT_SID = environ.get('TWILIO_ACCOUNT_SID_TEST')
    TWILIO_AUTH_TOKEN = environ.get('TWILIO_AUTH_TOKEN_TEST')
    TWILIO_SERVICE = environ.get('TWILIO_SERVICE_TEST')