import datetime
import random
import statistics
from typing import Dict, List, Any, Union, Set, Tuple

import munkres
import sys
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
    want_private_office = db.Column(db.Boolean(), default=False)
    locations = db.Column(db.JSON())
    organisation = db.Column(db.JSON())
    url = db.Column(db.String(64), default='main.submit_preferences')

    def has_form_to_complete(self, cid):
        form = Preferences.query.filter(self.candidate_id == cid, self.completed == False).all()
        return form

    def wanted_skills(self) -> List[str]:
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


class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.ForeignKey('candidates.id'))
    role_id = db.Column(db.ForeignKey('roles.id'))
    scores = db.Column(db.JSON())
    total = db.Column(db.Integer)
    suggested = db.Column(db.Boolean, default=False)

    weights_dict = {'location': 5, 'skills': 10, 'private office': 10, 'organisation': 5}

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
        return value_to_check in dict_to_check.values()

    @staticmethod
    def count_overlap_of_dicts(dict_a: Dict[Any, Any], dict_b: Dict[Any, Any]) -> int:
        a = [a for a in dict_a.values()]
        b = [b for b in dict_b.values()]
        set_a = set(a)
        set_b = set(b)
        return len(set_a.intersection(set_b))

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
            output = self.role.region_id == self.candidate.region_id
            """return True if the role's region is the same as their current region"""
        else:  # candidate can relocate
            wanted_regions = json.loads(self.candidate.preferences.first().locations)
            output = self.check_x_in_y_dict(wanted_regions, self.role.region_id)
            """return True if the role's region is in the candidate's preferred regions"""
        return output

    def organisation_check(self) -> bool:
        wanted_orgs = json.loads(self.candidate.preferences.first().organisation)
        return self.check_x_in_y_dict(wanted_orgs, self.role.organisation)

    def __init__(self, role_object: Role = None, candidate_object: Candidate = None,
                 weights_dict: Dict[str, int]=weights_dict) -> None:
        self.role = role_object
        self.candidate = candidate_object
        self.candidate_id = self.candidate.id
        self.role_id = self.role.id
        self.weights_dict = weights_dict
        self.boolean_scores = self.create_scores()
        self.weighted_scores = self.apply_weighting()
        self.scores = json.dumps(self.weighted_scores)
        self.total = self.calculate_total()

    def create_scores(self):
        po_match = self.boolean_implication(self.candidate.preferences.first().want_private_office,
                                            self.role.private_office)
        location_match = self.suitable_location_check()
        skills_match = self.count_overlap_of_dicts(json.loads(self.role.skills),
                                                        json.loads(self.candidate.preferences.first().skills))
        organisation_match = self.organisation_check()
        return {'location': location_match, 'private office': po_match,
                             'skills': skills_match, 'organisation': organisation_match}

    def calculate_total(self):
        return self.create_match_score(self.weighted_scores)

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

    def apply_weighting(self) -> Dict[str, int]:
        return {k: self.boolean_scores[k] * self.weights_dict[k] for k in self.boolean_scores}


class Algorithm:
    def __init__(self, candidate_ids: List[int], role_ids: List[int], weighted_dict: Dict[str, int]=None):
        if weighted_dict is None:
            self.weighted_dict = {'location': 15, 'skills': 20, 'private office': 15, 'organisation': 10}
        else:
            self.weighted_dict = weighted_dict
        self.candidate_ids = candidate_ids
        self.role_ids = role_ids

    def process(self):
        candidates = self.filtered_list_of_table_objects(Candidate, self.candidate_ids)
        roles = self.filtered_list_of_table_objects(Role, self.role_ids)
        matches = [Match(r, c, self.weighted_dict) for r in roles for c in candidates]
        tables = self.prepare_data_for_munkres(matches)
        munkres_object = munkres.Munkres()
        table_of_objects = tables[0]
        table_of_totals = tables[1]
        best_match_indices = munkres_object.compute(table_of_totals)
        best_matches = [table_of_objects[row][column] for row, column in best_match_indices]
        aggregate = sum([m.total for m in best_matches])
        totals = [m.total for m in best_matches]
        median_average = "{:.1%}".format(statistics.median(totals) / 100)
        db.session.add_all(matches)
        db.session.commit()

    @staticmethod
    def filtered_list_of_table_objects(table_object, filter_list) -> List[Union[Candidate, Role]]:
        return table_object.query.filter(table_object.id.in_(filter_list)).all()

    def prepare_data_for_munkres(self, match_list: List[Match]):
        match_list.sort(key=lambda x: x.role_id)
        table_of_matches = [match_list[i:i + len(self.candidate_ids)] for i in range(0, len(match_list),
                                                                                     len(self.candidate_ids))]
        table_of_totals = [[sys.maxsize - m.total for m in row] for row in table_of_matches]
        return table_of_matches, table_of_totals

    def mark_suggested_matches(self, suggested_match_indices: List[Tuple[int, int]],
                               list_of_list_of_objects: List[List[Match]]) -> List[List[Match]]:
        suggested_matches = [list_of_list_of_objects[row][column] for row, column in suggested_match_indices]
        for match in suggested_matches:
            match.suggested = True
        return list_of_list_of_objects


