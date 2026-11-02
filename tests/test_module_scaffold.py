import pytest


MODULES = (
    ("search", "Reflected XSS"),
    ("comments", "Stored XSS"),
    ("preview", "DOM-based XSS"),
)


@pytest.mark.parametrize("path,module_name", MODULES)
@pytest.mark.parametrize("version,other,label", [
    ("vulnerable", "fixed", "Có lỗ hổng"),
    ("fixed", "vulnerable", "Đã khắc phục"),
])
def test_module_pages_are_honest_placeholders(client, path, module_name, version, other, label):
    response = client.get(f"/{version}/{path}")
    assert response.status_code == 200
    assert module_name in response.text
    assert label in response.text
    assert "Chưa triển khai chức năng thực nghiệm" in response.text
    assert f'href="/{other}/{path}"' in response.text
    assert 'href="/"' in response.text
    assert '<form' not in response.text
    assert '<textarea' not in response.text


def test_placeholder_does_not_render_query_as_html(client):
    response = client.get("/vulnerable/search", query_string={"q": "<em>ghi chú</em>"})
    assert "<em>ghi chú</em>" not in response.text
