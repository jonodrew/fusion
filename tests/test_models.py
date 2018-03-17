from flask import json

from app.models import User, Candidate, Preferences, random_weighted_value


def test_password_hash():
    u = User(email='test_user@data.com')
    u.set_password('cat')
    assert u.check_password('cat')
    assert not u.check_password('cap')


def test_commit_to_db(session):
    u = Candidate(email='random@candidate.com')
    session.add(u)
    session.commit()
    assert 1 == Candidate.query.count()


def test_commit_session(session):
    u = Candidate(email='random2@candidate.com')
    session.add(u)
    session.commit()
    assert 0 < u.id


def test_delete_user_from_db(session):
    u = Candidate(email='random2@candidate.com')
    session.add(u)
    session.commit()
    c = User.query.first()
    session.delete(c)
    session.commit()
    assert 0 == Candidate.query.count()






