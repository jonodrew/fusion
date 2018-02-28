from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email

from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegisterAsForm(FlaskForm):
    type_of_user = RadioField(label="Please indicate the type of user you are. If you indicate that you are a cohort "
                                    "leader, an email will be sent to your HR team for approval.",
                              choices=[('candidate', 'Fast Streamer'), ('activity manager', 'Activity Manager'),
                                       ('cohort leader', 'Cohort Leader')])
    submit = SubmitField('Next')


class RegistrationForm(FlaskForm):
    first_name = StringField('How would you like to be addressed?')
    last_name = StringField("What's your family name?")
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    @staticmethod
    def validate_email(email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('It looks like you\'re already registered. Have you tried logging in?')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')
