# Hợp đồng tích hợp

## Cấu trúc hiện tại

```text
app/
  __init__.py                 # create_app và error handlers — TV1
  main/{__init__,routes,data}.py
  reflected/{__init__,routes}.py
  stored/{__init__,routes}.py  # scaffold; TV2 tiếp quản
  dom/{__init__,routes}.py     # scaffold; TV3 tiếp quản
  templates/
    base.html
    _document_card.html
    _module_placeholder.html
    main/{index,documents,document_detail,guide}.html
    reflected/placeholder.html
    stored/placeholder.html
    dom/placeholder.html
    errors/{404,405,500}.html
  static/{css/base.css,js/main.js}
tests/
  conftest.py
  test_factory.py
  test_navigation.py
  test_documents.py
  test_module_scaffold.py
  browser/test_foundation.py
docs/{requirements.md,integration.md,handover.md,modules/,testing/,report/,presentation/}
evidence/{reflected/,stored/,dom/}
instance/.gitkeep
requirements.txt
requirements-dev.txt
pytest.ini
README.md
```

`app/db.py` chưa tồn tại theo phạm vi giai đoạn 1. Thư mục `instance/` được factory tạo nếu chưa có; chưa có database. `evidence/foundation/` lưu bằng chứng nền tảng khi có kiểm tra thực tế; không thay thế bằng chứng từng module.

## Factory và Blueprint

Factory nằm tại `app/__init__.py`, chữ ký `create_app(test_config=None)`. Tất cả Blueprint hiện đã đăng ký; không thêm `url_prefix` khi tích hợp.

Ví dụ từ module reflected:

```python
# app/reflected/__init__.py
from flask import Blueprint

bp = Blueprint("reflected", __name__)
from app.reflected import routes

# app/reflected/routes.py
from app.reflected import bp

@bp.get("/vulnerable/search")
def vulnerable_search():
    ...  # thay phần render placeholder bằng xử lý thật
```

Giữ tên Blueprint và endpoint để không làm hỏng `url_for` từ layout hoặc module khác. Không đăng ký thêm route trùng khi thay khung; sửa route đã có. Không đặt lệnh chạy server trong module import.

## Route và endpoint thực tế

| Phương thức hiện tại | URL | Endpoint |
| --- | --- | --- |
| GET | `/` | `main.index` |
| GET | `/documents` | `main.documents` |
| GET | `/documents/<int:document_id>` | `main.document_detail` |
| GET | `/guide` | `main.guide` |
| GET | `/vulnerable/search` | `reflected.vulnerable_search` |
| GET | `/fixed/search` | `reflected.fixed_search` |
| GET | `/vulnerable/comments` | `stored.vulnerable_comments` |
| GET | `/fixed/comments` | `stored.fixed_comments` |
| GET | `/vulnerable/preview` | `dom.vulnerable_preview` |
| GET | `/fixed/preview` | `dom.fixed_preview` |
| GET | `/static/<path:filename>` | `static` |

HEAD/OPTIONS được Flask bổ sung. POST hiện trả 405. TV2 sẽ bổ sung POST cho hai route comments cùng validation và redirect 303 trong module thật. Test khung liên quan cần được cập nhật khi phạm vi này thay đổi.

## Layout, CSS và JavaScript

Các trang kế thừa `base.html`, cung cấp ba block:

```html
{% extends 'base.html' %}
{% block title %}Tên trang{% endblock %}
{% block content %}
<h1>Nội dung của module</h1>
{% endblock %}
{% block scripts %}
<script src="{{ url_for('static', filename='js/preview.js') }}" defer></script>
{% endblock %}
```

Template riêng đặt trong `templates/reflected/`, `stored/`, `dom/`. Template placeholder kế thừa `_module_placeholder.html` chỉ để hiển thị trạng thái hiện tại; module thật nên kế thừa `base.html` và tự render chức năng.

CSS chung tại `static/css/base.css`. Có sẵn `.button.primary`, `.button.secondary`, `.text-link`, `.tag.vulnerable`, `.tag.fixed`, `.tag.neutral`, `.content-card`, `.actions`. Dùng thêm class có tiền tố module nếu cần; thống nhất thay đổi CSS chung với TV1.

Mỗi trang có một h1. Nhãn phiên bản phải có chữ và màu. Form cần label, liên kết/nút cần focus state. Không thêm tài nguyên CDN. `main.js` chỉ điều khiển menu; TV3 đặt logic preview trong script riêng, nạp qua block `scripts`.

Mọi URL dùng `url_for`. Giữ autoescape mặc định; không tắt toàn cục hoặc đưa dữ liệu người dùng vào mã nguồn template.

## Dữ liệu tài liệu mẫu dùng chung

```python
from app.main.data import DOCUMENTS, CATEGORIES, get_document

document = get_document(1)  # dict hoặc None
```

`DOCUMENTS` là tuple chứa các dict `id`, `title`, `category`, `description`, `content`. Không sửa trực tiếp dict dùng chung trong request hoặc test; sao chép nếu cần dữ liệu thử. `CATEGORIES` là tuple tên danh mục sắp xếp. Nguồn này không đọc SQLite.

