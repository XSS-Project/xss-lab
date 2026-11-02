# ATMT Lab — Khung ứng dụng giai đoạn 1

Website lab chia sẻ tài liệu học tập cho môn An toàn máy tính. Thành viên 1 phụ trách khung Flask, giao diện chung và tích hợp. Chỉ chạy cục bộ trên `127.0.0.1`, dùng dữ liệu giả.

## Trạng thái bàn giao

Đã có: application factory, giao diện tiếng Việt responsive, trang chủ, 6 tài liệu mẫu, lọc theo danh mục, trang chi tiết, hướng dẫn, trang lỗi 404/405/500 và sáu trang điều hướng module. Các trang module đều ghi rõ **Chưa triển khai chức năng thực nghiệm** và có liên kết chuyển phiên bản.

Chưa có: tìm kiếm từ khóa, lỗ hổng XSS, xử lý ghi chú/fragment, bình luận, SQLite, init/reset dữ liệu, kết quả thực nghiệm XSS. Nhãn “Có lỗ hổng” / “Đã khắc phục” hiện chỉ định danh phiên bản dự kiến.

## Môi trường đã kiểm tra

- Windows, Python **3.12.10**.
- Flask **3.1.3**, pytest **9.2.0**, Playwright **1.64.1**, pytest-playwright **0.10.0**.
- Runtime: Flask/Jinja2; frontend: HTML, CSS, JavaScript thuần, không CDN.
- Các nền tảng macOS/Linux có lệnh cài đặt bên dưới nhưng chưa được chạy kiểm tra trực tiếp.

## Cài đặt và chạy

Chạy lệnh từ thư mục chứa README. Không cần database hoặc Node.js.

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app:create_app run --host 127.0.0.1
```

Mở `http://127.0.0.1:5000`. Dừng server bằng `Ctrl+C`.

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
flask --app app:create_app run --host 127.0.0.1
```

Nếu đã kích hoạt môi trường ảo trên PowerShell bằng `.\.venv\Scripts\Activate.ps1`, cũng có thể dùng lệnh chung:

```text
flask --app app:create_app run --host 127.0.0.1
```

Ứng dụng không tự bật debug, không tự khởi động server khi import. Không đổi host sang `0.0.0.0` hoặc triển khai lab công khai.

## Kiểm thử

Cài dependency kiểm thử (đã bao gồm dependency chạy ứng dụng):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -m "not browser" -q
```

Chạy riêng trình duyệt thật hoặc toàn bộ:

```powershell
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe -m pytest -m browser --browser chromium -q
.\.venv\Scripts\python.exe -m pytest --browser chromium -q
```

macOS/Linux sau khi kích hoạt `.venv` dùng cùng các lệnh `python -m ...` thay cho `.\.venv\Scripts\python.exe -m ...`. Linux có thể cần `python -m playwright install --with-deps chromium` nếu hệ thống thiếu thư viện trình duyệt.

Không cần tự bật Flask trước khi chạy test. Fixture `live_server` tự khởi động server ở `127.0.0.1` trên cổng trống do hệ điều hành cấp, rồi shutdown/đóng socket sau mỗi test. Mỗi app test dùng `DATABASE` trong thư mục tạm; giai đoạn 1 không mở database này.

`pytest.ini` đặt `--basetemp=.pytest-tmp`. **Đây là thư mục dành riêng cho test, pytest có thể xóa và tạo lại nó; không lưu dữ liệu làm việc tại đây.** Không chạy hai phiên pytest đồng thời với cùng basetemp; khi cần, chỉ định hai thư mục tạm riêng. Cache, database và `.artifacts/` được bỏ qua bởi `.gitignore`. Ảnh kiểm tra giao diện được sinh vào `.artifacts/screenshots/`.

Phạm vi và kết quả kiểm tra thực tế: [docs/testing/phase-1-results.md](docs/testing/phase-1-results.md).

## URL

