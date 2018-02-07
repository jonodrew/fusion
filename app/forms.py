from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, RadioField
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
                            choices=[("BPSS", "Baseline Personnel Security Standard"),
                                     ("CTC", "Counter-Terrorism Check"), ("SC", "Security check"),
                                     ("DV", "Developed Vetting")])
    private_office = BooleanField(label="This is a Private Office post")
    submit = SubmitField('Submit post for validation')


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

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('It looks like you\'re already registered. Have you tried logging in?')


class PreferencesForm(FlaskForm):
    from tests.conftest import skills
    skills_list = list(zip(skills, skills))
    skill1 = SelectField(label="Your first skill preference", choices=skills_list)
    skill2 = SelectField(label="Your second skill preference. Please do not choose the same skill as above.",
                         choices=skills_list)
    private_office = BooleanField(label="I'd like a Private Office role")
    submit = SubmitField("Register my preferences")
    # TODO: Skills should not be the same

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        result = True
        seen = set()
        for field in [self.skill1, self.skill2]:
            print(field.data)
            if field.data in seen:
                field.errors.append('Please select two different skills.')
                result = False
            else:
                seen.add(field.data)
        return result
