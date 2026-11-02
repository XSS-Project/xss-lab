# Kết quả kiểm thử giai đoạn 1

Ngày bàn giao: **02/11/2026**, theo ngữ cảnh phiên làm việc Asia/Saigon. Phạm vi là khung ứng dụng TV1 và chức năng nền tảng; không phải kết quả thí nghiệm XSS.

## Môi trường

Windows, Python 3.12.10; Flask 3.1.3, pytest 9.2.0, Playwright 1.64.1, pytest-playwright 0.10.0. Browser: Chromium / Chrome for Testing 156.0.8078.4, Playwright build 1248, headless. Chưa có Git repository hoặc commit SHA trong workspace ban đầu.

## Lệnh đã chạy và kết quả

```powershell
.\.venv\Scripts\python.exe -m pytest -m "not browser" -q --tb=short
# 57 passed, 6 deselected in 1.28s

.\.venv\Scripts\python.exe -m playwright install chromium
# Tải thành công Chromium và Chrome Headless Shell.

.\.venv\Scripts\python.exe -m pytest -m browser --browser chromium -q --tb=short --maxfail=2
# 6 passed, 57 deselected, 1 warning in 10.71s

.\.venv\Scripts\python.exe -m pip check
# No broken requirements found.

.\.venv\Scripts\python.exe -m flask --app app:create_app routes
# 11 endpoint, gồm 10 endpoint trang và static.
```

**Tổng kết hai lượt chạy độc lập: 63 lượt test được chọn, 63 đạt, 0 không đạt, 0 bỏ qua trong phần đã chọn.** `deselected` chỉ là test thuộc nhóm còn lại khi chạy bằng marker, không được tính thêm thành ca đạt hoặc ca chưa chạy. Mỗi tổ hợp parametrization được tính là một lượt pytest; đây không phải số ca REF/STO/DOM của giai đoạn thực nghiệm.

Playwright có một `PytestRemovedIn10Warning` từ fixture `base_url` của plugin về session-scoped instance-method fixture. Các test hiện tại vẫn đạt; không che/suppress cảnh báo. Cần kiểm tra tính tương thích plugin trước khi nâng lên pytest 10.

## Backend — Đạt

| Nhóm kiểm tra | Tệp / cách kiểm chứng |
| --- | --- |
| Factory, Blueprint, cấu hình mặc định/test, tự tạo instance directory | `tests/test_factory.py` |
| Không tạo database khi GET; không thay đổi database mặc định nếu có sẵn | `tests/test_factory.py` |
| Trang chủ/hướng dẫn/tài liệu trả 200; đủ sáu liên kết; liên kết nội bộ/static không hỏng | `tests/test_navigation.py` |
| POST bị từ chối trên route GET; response 405 giữ Allow | `tests/test_navigation.py` |
| CSS/JS được phục vụ; 404/500 có giao diện và đúng status | `tests/test_navigation.py` |
| 500 không đưa lỗi nội bộ vào response; route gây lỗi chỉ được thêm vào app test | `tests/test_navigation.py` |
| Sáu tài liệu, ID duy nhất, lọc từng danh mục, danh mục rỗng/không tồn tại | `tests/test_documents.py` |
| Query chứa ký tự giống HTML được escape; Unicode và nội dung chi tiết hiển thị đúng | `tests/test_documents.py` |
| Tài liệu có thật trả 200; ID không tồn tại trả 404 | `tests/test_documents.py` |
| Sáu scaffold đúng module/phiên bản/trạng thái, chuyển bản, không có form giả | `tests/test_module_scaffold.py` |

Fixture app dùng DATABASE tạm trong `.pytest-tmp`. Không mở SQLite trong giai đoạn này. Thư mục Temp mặc định của máy gặp lỗi quyền truy cập; cấu hình basetemp riêng trong repo giải quyết vấn đề mà không thay quyền thư mục hệ thống.

## Trình duyệt — Đạt

Tất cả test tại `tests/browser/test_foundation.py`, dùng server localhost và browser thật:

