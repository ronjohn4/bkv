from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, HiddenField


class KeyvalForm(FlaskForm):
    id = HiddenField('id:')
    instance_id = HiddenField('instance_id:')
    key_id = HiddenField('key_id:')
    val = StringField('value:')
    is_active = BooleanField('active:')

    def load(self, data):
        self.id.default = data.id
        self.instance_id.default = data.instance_id
        self.key_id.default = data.key_id
        self.val.default = data.val
        self.is_active.default = data.is_active
        self.process()
