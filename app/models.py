from app import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    type = db.Column(db.String(32))

    __mapper__args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': 'type'
    }

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(1024), index=True, unique=True)

    def __repr__(self):
        return '<Department {}'.format(self.name)


class ActivityManager(User):
    __tablename__ = 'activity_manager'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    department = db.Column(db.Integer, db.ForeignKey('department.id'))

    __mapper_args__ = {
        'polymorphic_identity': 'activity_manager',
    }