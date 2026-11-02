"""Navigation scaffold for TV2; no storage or POST handlers yet."""
from flask import render_template

from app.stored import bp


@bp.get("/vulnerable/comments")
def vulnerable_comments():
    return render_template("stored/placeholder.html", version="vulnerable")


@bp.get("/fixed/comments")
def fixed_comments():
    return render_template("stored/placeholder.html", version="fixed")
