from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, HiddenField
from wtforms.validators import DataRequired


class BagForm(FlaskForm):
    id = HiddenField('id:')
    name = StringField('name:', validators=[DataRequired()])
    desc = StringField('desc:')
    is_active = BooleanField('active:')

    def load(self, data):
        self.id.default = data.id
        self.name.default = data.name
        self.desc.default = data.desc
        self.is_active.default = data.is_active
        self.process()
