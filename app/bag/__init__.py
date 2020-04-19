from flask import Blueprint

bp = Blueprint('bag', __name__, template_folder='templates')

from app.bag import routes
