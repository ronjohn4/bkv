from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, HiddenField
from wtforms.validators import DataRequired


class KeyForm(FlaskForm):
    id = HiddenField('id:')
    bag_id = HiddenField('bag_id:')
    name = StringField('name:', validators=[DataRequired()])
    desc = StringField('desc:')
    is_active = BooleanField('active:')

    def load(self, data):
        self.id.default = data.id
        self.bag_id.default = data.bag_id
        self.name.default = data.name
        self.desc.default = data.desc
        self.is_active.default = data.is_active
        self.process()
