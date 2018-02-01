from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RoleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    organisation = StringField("Name of the organisation offering the role")  # should this be a dropdown?
    submit = SubmitField('Submit post for validation')


class DepartmentalRoleForm(RoleForm):
    clearance = SelectField(label="Clearance required for this role",
                            choices=[("CTC", "Counter-Terrorism Check"), ("DV", "Developed Vetting"),
                                     ("BPSS", "Baseline Personnel Security Standard"), ("SC", "Security check")])
    private_office = BooleanField(label="Is this a Private Office post?")
