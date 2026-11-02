from html import escape

import pytest
from markupsafe import escape as jinja_escape

from app.main.data import CATEGORIES, DOCUMENTS


def test_document_list_has_all_samples(client):
    response = client.get("/documents")
    assert len(DOCUMENTS) >= 6
    assert len({item["id"] for item in DOCUMENTS}) == len(DOCUMENTS)
    assert response.text.count('class="document-card"') == len(DOCUMENTS)
    assert f"<strong>{len(DOCUMENTS)}</strong> tài liệu phù hợp" in response.text
    for document in DOCUMENTS:
        assert document["title"] in response.text
        assert set(document) == {"id", "title", "category", "description", "content"}


@pytest.mark.parametrize("category", CATEGORIES)
def test_category_filter(client, category):
    response = client.get("/documents", query_string={"category": category})
    assert response.status_code == 200
    matching = [item for item in DOCUMENTS if item["category"] == category]
    assert response.text.count('class="document-card"') == len(matching)
    for document in DOCUMENTS:
        assert (document["title"] in response.text) == (document["category"] == category)


def test_unknown_category_is_empty(client):
    response = client.get("/documents", query_string={"category": "Chưa có danh mục"})
    assert response.status_code == 200
    assert "Không tìm thấy tài liệu" in response.text
    assert "Bỏ lọc danh mục" in response.text
    assert '<strong>0</strong> tài liệu phù hợp' in response.text
    assert 'class="document-card"' not in response.text


def test_empty_category_shows_all_documents(client):
    assert client.get("/documents?category=").text.count('class="document-card"') == len(DOCUMENTS)


def test_filter_value_is_escaped(client):
    category = '<em data-marker="sample">Tiếng Việt & tài liệu</em>'
    response = client.get("/documents", query_string={"category": category})
    assert response.status_code == 200
    assert category not in response.text
    assert str(jinja_escape(category)) in response.text


@pytest.mark.parametrize("document", DOCUMENTS, ids=lambda item: str(item["id"]))
def test_document_detail(client, document):
    response = client.get(f'/documents/{document["id"]}')
    assert response.status_code == 200
    assert document["title"] in response.text
    assert document["description"] in response.text
    assert escape(document["content"], quote=False) in response.text
    assert "Chưa triển khai" in response.text
    assert '<form' not in response.text


@pytest.mark.parametrize("document_id", [0, 999999])
def test_missing_document_returns_404(client, document_id):
    assert client.get(f"/documents/{document_id}").status_code == 404