| Lượt | Đầu vào / thao tác | Kỳ vọng và thực tế |
| --- | --- | --- |
| Desktop | Viewport 1440×1000, mở `/`, `/documents`, `/documents/1`, `/guide`, `/vulnerable/search` | Các trang 200, h1 thấy được, không tràn ngang, không pageerror/requestfailed; đã chụp ảnh. |
| Mobile | Viewport 390×844, cùng năm trang | Cùng kiểm tra desktop, bố cục đổi về cột đơn; đã chụp ảnh. |
| Lọc và đọc | Chọn JavaScript, bấm lọc, mở tài liệu, quay lại danh sách | Một tài liệu phù hợp, chi tiết đúng, quay lại có đủ 6 tài liệu. |
| Menu/bàn phím | Mobile: mở menu, Escape, mở lại, chọn Tài liệu | Menu đóng/mở đúng, Escape đưa focus về nút, điều hướng và aria-current đúng. |
| Chuyển phiên bản | Mở từng module bản vulnerable rồi chuyển sang fixed | Đúng URL đối ứng, đúng tên và trạng thái chưa triển khai cho cả ba module. |
| Không JavaScript | Context mobile tắt JS, mở trang chủ và chọn Hướng dẫn | Navigation vẫn hiển thị và điều hướng được. |

Đã xem trực tiếp ảnh trang chủ desktop/mobile: chữ, thẻ, nút và nội dung hiển thị đầy đủ trong hai kích thước đã thử. Đây là đánh giá giới hạn trên Chromium, không khẳng định đã kiểm tra mọi thiết bị hoặc accessibility toàn diện.

Fixture tự cấp cổng localhost và shutdown/đóng socket/join thread sau mỗi test. Browser context riêng được đóng khi xong. Không cần server chạy thủ công.

## Kiểm tra chạy thật qua Flask CLI

Đã khởi động tiến trình bằng `python -m flask --app app:create_app run --host 127.0.0.1 --port <cổng trống>` và gửi HTTP thật tới `/`, `/documents`, `/documents/1`, `/guide`, `/fixed/preview`, `/static/css/base.css`: tất cả trả 200. `instance/lab.sqlite` không được tạo; tiến trình kiểm tra đã dừng.

Thông tin dependency và kết quả request lấy từ chương trình kiểm tra tại [cli-smoke.json](../../evidence/foundation/cli-smoke.json). Phản hồi trang chủ: [home-response.html](../../evidence/foundation/home-response.html).

## Bằng chứng giao diện

- [Trang chủ desktop 1440px](../../evidence/foundation/home-1440.png).
- [Trang chủ mobile 390px](../../evidence/foundation/home-390.png).
- [Thư viện desktop 1440px](../../evidence/foundation/documents-1440.png).
- [Thư viện mobile 390px](../../evidence/foundation/documents-390.png).

Ảnh do Playwright chụp từ ứng dụng đang chạy. Bộ ảnh đầy đủ của năm trang ở hai kích thước nằm trong `.artifacts/screenshots/`, được bỏ qua khỏi Git. Các ảnh chọn trong `evidence/foundation/` là bằng chứng bàn giao giữ lại có chủ đích.

## Chưa chạy / ngoài phạm vi hiện tại

| Phần | Trạng thái và lý do |
| --- | --- |
| REF-01…REF-08 | Chưa chạy: tìm kiếm và thí nghiệm Reflected chưa triển khai theo yêu cầu dừng ở giai đoạn 1. |
| STO-01…STO-10 | Chưa chạy: chờ lớp dữ liệu và module TV2. |
| DOM-01…DOM-10 | Chưa chạy: chờ module TV3. |
| Kiểm tra chéo DOM/Stored/Reflected | Chưa chạy: chưa nhận module thật và bằng chứng tương ứng. |
| Init/reset, seed, tách bảng, dữ liệu cũ | Chưa chạy: chưa có SQLite/CLI. |
| Firefox, WebKit, macOS/Linux | Chưa chạy: phiên này chỉ kiểm tra Windows/Chromium. |
| Báo cáo/slide/demo tổng hợp | Chưa thực hiện: thuộc giai đoạn/module tiếp theo. |

Không có payload, kết quả thực thi XSS hoặc tỷ lệ khắc phục được khẳng định từ các test nền tảng này.
