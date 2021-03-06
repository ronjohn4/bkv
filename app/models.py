# https://flask-migrate.readthedocs.io/
# make sure db is not open in editor
# make sure db is not in use by the bag

# one time creation of the migrations folder
#   flask db init

# commit current changes to the model and build the migration script
#   flask db migrate -m "comment"  #double quotes

# execute the migration script
#   flask db upgrade

# Good article on cascade
# https://dev.to/zchtodd/sqlalchemy-cascading-deletes-8hk
# alembic doesn't handle alter on MySQL, need to delete and rebuild


from flask import current_app, url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from datetime import datetime, timedelta
from hashlib import md5
import jwt
from time import time
import os
from sqlalchemy.orm import sessionmaker, relationship


class Bag(db.Model):
    __tablename__ = 'bag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    desc = db.Column(db.String(128))
    is_active = db.Column(db.Boolean)
    instances = relationship("Instance", cascade="all, delete", passive_deletes=True)
    keys = relationship("Key", cascade="all, delete", passive_deletes=True)

    def __repr__(self):
        return '<Bag {}>'.format(self.name)

    def to_dict(self):
        data = {
            "id": self.id,
            "name": self.name,
            "desc": self.desc,
            "is_active": self.is_active
        }
        return data


class Instance(db.Model):
    __tablename__ = 'instance'

    id = db.Column(db.Integer, primary_key=True)
    bag_id = db.Column(db.Integer, db.ForeignKey('bag.id', ondelete="cascade"))
    name = db.Column(db.String(64))
    desc = db.Column(db.String(128))
    is_active = db.Column(db.Boolean)
    keyvals = relationship("Keyval", cascade="all, delete", passive_deletes=True)

    def __repr__(self):
        return '<Instance {}>'.format(self.name)

    def to_dict(self):
        data = {
            "id": self.id,
            "bag_id": self.bag_id,
            "name": self.name,
            "desc": self.desc,
            "is_active": self.is_active
        }
        return data


class Key(db.Model):
    __tablename__ = 'key'

    id = db.Column(db.Integer, primary_key=True)
    bag_id = db.Column(db.Integer, db.ForeignKey('bag.id', ondelete="cascade"))
    name = db.Column(db.String(64))
    desc = db.Column(db.String(128))
    is_active = db.Column(db.Boolean)
    keyvals = relationship("Keyval", cascade="all, delete", passive_deletes=True)

    def __repr__(self):
        return '<Key {}>'.format(self.name)

    def to_dict(self):
        data = {
            "id": self.id,
            "bag_id": self.bag_id,
            "name": self.name,
            "desc": self.desc,
            "is_active": self.is_active
        }
        return data


class Keyval(db.Model):
    __tablename__ = 'keyval'

    id = db.Column(db.Integer, primary_key=True)
    instance_id = db.Column(db.Integer, db.ForeignKey('instance.id', ondelete="cascade"))
    key_id = db.Column(db.Integer, db.ForeignKey('key.id', ondelete="cascade"))
    val = db.Column(db.String(120))
    is_active = db.Column(db.Boolean)
    last_loaded = db.Column(db.DateTime)
    last_changed = db.Column(db.DateTime)
    is_dirty = db.Column(db.Boolean)
    count_loaded = db.Column(db.Integer)
    count_changed = db.Column(db.Integer)

    def __repr__(self):
        return '<Keyval {}>'.format(self.id)

    def to_dict(self):
        data = {
            "id": self.id,
            "instance_id": self.instance_id,
            "key_id": self.key_id,
            "val": self.val,
            "is_active": self.is_active,
            "last_loaded": self.last_loaded,
            "last_changed": self.last_changed,
            "is_dirty":  self.is_dirty,
            "count_loaded": self.count_loaded,
            "count_changed": self.count_changed
        }
        return data


# parent_id is not a foreign key so can be used by multiple models
class Audit(db.Model):
    __tablename__ = 'audit'

    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(64))
    parent_id = db.Column(db.Integer)
    a_datetime = db.Column(db.DateTime)
    a_user_id = db.Column(db.Integer)
    a_username = db.Column(db.String(64))
    action = db.Column(db.String(64))
    before = db.Column(db.String)
    after = db.Column(db.String)

    def __repr__(self):
        return '<Audit {}>'.format(self.datetime)


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'last_seen': self.last_seen.isoformat() + 'Z',
            'about_me': self.about_me,
            'post_count': self.posts.count(),
            'follower_count': self.followers.count(),
            'followed_count': self.followed.count(),
            '_links': {
                'self': url_for('api.get_user', id=self.id),
                'followers': url_for('api.get_followers', id=self.id),
                'followed': url_for('api.get_followed', id=self.id),
                'avatar': self.avatar(128)
            }
        }
        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
