from sqlalchemy.ext.declarative import declarative_base
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


Base = declarative_base()


class User(db.Model, UserMixin, Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    type = db.Column(db.String(24), nullable=False)

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


class ActivityManager(User):
    __tablename__ = 'activity_manager'
    __mapper_args__ = {
        'polymorphic_identity': 'activity manager',
    }
    id = db.Column(None, db.ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    organisation = db.Column(db.Integer, db.ForeignKey('organisation.id'))


class Candidate(User):
    __tablename__ = 'candidate'
    id = db.Column(None, db.ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    staff_number = db.Column(db.Integer, unique=True)

    __mapper_args__ = {
        'polymorphic_identity': 'candidate'
    }


class Organisation(db.Model):
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
    id = db.Column(db.Integer, db.ForeignKey('organisation.id'), primary_key=True)
    parent_dept = db.Column(db.String(256))

    __mapper_args__ = {
        'polymorphic_identity': 'department'
    }





class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organisation = db.Column(db.Integer, db.ForeignKey('organisation.id'))
    description = db.Column(db.Text)
    responsibilities = db.Column(db.Text)
    # region = db.Column(db.Integer, db.ForeignKey('region.id'))

