from flask import Blueprint

bp = Blueprint('inst', __name__, template_folder='templates')

from app.inst import routes
