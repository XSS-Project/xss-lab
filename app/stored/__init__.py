from flask import Blueprint

bp = Blueprint("stored", __name__)

from app.stored import routes  # noqa: E402, F401
