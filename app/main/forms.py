from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired

departments = ['HO', 'DWP', 'HMRC', 'DH', 'CO', 'GDS', 'MOD', 'DDCMS', 'DCLG', 'DEFRA', 'MOJ', 'DFT', 'DFE', 'DFID']
skills = ['Software Engineering', 'User Research', 'Strategy & Policy', 'Product Design', 'Content & Analysis',
          'Delivery', 'Operations', 'Commercial Management']
anchors = ['Digital', 'Corporate', 'Operations']
locations = ['London', 'South West', 'Midlands', 'Scotland', 'The North', 'Overseas']
clearances = ['BPSS', 'CTC', 'SC', 'DV']

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
