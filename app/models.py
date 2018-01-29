from app import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    type = db.Column(db.String(32))

    __mapper__args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type,
    }

    def __repr__(self):
        return '<User {}>'.format(self.email)


class ActivityManager(User):
    __tablename__ = 'activity_manager'
    id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), primary_key=True)
    organisation = db.Column(db.Integer, db.ForeignKey('organisation.id'))

    __mapper_args__ = {
        'polymorphic_identity': 'activity_manager',
    }


class Candidate(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), primary_key=True)
    staff_number = db.Column(db.Integer, unique=True)

    __mapper__args__ = {
        'polymorphic_identity': 'candidate',
    }


class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(1024), index=True, unique=True)
    type = db.Column(db.String(128))

    __mapper_args__ = {
        'polymorphic_identity': 'organisation',
        'polymorphic_on': type,
    }

    def __repr__(self):
        return '<Organisation {}'.format(self.name)


class Department(Organisation):
    id = db.Column(db.Integer, db.ForeignKey('organisation.id'), primary_key=True)
    parent_dept = db.Column(db.String(256))

    __mapper_args__ = {
        'polymorphic_identity': 'department',
    }
