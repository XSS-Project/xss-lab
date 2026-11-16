"""
Máy chủ HTTP tĩnh cổng 8000 phục vụ môi trường thực hành Lab.
Hỗ trợ:
  - Phục vụ tệp tĩnh với bảng mã chuẩn UTF-8 (khắc phục lỗi hiển thị tiếng Việt trên Python 3.11+)
  - Tắt bộ nhớ đệm (Cache-Control: no-store) để trình duyệt luôn nhận nội dung tệp mới nhất
  - Cung cấp API trạng thái (/api/status) và cập nhật tham số cấu hình (/api/update-worm)
"""

from __future__ import annotations

from datetime import datetime
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from pathlib import Path
import re
import socket
from urllib.parse import urlparse

PORT = 8000
SERVE_DIR = Path(__file__).resolve().parent
TARGET_JS_PATH = SERVE_DIR / "worm.js"
SHORT_JS_PATH = SERVE_DIR / "w.js"

ACCESS_LOGS: list[dict[str, str]] = []
MAX_LOGS = 100


class LabHTTPRequestHandler(SimpleHTTPRequestHandler):
    def guess_type(self, path: str) -> str:
        base_type = super().guess_type(path)
        if any(
            base_type.startswith(t)
            for t in ("application/javascript", "text/javascript", "text/html", "text/css", "text/plain")
        ):
            if "charset=" not in base_type:
                return f"{base_type}; charset=utf-8"
        return base_type

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        super().end_headers()

    def log_message(self, fmt: str, *args):
        super().log_message(fmt, *args)
        path = urlparse(self.path).path
        if not path.startswith("/api/") and path != "/favicon.ico":
            ACCESS_LOGS.insert(
                0,
                {
                    "time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
                    "ip": self.client_address[0],
                    "method": getattr(self, "command", "GET"),
                    "path": self.path,
                    "user_agent": self.headers.get("User-Agent", ""),
                },
            )
            del ACCESS_LOGS[MAX_LOGS:]

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            js_text = TARGET_JS_PATH.read_text(encoding="utf-8") if TARGET_JS_PATH.exists() else ""
            msv_match = re.search(r'var\s+MSV\s*=\s*["\']([^"\']*)["\']', js_text)
            guid_match = re.search(r"var\s+samyGuid\s*=\s*(\d+)", js_text)
            self._send_json(
                {
                    "ips": get_local_ips(),
                    "port": PORT,
                    "logs": ACCESS_LOGS[:30],
                    "worm_js": js_text,
                    "msv": msv_match.group(1) if msv_match else "23001925",
                    "samy_guid": int(guid_match.group(1)) if guid_match else 59,
                }
            )
            return
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/update-worm":
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8", errors="replace")
            data = json.loads(raw or "{}")

            msv = str(data.get("msv", "23001925")).strip()
            samy_guid = int(data.get("samy_guid", 59))

            content = TARGET_JS_PATH.read_text(encoding="utf-8") if TARGET_JS_PATH.exists() else ""
            if content:
                content = re.sub(
                    r'var\s+MSV\s*=\s*["\'][^"\']*["\']\s*;',
                    f"var MSV = {json.dumps(msv, ensure_ascii=False)};",
                    content,
                )
                content = re.sub(
                    r"var\s+samyGuid\s*=\s*\d+\s*;",
                    f"var samyGuid = {samy_guid};",
                    content,
                )
                TARGET_JS_PATH.write_text(content, encoding="utf-8")
                SHORT_JS_PATH.write_text(content, encoding="utf-8")

            self._send_json({"ok": True, "worm_js": content, "msv": msv, "samy_guid": samy_guid})
            return

        if parsed.path == "/api/clear-logs":
            ACCESS_LOGS.clear()
            self._send_json({"ok": True})
            return

        self.send_error(404, "Endpoint not found")

    def _send_json(self, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def get_local_ips() -> list[str]:
    ips = ["127.0.0.1"]
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            ip = info[4][0]
            if ip not in ips:
                ips.append(ip)
    except OSError:
        pass
    return ips


def main():
    if TARGET_JS_PATH.exists():
        SHORT_JS_PATH.write_text(TARGET_JS_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    handler = partial(LabHTTPRequestHandler, directory=str(SERVE_DIR))
    server = HTTPServer(("0.0.0.0", PORT), handler)

    print("=" * 72)
    print(f"[+] Máy chủ HTTP cổng {PORT} đang chạy tại: {SERVE_DIR}")
    for ip in get_local_ips():
        print(f"    • Giao diện quản lý : http://{ip}:{PORT}/")
    print("=" * 72, flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Đã dừng máy chủ HTTP.")
        server.server_close()


if __name__ == "__main__":
    main()
