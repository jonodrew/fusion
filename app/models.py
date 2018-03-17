import datetime
import random
from typing import Dict, List, Any, Union, Set

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from app import login, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
import jwt
from . import db as database
from flask import current_app


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


Base = declarative_base()


def random_between_one_hundred():
    return random.randint(0, 100)


def random_weighted_value(random_integer, weighted_values_dict: Dict[float, str]) -> str:
    for value in weighted_values_dict:
        if random_integer < value:
            return weighted_values_dict[value]


class User(db.Model, UserMixin, Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    type = db.Column(db.String(24), nullable=False)
    confirmed = db.Column(db.Boolean, default=False, nullable=False)

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'user'
    }

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    def generate_token(self, redirect: str, expiration=3600):
        return jwt.encode(
            {redirect: self.id, 'exp': time() + expiration},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def set_confirmed(self) -> None:
        self.confirmed = True

    @staticmethod
    def validate_token(token: str, redirect: str):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])[redirect]
        except:
            return None
        return User.query.get(id)

    def confirm_user(self, token: str):
        u = User.validate_token(token, 'confirm_email')
        if u.id == self.id:
            self.set_confirmed()
            database.session.add(self)
            database.session.commit()
            return True
        else:
            print('Error')
        return None

    def create_random(self):
        return User()


class ActivityManager(User):
    __tablename__ = 'activity_managers'
    __mapper_args__ = {
        'polymorphic_identity': 'activity manager',
    }
    # id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    organisation = db.Column(db.Integer, db.ForeignKey('organisation.id'))


class Candidate(User):
    __tablename__ = 'candidates'
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False, unique=True)
    staff_number = db.Column(db.Integer, unique=True)
    line_manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    line_manager = db.relationship("User", foreign_keys=[line_manager_id])
    preference_forms = db.relationship('Preferences', backref='owner', lazy='dynamic')

    @declared_attr
    def specialism(cls):
        return User.__table__.c.get('specialism', db.Column(db.ForeignKey('specialisms.id')))

    __mapper_args__ = {
        'polymorphic_identity': 'candidate'
    }

    def get_open_forms(self):
        return self.preference_forms.filter(Preferences.close_date >= datetime.datetime.today(),
                                                  Preferences.completed == False).all()


class CohortLeader(User):
    __tablename__ = 'cohort_leaders'
    # id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'cohort_leader'
    }

    def get_cohort(self):
        return Candidate.query.filter(Candidate.line_manager_id == self.id).all()


class SchemeLeader(User):
    __tablename__ = 'scheme_leaders'
    # id = db.Column(None, db.ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)

    @declared_attr
    def specialism(cls):
        return User.__table__.c.get('specialism', db.Column(db.ForeignKey('specialisms.id')))

    __mapper_args__ = {
        'polymorphic_identity': 'scheme_leader'
    }


class Organisation(db.Model, Base):
    __tablename__ = 'organisation'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(1024), index=True, unique=True)
    type = db.Column(db.String(128))

    __mapper_args__ = {
        'polymorphic_identity': 'organisation',
        'polymorphic_on': type
    }

    def __repr__(self):
        return '<Organisation {}'.format(self.name)


class Department(Organisation):
    # id = db.Column(db.Integer, db.ForeignKey('organisation.id'), primary_key=True)
    parent_dept = db.Column(db.String(256))

    __mapper_args__ = {
        'polymorphic_identity': 'department'
    }


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    organisation = db.Column(db.Integer, db.ForeignKey('organisation.id'))
    description = db.Column(db.Text)
    responsibilities = db.Column(db.Text)
    region = db.Column(db.Integer, db.ForeignKey('regions.id'))


class Preferences(db.Model, Base):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.ForeignKey('users.id'))
    open_date = db.Column(db.DateTime())
    close_date = db.Column(db.DateTime())
    completed_date = db.Column(db.DateTime())
    completed = db.Column(db.Boolean(), default=False)
    skills = db.Column(db.JSON())
    want_private_office = db.Column(db.Boolean())
    location = db.Column(db.String(64))
    department = db.Column(db.JSON())
    url = db.Column(db.String(64), default='main.submit_preferences')

    def has_form_to_complete(self, cid):
        form = Preferences.query.filter(self.candidate_id == cid, self.completed == False).all()
        return form


class Specialism(db.Model, Base):
    __tablename__ = 'specialisms'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(28))


class Region(db.Model):
    __tablename__ = 'regions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))


# class MatchTable(db.Model):
#     __tablename__ = 'matches'
#     id = db.Column(db.Integer, primary_key=True)
#     candidate_id = db.Column(db.ForeignKey('candidates.user_id'))
#     role_id = db.Column(db.ForeignKey('roles.id'))
#     match_score = db.Column(db.Integer)
#     skill_score = db.Column(db.Integer)
#     location_score = db.Column(db.Integer)


