from flask import Blueprint

bp = Blueprint('questions',__name__)

from flor_blanca.questions import routes