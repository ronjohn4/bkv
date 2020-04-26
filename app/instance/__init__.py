from flask import Blueprint

bp = Blueprint('instance', __name__, template_folder='templates')

from app.instance import routes
