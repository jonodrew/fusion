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
from flask import current_app, json


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


Base = declarative_base()


def random_between_one_hundred():
    return random.randint(0, 100)


def random_weighted_value(random_integer, weighted_values_dict: Dict[int, int]) -> int:
    for value in weighted_values_dict:
        if random_integer <= value:
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
            db.session.commit()
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
    id = db.Column(None, db.ForeignKey('users.id'), primary_key=True)
    staff_number = db.Column(db.Integer, unique=True)
    line_manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    able_to_relocate = db.Column(db.Boolean, default=True)
    region_id = db.Column(db.ForeignKey('regions.id'))

    line_manager = db.relationship("User", foreign_keys=[line_manager_id])
    preferences = db.relationship('Preferences', backref='owner', lazy='dynamic', cascade='all, delete')
    specialism = db.relationship('Specialism', lazy='select', backref='specialist')
    region = db.relationship('Region', lazy='select')

    @declared_attr
    def specialism_id(cls):
        return User.__table__.c.get('specialism', db.Column(db.ForeignKey('specialisms.id')))

    __mapper_args__ = {
        'polymorphic_identity': 'candidate',
        'inherit_condition': id == User.id
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
    def specialism_id(cls):
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
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisation.id'))
    description = db.Column(db.Text)
    specialism_id = db.Column(db.ForeignKey('specialisms.id'))
    responsibilities = db.Column(db.Text)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'))
    private_office = db.Column(db.Boolean, default=False)
    skills = db.Column(db.JSON())

    specialism = db.relationship('Specialism', lazy='select', backref='specialist_roles')
    organisation = db.relationship('Organisation', lazy='select')
    region = db.relationship('Region', lazy='select')

    def wanted_skills(self):
        """This function takes the JSON formatted text from the column for this preference form and compares it with
        the skills in the Skill table. It returns the name of the matching skill. This is for formatting and output
        purposes - analysing equality or comparisons is done with integers for speed."""
        skills_dict = json.loads(self.skills)
        specialism_id = self.specialism.id
        skill_id_and_name = dict(
            Skill.query.with_entities(Skill.id, Skill.description).filter(Skill.specialism == specialism_id). \
            all())
        return [skill_id_and_name[skill] for preference, skill in skills_dict.items()]


class Preferences(db.Model, Base):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.ForeignKey('users.id'))
    open_date = db.Column(db.DateTime())
    close_date = db.Column(db.DateTime())
    completed_date = db.Column(db.DateTime())
    completed = db.Column(db.Boolean(), default=False)
    skills = db.Column(db.JSON())  # using JSON for now because I don't know how many skills will be in table
    want_private_office = db.Column(db.Boolean())
    location = db.Column(db.String(64))
    organisation = db.Column(db.JSON())
    url = db.Column(db.String(64), default='main.submit_preferences')

    def has_form_to_complete(self, cid):
        form = Preferences.query.filter(self.candidate_id == cid, self.completed == False).all()
        return form

    def wanted_skills(self):
        """This function takes the JSON formatted text from the column for this preference form and compares it with
        the skills in the Skill table. It returns the name of the matching skill. This is for formatting and output
        purposes - analysing equality or comparisons is done with integers for speed."""
        skills_dict = json.loads(self.skills)
        specialism_id = self.owner.specialism.id
        skill_id_and_name = dict(
            Skill.query.with_entities(Skill.id, Skill.description).filter(Skill.specialism == specialism_id). \
            all())
        return [skill_id_and_name[skill] for preference, skill in skills_dict.items()]

    def __repr__(self):
        return 'Belongs to Candidate {}'.format(self.owner)


class Specialism(db.Model, Base):
    __tablename__ = 'specialisms'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(28))


class Region(db.Model):
    __tablename__ = 'regions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return 'Region {}'.format(self.name)


class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer(), primary_key=True, index=True)
    specialism = db.Column(db.ForeignKey('specialisms.id'), nullable=True)
    description = db.Column(db.String(128))

    def __repr__(self):
        return 'Skill {}'.format(self.description)


class MatchTable(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.ForeignKey('candidates.id'))
    role_id = db.Column(db.ForeignKey('roles.id'))
    scores = db.Column(db.JSON())
    match_score = db.Column(db.Integer)
#     skill_score = db.Column(db.Integer)
#     location_score = db.Column(db.Integer)
