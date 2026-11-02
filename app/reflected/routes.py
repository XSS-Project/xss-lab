"""Navigation scaffold only; TV1 implements search in the next stage."""
from flask import render_template

from app.reflected import bp


@bp.get("/vulnerable/search")
def vulnerable_search():
    return render_template("reflected/placeholder.html", version="vulnerable")


@bp.get("/fixed/search")
def fixed_search():
    return render_template("reflected/placeholder.html", version="fixed")
