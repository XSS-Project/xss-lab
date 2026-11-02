# Bàn giao giai đoạn 1 — TV1

## Sản phẩm

- Khung ứng dụng tại thư mục gốc hiện tại, không có ứng dụng thứ hai hoặc phụ thuộc đường dẫn máy cá nhân.
- Factory, bốn Blueprint, cấu hình development/test, instance directory và DATABASE có thể ghi đè.
- Trang chủ có ba thẻ module, sáu liên kết phiên bản, tài liệu mẫu và hướng dẫn.
- Thư viện 6 tài liệu/4 danh mục, bộ lọc GET có trạng thái rỗng và bỏ lọc; chi tiết có nội dung và 404 cho ID thiếu.
- Sáu scaffold module có chuyển phiên bản, về trang chủ và trạng thái chưa triển khai.
- Giao diện tiếng Việt responsive, menu di động có hỗ trợ bàn phím và điều hướng khi tắt JavaScript, CSS/JS cục bộ, nhãn/focus, trang lỗi giữ status.
- Dependency runtime/dev tách riêng, pytest backend và bộ kiểm tra giao diện Playwright tối thiểu, tài liệu tích hợp.

## Tệp chính

| Nhóm | Tệp |
| --- | --- |
| Factory | `app/__init__.py` |
| Chức năng nền | `app/main/routes.py`, `app/main/data.py`, `app/templates/main/` |
| Giao diện chung | `app/templates/base.html`, `_document_card.html`, `_module_placeholder.html`, `errors/`, `app/static/css/base.css`, `app/static/js/main.js` |
| Scaffold | `app/reflected/`, `app/stored/`, `app/dom/` và template tương ứng |
| Test | `tests/conftest.py`, bốn test file backend, `tests/browser/test_foundation.py`, `pytest.ini` |
| Cài đặt | `requirements.txt`, `requirements-dev.txt`, `.gitignore`, `instance/.gitkeep` |
| Hồ sơ | `README.md`, `docs/requirements.md`, `docs/integration.md`, `docs/testing/phase-1-results.md` |

Xem README để cài/chạy và hồ sơ kết quả để xem số lượt kiểm thử thực tế. Không tự đánh dấu hoàn thành các checklist giai đoạn 2–5 trong tài liệu phân công gốc.

## TV2 có thể bắt đầu

Đọc DATABASE, bảng endpoint và ID tài liệu tại `integration.md`. Triển khai lớp dữ liệu `app/db.py`, schema/seed/CLI an toàn, sau đó thay hai route và template Stored. Giữ tên Blueprint/endpoint, đề xuất dùng document_id 1 cho lab. Thêm backend/database/browser test của module mình; bàn giao hook `init_app` để TV1 nối factory.

## TV3 có thể bắt đầu

Kế thừa `base.html`, tạo template/script preview riêng, giữ route DOM hiện có. Dùng fixture `live_server` và Playwright, bổ sung xử lý fragment/hashchange/reset và kiểm thử của module mình. Kế hoạch, mẫu kết quả tổng hợp, nội dung slide/demo vẫn thuộc phạm vi TV3.

## TV1 tiếp theo

1. Tạo tìm kiếm Reflected theo tiêu đề trên dữ liệu cố định, `q` tối đa 200 ký tự; quá giới hạn trả 400, không cắt dữ liệu.
2. Tạo cặp phiên bản có cùng chức năng, khác xử lý đầu ra HTML tại điểm minh họa; không tắt autoescape toàn ứng dụng.
3. Viết/chạy REF-01…REF-08 ở backend và trình duyệt; lưu bằng chứng HTTP/DOM trước/sau, kết quả thật, tài liệu module và nội dung demo.
4. Nhận lớp dữ liệu/Stored từ TV2, DOM từ TV3, nối hook SQLite và cập nhật trạng thái trang chủ/hướng dẫn/test scaffold khi tích hợp.
5. Kiểm tra chéo DOM sau khi có module; chưa kết luận về code chưa được bàn giao.

## Giới hạn còn lại

Chưa có đề chi tiết từ giảng viên. Chưa có XSS, database, tìm kiếm từ khóa, bình luận, preview hoặc kiểm tra chéo module. Chưa có báo cáo/slide/demo tổng hợp. Chưa kiểm tra trên macOS/Linux hoặc các trình duyệt ngoài Chromium. Kết quả kiểm thử giai đoạn 1 được thu trước khi khởi tạo Git; Git được bổ sung khi người dùng yêu cầu đưa mã nguồn lên GitHub.
