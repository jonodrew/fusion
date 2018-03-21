from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import NumberRange, ValidationError


class HowManyRandom(FlaskForm):
    number = IntegerField('Please indicate the number of candidates and roles you\'d like to generate. '
                          'Please don\'t ask for more than 150 data points', validators=[NumberRange(min=1)])
    submit = SubmitField(label='Create my trial data')


    def validate_below_200(self, number):
        if number > 150:
            return ValidationError("That's too much. Try a number lower than 150")