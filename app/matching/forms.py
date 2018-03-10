from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import NumberRange


class HowManyRandom(FlaskForm):
    number = IntegerField('Please indicate the number of candidates and roles you\'d like to generate', validators=[NumberRange(min=1)])
    submit = SubmitField(label='Create my trial data')
