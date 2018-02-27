from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, RadioField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email

from app.models import User


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
