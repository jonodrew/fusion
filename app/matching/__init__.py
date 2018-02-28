from flask import Blueprint

bp = Blueprint('matching', __name__)

from app.matching import routes