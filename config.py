import os
import secrets

basedir = os.path.abspath((os.path.dirname(__name__)))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "postgresql://postgres:password@localhost/test_local"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SENDGRID_API_KEY = os.environ.get('SENDGRID_KEY') or "fivefourthreetoone"
    print(SENDGRID_API_KEY)
    SENDGRID_DEFAULT_FROM = 'admin@example.com'
    SECRET_KEY = secrets.token_hex(64)


class Test(Config):
    FLASK_DEBUG = True
