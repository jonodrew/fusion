from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, ValidationError

from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RoleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    organisation = StringField("Name of the organisation offering the role")  # should this be a dropdown?
    context = TextAreaField(
        label="Please give some context for this role. For example, what are the team's objectives? "
              "What is its wider purpose or mission statement?")


class DepartmentalRoleForm(RoleForm):
    clearance = SelectField(label="Clearance required for this role",
                            choices=[("CTC", "Counter-Terrorism Check"), ("DV", "Developed Vetting"),
                                     ("BPSS", "Baseline Personnel Security Standard"), ("SC", "Security check")])
    private_office = BooleanField(label="This is a Private Office post")
    submit = SubmitField('Submit post for validation')


class RegisterAsForm(FlaskForm):
    type_of_user = SelectField(label="Please indicate the type of user you are. If you indicate that you are a cohort "
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

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('It looks like you\'re already registered. Have you tried logging in?')