| Trang | URL | Trạng thái |
| --- | --- | --- |
| Trang chủ | `/` | Hoạt động |
| Thư viện và lọc | `/documents`, `/documents?category=Web` | Hoạt động |
| Chi tiết tài liệu | `/documents/1` đến `/documents/6` | Hoạt động |
| Hướng dẫn | `/guide` | Hoạt động |
| Reflected | `/vulnerable/search`, `/fixed/search` | Khung điều hướng |
| Stored | `/vulnerable/comments`, `/fixed/comments` | Khung điều hướng |
| DOM-based | `/vulnerable/preview`, `/fixed/preview` | Khung điều hướng |

Tất cả route trên chỉ nhận GET (Flask cũng cung cấp HEAD/OPTIONS). POST hiện trả 405, kể cả trang bình luận. ID tài liệu không tồn tại trả 404. Danh mục không tồn tại trả 200 với trạng thái rỗng và nút bỏ lọc.

## Thành viên tiếp tục từ đâu?

Đọc [hợp đồng tích hợp](docs/integration.md) trước khi sửa phần chung.

- **TV2:** phát triển `app/db.py`, schema/seed/CLI và thay khung trong `app/stored/`, `app/templates/stored/` bằng bình luận thật. Dùng `current_app.config['DATABASE']`, giữ ID tài liệu. Giao diện dữ liệu sẽ gồm `get_db()`, `close_db(error=None)`, `init_db()`, `init_app(app)`. Khi nhận module, TV1 sẽ nối `init_app(app)` vào factory. Hiện chưa có lệnh init/reset để chạy.
- **TV3:** thay khung trong `app/dom/`, `app/templates/dom/`; đặt script preview riêng tại `app/static/js/`, dùng block `scripts`. Module này không phụ thuộc SQLite. Dùng lại fixture `live_server`, Playwright và layout hiện có.
- **TV1 tiếp theo:** triển khai tìm kiếm Reflected, hai phiên bản xử lý đầu ra, kiểm thử REF-01…REF-08 và bằng chứng trước/sau. Giai đoạn 1 dừng trước phần thực nghiệm.

## Lỗi môi trường thường gặp

| Hiện tượng | Cách xử lý |
| --- | --- |
| Không có lệnh `py` | Dùng `python` với Python 3.12 đã cài; kiểm tra `python --version`. |
| PowerShell chặn `Activate.ps1` | Dùng trực tiếp `.\.venv\Scripts\python.exe` như các lệnh trên; không cần thay execution policy. |
| `No module named flask/pytest` | Cài file requirements tương ứng bằng đúng Python của `.venv`. |
| Flask không import được `app` | Chạy từ thư mục gốc chứa `app/` và README. |
| Cổng 5000 đang được dùng | Thêm `--port 5001` vào lệnh Flask rồi mở URL cổng 5001. |
| Playwright báo thiếu executable | Chạy `python -m playwright install chromium` bằng môi trường ảo tương ứng. |
| Pytest lỗi quyền thư mục tạm | Dùng cấu hình `.pytest-tmp` đã cung cấp, hoặc `--basetemp=<thư mục riêng cho test có quyền ghi>`. Không trỏ tới thư mục chứa dữ liệu cần giữ. |
| Thấy trang “Chưa triển khai” | Đây là trạng thái đúng của sáu trang module trong giai đoạn 1. |

## Hồ sơ bàn giao

- [Yêu cầu và phần chưa xác nhận](docs/requirements.md).
- [Tích hợp, route, dữ liệu và quyền sở hữu](docs/integration.md).
- [Kết quả kiểm thử giai đoạn 1](docs/testing/phase-1-results.md).
- [Bàn giao và công việc tiếp theo](docs/handover.md).

Thư mục ban đầu trống, chưa có Git repository hoặc mã nguồn thành viên khác. Git được khởi tạo khi người dùng yêu cầu đưa bộ khung lên GitHub; `.gitignore` loại môi trường ảo, cache, log và dữ liệu tạm. Chưa nhận đề chi tiết từ giảng viên để đối chiếu yêu cầu môn học.
