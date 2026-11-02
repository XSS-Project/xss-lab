from flask import abort, render_template, request

from app.main import bp
from app.main.data import CATEGORIES, DOCUMENTS, get_document


@bp.get("/")
def index():
    return render_template("main/index.html", documents=DOCUMENTS[:3])


@bp.get("/documents")
def documents():
    category = request.args.get("category", "")
    items = [item for item in DOCUMENTS if not category or item["category"] == category]
    return render_template(
        "main/documents.html", documents=items, categories=CATEGORIES,
        selected_category=category,
    )


@bp.get("/documents/<int:document_id>")
def document_detail(document_id):
    document = get_document(document_id)
    if document is None:
        abort(404)
    return render_template("main/document_detail.html", document=document)


@bp.get("/guide")
def guide():
    return render_template("main/guide.html")
