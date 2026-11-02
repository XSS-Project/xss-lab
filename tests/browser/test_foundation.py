from pathlib import Path

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser


@pytest.mark.parametrize("width,height", [(1440, 1000), (390, 844)], ids=["desktop", "mobile"])
def test_layout_and_assets(page, live_server, width, height):
    errors = []
    failed_requests = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("requestfailed", lambda request: failed_requests.append(request.url))
    page.set_viewport_size({"width": width, "height": height})
    artifacts = Path(".artifacts/screenshots")
    artifacts.mkdir(parents=True, exist_ok=True)
    for path, name in [("/", "home"), ("/documents", "documents"),
                       ("/documents/1", "detail"), ("/guide", "guide"),
                       ("/vulnerable/search", "module")]:
        response = page.goto(live_server + path)
        assert response.status == 200
        expect(page.locator("h1")).to_be_visible()
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        page.screenshot(path=str(artifacts / f"{name}-{width}.png"), full_page=True)
    assert errors == []
    assert failed_requests == []


def test_filter_and_read_document(page, live_server):
    page.goto(live_server + "/documents")
    page.get_by_label("Danh mục", exact=True).select_option("JavaScript")
    page.get_by_role("button", name="Lọc tài liệu").click()
    expect(page.locator(".document-card")).to_have_count(1)
    page.get_by_role("link", name="JavaScript và cây DOM", exact=True).click()
    expect(page.locator("h1")).to_have_text("JavaScript và cây DOM")
    page.get_by_role("link", name="Quay lại danh sách", exact=False).click()
    expect(page.locator(".document-card")).to_have_count(6)


def test_mobile_menu_keyboard_and_navigation(page, live_server):
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(live_server)
    navigation = page.get_by_role("navigation", name="Điều hướng chính")
    toggle = page.get_by_role("button", name="Menu")
    expect(navigation).not_to_be_visible()
    toggle.click()
    expect(navigation).to_be_visible()
    page.keyboard.press("Escape")
    expect(navigation).not_to_be_visible()
    expect(toggle).to_be_focused()
    toggle.click()
    navigation.get_by_role("link", name="Tài liệu", exact=True).click()
    expect(page).to_have_url(live_server + "/documents")
    expect(page.locator('nav a[aria-current="page"]')).to_have_text("Tài liệu")


def test_module_pair_navigation(page, live_server):
    for path, module_name in [("search", "Reflected XSS"), ("comments", "Stored XSS"),
                              ("preview", "DOM-based XSS")]:
        page.goto(live_server + f"/vulnerable/{path}")
        expect(page.locator("h1")).to_have_text(module_name)
        page.get_by_role("link", name="Sang bản Đã khắc phục", exact=False).click()
        expect(page).to_have_url(live_server + f"/fixed/{path}")
        expect(page.get_by_role("heading", name="Chưa triển khai chức năng thực nghiệm")).to_be_visible()


def test_navigation_without_javascript(browser, live_server):
    context = browser.new_context(java_script_enabled=False, viewport={"width": 390, "height": 844})
    try:
        page = context.new_page()
        page.goto(live_server)
        navigation = page.get_by_role("navigation", name="Điều hướng chính")
        expect(navigation).to_be_visible()
        navigation.get_by_role("link", name="Hướng dẫn").click()
        expect(page.locator("h1")).to_have_text("Một lab nhỏ, mục tiêu rõ ràng.")
    finally:
        context.close()
