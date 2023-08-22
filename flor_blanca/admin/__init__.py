from flask import Blueprint

bp = Blueprint('admin',__name__)

from flor_blanca.admin import routes