from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, validators
from wtforms.validators import NumberRange, ValidationError


class ClearanceForm(FlaskForm):
    pass


class RoleTitleForm(FlaskForm):
    role_title = StringField('Full Name', [validators.required(), validators.length(max=10)])
