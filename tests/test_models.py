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


def test_random_weighted_value():
    r = 9
    f = 89
    weighted_dict = {10: 'True', 90: 'False'}
    assert 'True' == random_weighted_value(r, weighted_dict)
    assert 'False' == random_weighted_value(f, weighted_dict)


def test_create_random_preferences():
    weighted_dict = {'skills': {20: 1, 50: 2, 100: 3}}
    preferences_list = [Preferences.create_random(i, weighted_dict) for i in range(0, 100)] # only one skill per candidate for now
    count_dictionary = {1: 0, 2: 0, 3: 0}
    for p in preferences_list:
        skills = json.loads(p.skills)
        count_dictionary[skills['1']] += 1
    assert count_dictionary[1] <= 25
    assert count_dictionary[2] <= 35
    assert count_dictionary[3] <= 55
