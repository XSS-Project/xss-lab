from flask import Blueprint

bp = Blueprint("dom", __name__)

from app.dom import routes  # noqa: E402, F401
