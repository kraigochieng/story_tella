from flask import Blueprint

summary = Blueprint("summary", __name__, template_folder="templates")

from . import routes
