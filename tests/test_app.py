from flask import current_app

def test_config(app):
    assert 'sqlite:///test_project.db' == current_app.config['SQLALCHEMY_DATABASE_URI']