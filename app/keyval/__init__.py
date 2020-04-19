from flask import Blueprint

bp = Blueprint('keyval', __name__, template_folder='templates')

from app.keyval import routes
