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
    locations = db.Column(db.JSON())
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

    def wanted_organisations(self):
        """This function examines the 'wanted organisations' stored as integers in JSON code and returns their names
        for display"""
        orgs_dict = json.loads(self.organisation)
        organisation_id_and_name = dict(
            Organisation.query.with_entities(Organisation.id, Organisation.name).all()
        )
        return [organisation_id_and_name[org] for preference, org in orgs_dict.items()]

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

    weights_dict = {'anchor': 10, 'location': 2, 'skills': 5, 'department': 2}

    @staticmethod
    def check_if_equal(p_attribute: str, fs_attribute: str) -> int:
        """
        Compare two attributes. If they're equal, return True, otherwise return False.
        Args:
            p_attribute (str): some attribute of the post
            fs_attribute (str): some attribute of the FastStreamer

        Returns:
            int: the value of the match of the two attributes

        """
        return p_attribute == fs_attribute

    @staticmethod
    def create_match_score(scores: Dict[str, int]) -> int:
        """
        This method returns the sum of all the scores, passed as a dictionary
        Args:
            scores:

        Returns:

        """
        return sum([scores[k] for k in scores])

    @staticmethod
    def check_x_in_y_list(list_to_check: List[Any], value_to_check) -> bool:
        try:
            r = value_to_check in set(list_to_check)
        except TypeError:
            r = True
        return r

    @staticmethod
    def check_x_in_y_dict(dict_to_check: Dict[Any, Any], value_to_check) -> bool:
        return value_to_check in [v for k, v in dict_to_check.items()]

    @staticmethod
    def convert_clearances(clearance: str) -> int:
        """
        This function converts a clearance level as a string to an int for comparison
        Args:
            clearance: string representing clearance level

        Returns:
            int

        """
        c = {'SC': 3, 'DV': 4, 'CTC': 2, 'BPSS': 1}
        return c[clearance]

    @staticmethod
    def boolean_implication(a: bool, b: bool) -> bool:
        return (not a) or b

    @staticmethod
    def check_any_item_from_list_a_in_list_b(a: Union[List[str], Set], b: List) -> bool:
        return bool(set(a).intersection(set(b)))

    def suitable_location_check(self) -> bool:
        """
        Checks if FS has location restriction: if so, returns True if it's the location the FS wants, if not, returns
        False
        @return: bool
       """
        if not self.candidate.able_to_relocate:  # if the candidate cannot relocate
            return self.role.region_id == self.candidate.region_id  #
            """return True if the role's region is the same as their current region"""
        return (not self.candidate.able_to_relocate) or self.check_x_in_y_list(
            self.candidate.preferences.first().location, self.role.location)

    def __init__(self, role_object: Role = None, candidate_object: Candidate = None) -> None:
        self.role = role_object
        self.candidate = candidate_object
        self.candidate_id = self.candidate.id
        self.role_id = self.role.id
        self.po_match = self.boolean_implication(self.role.is_private_office,
                                                 self.candidate.preferences.first().wants_private_office)
        # self.reserved_match = self.boolean_implication(self.post.reserved, self.fast_streamer.national)
        # self.clearance_match = self.compare_clearance()
        self.suitable_location = self.suitable_location_check()
        if not (self.clearance_match and self.po_match and self.reserved_match and self.suitable_location):
            self.total = 0
            self.weighted_scores = {'anchor': 0, 'location': 0, 'skills': 0, 'department': 0}
            # this approach massively improves speed when generating the matrix, but also means that the match cannot
            # later be examined for how good or bad it was
        else:
            self.anchor_match = self.check_x_in_y_dict(self.fast_streamer.preferences.anchors, self.post.anchor)
            self.location_match = self.check_x_in_y_list(self.fast_streamer.preferences.locations, self.post.location)
            self.skills_match = self.check_any_item_from_list_a_in_list_b(self.post.skills,
                                                                          self.fast_streamer.preferences.skills)
            self.department_match = self.check_any_item_from_list_a_in_list_b(self.post.department,
                                                                              self.fast_streamer.preferences.departments)
            self.match_scores = {'anchor': self.anchor_match, 'location': self.location_match,
                                 'skills': self.skills_match, 'department': self.department_match}
            self.weighted_scores = self.apply_weighting(weighting_dict=MatchTable.weights_dict)
            self.total = self.create_match_score(self.weighted_scores)

    def compare_clearance(self) -> bool:
        """
        Compares FastStreamer's clearance and Post clearance. Returns True if FastStreamer clearance is greater than
        or equal to Post clearance returns True, else returns False

        Returns:
            bool

        """
        post_c = self.convert_clearances(self.post.clearance)
        fs_c = self.convert_clearances(self.fast_streamer.clearance)
        if self.post.clearance == 'DV' and self.fast_streamer.preferences.will_undertake_dv is True:
            r = True
        else:
            r = post_c <= fs_c
        return r

    def compare_private_office(self) -> bool:
        return (not self.post.is_private_office) or self.fast_streamer.preferences.wants_private_office

    def apply_weighting(self, weighting_dict: Dict[str, int]) -> Dict[str, int]:
        return {k: self.match_scores[k] * weighting_dict[k] for k in self.match_scores}
#     skill_score = db.Column(db.Integer)
#     location_score = db.Column(db.Integer)
