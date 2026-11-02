from html.parser import HTMLParser
from urllib.parse import urlsplit

import pytest


MODULE_PATHS = (
    "/vulnerable/search", "/fixed/search", "/vulnerable/comments",
    "/fixed/comments", "/vulnerable/preview", "/fixed/preview",
)


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        key = "href" if tag in {"a", "link"} else "src" if tag == "script" else None
        value = attributes.get(key, "")
        if value.startswith("/"):
            parts = urlsplit(value)
            self.urls.add(parts.path + (f"?{parts.query}" if parts.query else ""))


@pytest.mark.parametrize("path", ["/", "/guide", "/documents", "/documents/1"])
def test_foundation_pages(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert '<html lang="vi">' in response.text
    assert 'id="main-content"' in response.text


def test_home_links_to_all_modules(client):
    parser = LocalLinks()
    parser.feed(client.get("/").text)
    assert set(MODULE_PATHS) <= parser.urls


@pytest.mark.parametrize("path", ["/", "/guide", "/documents", "/documents/1", *MODULE_PATHS])
def test_local_links_are_resolvable(client, path):
    parser = LocalLinks()
    parser.feed(client.get(path).text)
    for target in parser.urls:
        assert client.get(target).status_code == 200, f"Broken link {path} -> {target}"


@pytest.mark.parametrize("path", ["/", "/guide", "/documents", "/documents/1", *MODULE_PATHS])
def test_read_only_routes_reject_post(client, path):
    response = client.post(path, data={"author": "Tên mẫu", "content": "Nội dung mẫu"})
    assert response.status_code == 405
    assert "Phương thức không được hỗ trợ" in response.text
    assert "GET" in response.headers["Allow"]
    assert 'href="/"' in response.text


@pytest.mark.parametrize("asset,content_type", [
    ("css/base.css", "text/css"), ("js/main.js", "javascript"),
])
def test_static_assets(client, asset, content_type):
    response = client.get(f"/static/{asset}")
    assert response.status_code == 200
    assert content_type in response.content_type
    assert len(response.data) > 100


def test_not_found_page(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert "LỖI 404" in response.text
    assert 'href="/"' in response.text


def test_500_page_does_not_leak_internal_error(app):
    app.config["PROPAGATE_EXCEPTIONS"] = False

    @app.get("/__test_only_error")
    def test_error():
        raise RuntimeError("INTERNAL_SECRET_PATH_123")

    response = app.test_client().get("/__test_only_error")
    assert response.status_code == 500
    assert "LỖI 500" in response.text
    assert "INTERNAL_SECRET_PATH_123" not in response.text
    assert "Traceback" not in response.text
    assert 'href="/"' in response.text