| ID ổn định | Tiêu đề | Danh mục |
| --- | --- | --- |
| 1 | Bắt đầu với ứng dụng Web | Web |
| 2 | HTTP: request và response | HTTP |
| 3 | JavaScript và cây DOM | JavaScript |
| 4 | Dữ liệu đầu vào và ranh giới tin cậy | An toàn ứng dụng |
| 5 | Template Jinja2 và hiển thị văn bản | Web |
| 6 | Query parameter và URL fragment | HTTP |

Không đánh lại ID khi bổ sung tài liệu. Đề xuất TV2 dùng **document_id = 1** cho tài liệu cố định trên hai trang comments và ghi lựa chọn này trong docs/module của mình. Khi đổi nguồn dữ liệu hoặc ID, cập nhật đồng bộ code, seed, test và tài liệu.

Danh sách hiện chỉ lọc chính xác theo query `category`; chưa có `q`. TV1 có thể dùng cùng DOCUMENTS cho tìm kiếm theo tiêu đề ở giai đoạn Reflected.

## Hợp đồng SQLite chờ TV2 bàn giao

`app.config['DATABASE']` mặc định là đường dẫn tuyệt đối được tính từ `app.instance_path / 'lab.sqlite'`, không gắn cứng đường dẫn máy. Test ghi đè bằng đường dẫn tạm. Factory chỉ tạo instance directory; không mở file, không import module dữ liệu chưa tồn tại.

TV2 sẽ cung cấp `app/db.py`:

```python
get_db()
close_db(error=None)
init_db()
init_app(app)
```

Khi nhận đầy đủ module, TV1 thêm vào factory:

```python
from app import db
db.init_app(app)
```

`init_app` đăng ký teardown và CLI, **không reset/seed/xóa dữ liệu khi startup**. TV2 dùng application context, `sqlite3.Row`, truy vấn tham số hóa, ánh xạ tên bảng nội bộ. Hai bảng `comments_vulnerable`, `comments_fixed` độc lập có `id`, `document_id`, `author`, `content`, `created_at`.

Theo tài liệu phân công, CLI dự kiến là `init-db` (không nhân seed) và `reset-lab --yes` (transaction, chỉ hai bảng lab). Đây là hợp đồng tương lai, **chưa có các lệnh này trong khung hiện tại**. TV2 phải bàn giao test và hướng dẫn trước khi README chuyển chúng sang trạng thái hoạt động.

## Quyền sở hữu và thay scaffold

| Thành viên | Tệp phụ trách |
| --- | --- |
| TV1 | Factory, `main/`, layout/includes/errors, CSS/JS chung, requirements, hạ tầng test, README, requirements/integration, `reflected/`, tài liệu/bằng chứng Reflected. |
| TV2 | `app/db.py`, schema/seed, `stored/`, templates Stored, tests Stored, docs/bằng chứng Stored, báo cáo tổng hợp. |
| TV3 | `dom/`, templates DOM, script preview riêng, tests DOM, docs/bằng chứng DOM, kế hoạch/kết quả kiểm thử tổng hợp và slide/demo. |

Các scaffold Stored/DOM hiện do TV1 tạo theo yêu cầu giai đoạn 1; TV2/TV3 tiếp quản từ đó. Không có module thực nghiệm của thành viên khác bị ghi đè.

Khi thay scaffold:

1. Giữ `bp`, tên endpoint, đường dẫn, layout và liên kết chuyển phiên bản.
2. Thay template/route của module mình; không tạo factory hoặc giao diện nền thứ hai.
3. Viết test riêng tại `tests/reflected/`, `tests/stored/`, `tests/dom/`; kế thừa fixture chung.
4. Chỉ cập nhật test scaffold của module tương ứng: khi module thật xuất hiện, assertion “chưa triển khai” và “không có form” sẽ không còn phù hợp. TV2 cũng cập nhật kỳ vọng POST trong test navigation cho hai trang comments.
5. Cùng TV1 cập nhật trạng thái trang chủ/hướng dẫn, tài liệu, seed, requirements và test khi có thay đổi phần chung. Không xóa test khung không liên quan để làm module mình chạy.
6. Cung cấp kết quả đã chạy và bằng chứng thật; ca thiếu môi trường ghi Chưa chạy, không suy ra kết quả từ module khác.

TV3 triển khai preview từ fragment, decode đúng một lần, hashchange/reset và script riêng; không phụ thuộc SQLite. Fixture hiện không có dữ liệu thử Stored: TV2 cần tự thêm fixture schema/seed trong phạm vi test của mình.

## Chạy và kiểm thử

```text
python -m pip install -r requirements-dev.txt
python -m flask --app app:create_app run --host 127.0.0.1
python -m pytest -m "not browser" -q
python -m playwright install chromium
python -m pytest -m browser --browser chromium -q
```

Các lệnh trên dùng Python đã kích hoạt `.venv`; xem README cho lệnh PowerShell không cần activate. Factory fixture nhận DATABASE tạm. `live_server` khởi động/dừng localhost mỗi test; `page`, `browser`, `context` do pytest-playwright quản lý. Đánh dấu test trình duyệt bằng `@pytest.mark.browser` để có thể chạy backend riêng.

`--basetemp=.pytest-tmp` là thư mục test chuyên dụng, được pytest dọn khi chạy lại. Không lưu dữ liệu cần giữ trong đó. Không dùng hai pytest đồng thời cùng basetemp. Không có server test cần tự tắt thủ công.
