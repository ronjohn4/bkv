from flask import Blueprint

bp = Blueprint('key', __name__, template_folder='templates')

from app.key import routes
