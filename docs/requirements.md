# Yêu cầu giai đoạn 1 — Thành viên 1

## Nguồn và phạm vi đã xác nhận

Đã đọc ba tài liệu phân công `Thanh_vien_1_Reflected_XSS.md`, `Thanh_vien_2_Stored_XSS.md`, `Thanh_vien_3_DOM_XSS.md` từ thư mục Downloads và yêu cầu chi tiết đính kèm trong phiên làm việc ngày 02/11/2026 (Asia/Saigon).

Yêu cầu đính kèm chỉ định **dừng sau giai đoạn 1 của TV1** và bổ sung rõ các chức năng nền tảng. Khi có khác biệt về phạm vi, dùng yêu cầu cụ thể này:

- Cho phép tạo trang scaffold có trạng thái trung thực, gồm sáu route điều hướng; không triển khai module thực nghiệm giả.
- Chưa tạo `app/db.py`, chưa kết nối, tạo hay seed database. Đây là công việc TV2.
- Trang chủ, tài liệu, chi tiết và hướng dẫn phải hoạt động thật; dữ liệu mẫu cố định trong `app/main/data.py`.
- Chưa làm tìm kiếm từ khóa, bình luận, preview từ fragment, payload hay lỗ hổng XSS.
- Chuẩn bị Playwright; chưa cần toàn bộ hạ tầng kiểm thử thực nghiệm của ba module. Có thể kiểm tra giao diện thật nếu môi trường hỗ trợ.

## Yêu cầu đã thực hiện trong khung

| Nhóm | Yêu cầu |
| --- | --- |
| Công nghệ | Python Flask, Jinja2, HTML/CSS/JS thuần; không frontend framework, CDN, Docker hoặc dịch vụ ngoài. |
| Factory | `create_app(test_config=None)`, instance directory, DATABASE mặc định `instance/lab.sqlite`, cấu hình test ghi đè được. |
| Module | Blueprint `main`, `reflected`, `stored`, `dom`; export `bp`; đăng ký không url_prefix. |
| Trang nền tảng | `/`, `/documents`, `/documents/<int:document_id>`, `/guide`. |
| Tài liệu | 6 tài liệu giả, ID ổn định, 4 danh mục; lọc `category`, trạng thái rỗng, bỏ lọc, 404 nếu thiếu ID. |
| Khung thực nghiệm | 6 trang GET có nhãn phiên bản, trạng thái chưa triển khai, chuyển phiên bản và về trang chủ. |
| Layout | Tiếng Việt; block title/content/scripts; điều hướng đang chọn, thẻ tài liệu, responsive, label, focus và nhãn có chữ. |
| Lỗi | Trang 404/405/500 giữ status; 405 giữ Allow; 500 không đưa thông tin lỗi nội bộ vào response. |
| Kiểm thử | pytest backend; kiểm tra trình duyệt nền tảng bằng Playwright; cấu hình DATABASE tạm; server test tự dừng. |
| Tài liệu | README, requirements, integration, kết quả kiểm thử và bàn giao. |

## Quyết định kỹ thuật của khung

- Dùng Python 3.12.10 và pin các dependency trực tiếp đã cài kiểm chứng trong `requirements*.txt`.
- Tách `main` khỏi ba module nghiên cứu. Trang chủ tại `templates/main/index.html` theo yêu cầu đính kèm; không tạo thêm `templates/index.html` trùng lặp.
- Chưa cần secret key vì chưa có session hoặc form ghi dữ liệu.
- Giữ autoescape mặc định của Flask/Jinja2 cho HTML. Các giá trị query chỉ dùng trong dữ liệu template, không biên dịch thành template hay HTML.
- Không có `config.py` riêng: cấu hình mặc định nằm trong factory và có thể ghi đè bằng `test_config`.
- Shared placeholder nằm ở `_module_placeholder.html`, từng module có template và route riêng để thay độc lập.
- ID tài liệu 1…6 là khóa ổn định; không dùng vị trí trong tuple làm ID. Danh mục lọc bằng tên đầy đủ, so khớp chính xác; bỏ trống nghĩa là tất cả.
- JavaScript chung chỉ điều khiển menu di động; không có xử lý fragment hay sink HTML.
- Fixture browser tối thiểu dùng Werkzeug trên cổng trống localhost, dừng trong `finally`; không thêm dịch vụ chạy nền lâu dài.
- Pytest dùng `.pytest-tmp` trong dự án do thư mục Temp mặc định của môi trường hiện tại gặp lỗi quyền; thư mục này chỉ dành cho test và nằm trong `.gitignore`.
- Workspace ban đầu trống, chưa có `.git` và không có AGENTS.md ở workspace/ổ đĩa cha. Git được khởi tạo khi người dùng yêu cầu đẩy mã nguồn lên GitHub sau bàn giao giai đoạn 1.

## Nội dung chờ đối chiếu hoặc giai đoạn sau

- Chưa được cung cấp đề chi tiết từ giảng viên hoặc nội dung “Projects”; chưa xác nhận yêu cầu ngoài ba tài liệu phân công và yêu cầu đính kèm.
- Chưa có danh tính thành viên, thời hạn, mẫu báo cáo của lớp hoặc yêu cầu định dạng slide.
- TV2 chưa bàn giao SQLite/Stored; TV3 chưa bàn giao DOM, biểu mẫu kiểm thử tổng hợp và demo.
- Chưa có thực nghiệm XSS để thu bằng chứng trước/sau hoặc kiểm tra chéo. Không coi kiểm thử nền tảng là bằng chứng XSS.
- Việc tích hợp `app.db.init_app(app)`, init/reset và kiểm tra đầy đủ ba module thuộc giai đoạn bàn giao tiếp theo.

Không tự thêm đăng nhập, phân quyền, upload, rich text hoặc triển khai công khai.
