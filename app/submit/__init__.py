from flask import Blueprint

bp = Blueprint('submit', __name__)

from app.submit import routes