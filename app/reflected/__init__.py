from flask import Blueprint

bp = Blueprint("reflected", __name__)

from app.reflected import routes  # noqa: E402, F401
