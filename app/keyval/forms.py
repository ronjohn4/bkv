from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, HiddenField, DecimalField, SelectField
from wtforms.validators import DataRequired, Email
import dateutil.parser
from app.models import sex


def validate_dob(form, field):
    try:
        dateutil.parser.parse(str(field.data))
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")


class KeyvalForm(FlaskForm):
    id = HiddenField('id:')
    name = StringField('Name:', validators=[DataRequired()])
    email = StringField('Email:', validators=[DataRequired(), Email()])
    # https://en.wikipedia.org/wiki/ISO/IEC_5218
    # pattern for converting a dictionary to choices
    sex = SelectField('Sex', choices=[(str(k), v) for k, v in sorted(sex.items())])
    dob = StringField('DOB:', validators=[validate_dob])
    is_active = BooleanField('Active:')
    income_amount = DecimalField('Income Amount:', places=2)

    def load(self, data):
        self.id.default = data.id
        self.name.default = data.name
        self.email.default = data.email
        self.sex.default = data.sex
        self.dob.default = data.dob
        self.is_active.default = data.is_active
        self.income_amount.default = data.income_amount
        self.process()
