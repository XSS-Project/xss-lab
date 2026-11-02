# Bằng chứng nền tảng — giai đoạn 1

Các tệp ở đây được lấy từ ứng dụng Flask đang chạy cục bộ:

| Tệp | Nội dung |
| --- | --- |
| `home-1440.png`, `home-390.png` | Ảnh trang chủ desktop/mobile, chụp bằng Chromium qua Playwright. |
| `documents-1440.png`, `documents-390.png` | Ảnh thư viện ở hai viewport tương ứng. |
| `home-response.html` | Body HTTP thật của GET `/` khi chạy bằng Flask CLI. |
| `cli-smoke.json` | Phiên bản Python/dependency, status/độ dài phản hồi, kiểm tra database chưa tạo và server đã dừng. |

Đây không phải bằng chứng Reflected/Stored/DOM XSS. Chưa có thực nghiệm XSS trong giai đoạn 1. Chi tiết lệnh, phương pháp và kết quả pytest ở [phase-1-results.md](../../docs/testing/phase-1-results.md).
