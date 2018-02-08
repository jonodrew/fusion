import os

basedir = os.path.abspath((os.path.dirname(__name__)))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "fivefourthreetoone"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "postgresql:///test_local"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Test(Config):
    FLASK_DEBUG = True
