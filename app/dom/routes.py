"""Navigation scaffold for TV3; no URL-fragment processing yet."""
from flask import render_template

from app.dom import bp


@bp.get("/vulnerable/preview")
def vulnerable_preview():
    return render_template("dom/placeholder.html", version="vulnerable")


@bp.get("/fixed/preview")
def fixed_preview():
    return render_template("dom/placeholder.html", version="fixed")
