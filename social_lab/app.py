"""
Trang Web Mạng xã hội giả lập (Elgg Profile Lab) phục vụ thực hành môn An toàn máy tính.
Mô phỏng đầy đủ các chức năng của mạng xã hội Elgg:
  - Đăng nhập / Đăng xuất & Chuyển nhanh giữa các tài khoản (Alice, Boby, Charlie, Samy)
  - Trang Hồ sơ cá nhân (Profile) hiển thị:
      + Brief Description (giới hạn tối đa 250 ký tự, minh họa lỗ hổng Stored XSS)
      + About me (description)
      + Danh sách bạn bè (Friends)
  - Trang Chỉnh sửa hồ sơ (Edit Profile) với kiểm tra độ dài Brief Description <= 250 ký tự
  - Chức năng Kết bạn (Add Friend) tại /action/friends/add
  - Chức năng Cập nhật hồ sơ tại /action/profile/edit
  - Cung cấp biến môi trường JS `window.elgg` tương thích chuẩn SEED Labs Elgg
  - Nút Reset Lab để khôi phục dữ liệu gốc về ban đầu
"""

from __future__ import annotations

from http import cookies
from http.server import BaseHTTPRequestHandler, HTTPServer
import html
import io
import json
import os
from pathlib import Path
import socket
import sqlite3
import time
from urllib.parse import parse_qs, urlparse

PORT = int(os.environ.get("PORT", "5000"))
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "social_lab.sqlite"
BRIEF_MAX_LEN = 250

INITIAL_USERS = [
    {
        "guid": 56,
        "username": "alice",
        "password": "seedalice",
        "name": "Alice Nguyen",
        "email": "alice@example.edu.vn",
        "location": "Hà Nội, Việt Nam",
        "briefdescription": "Sinh viên năm 3 ngành An toàn thông tin.",
        "description": "Xin chào! Mình là Alice. Mình yêu thích nghiên cứu bảo mật ứng dụng Web và CTF.",
        "avatar_color": "#2563eb",
    },
    {
        "guid": 57,
        "username": "boby",
        "password": "seedboby",
        "name": "Boby Tran",
        "email": "boby@example.edu.vn",
        "location": "Đà Nẵng, Việt Nam",
        "briefdescription": "Thành viên CLB An toàn thông tin.",
        "description": "Mình là Boby, đam mê lập trình Python và quản trị mạng.",
        "avatar_color": "#059669",
    },
    {
        "guid": 58,
        "username": "charlie",
        "password": "seedcharlie",
        "name": "Charlie Le",
        "email": "charlie@example.edu.vn",
        "location": "TP. Hồ Chí Minh, Việt Nam",
        "briefdescription": "Full-stack Developer & Security Researcher.",
        "description": "Trang hồ sơ cá nhân của Charlie trên mạng xã hội nội bộ.",
        "avatar_color": "#7c3aed",
    },
    {
        "guid": 59,
        "username": "samy",
        "password": "seedsamy",
        "name": "Samy Kamkar",
        "email": "samy@example.edu.vn",
        "location": "Hà Nội, Việt Nam",
        "briefdescription": "Samy is my hero!",
        "description": "Tài khoản thực nghiệm trong bài Lab Self-Propagation XSS.",
        "avatar_color": "#dc2626",
    },
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(reset=False):
    conn = get_db()
    with conn:
        if reset:
            conn.execute("DROP TABLE IF EXISTS friendships")
            conn.execute("DROP TABLE IF EXISTS users")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                guid INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                location TEXT NOT NULL,
                briefdescription TEXT NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT '',
                avatar_color TEXT NOT NULL DEFAULT '#2563eb'
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS friendships (
                user_guid INTEGER NOT NULL,
                friend_guid INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (user_guid, friend_guid)
            )
            """
        )

        existing = conn.execute("SELECT COUNT(*) AS cnt FROM users").fetchone()["cnt"]
        if existing == 0:
            for u in INITIAL_USERS:
                conn.execute(
                    """
                    INSERT INTO users (guid, username, password, name, email, location, briefdescription, description, avatar_color)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        u["guid"],
                        u["username"],
                        u["password"],
                        u["name"],
                        u["email"],
                        u["location"],
                        u["briefdescription"],
                        u["description"],
                        u["avatar_color"],
                    ),
                )
    conn.close()


def get_all_users():
    conn = get_db()
    rows = conn.execute("SELECT * FROM users ORDER BY guid ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_by_guid(guid: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE guid = ?", (guid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_username(username: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username.lower(),)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_friends_of(user_guid: int):
    conn = get_db()
    rows = conn.execute(
        """
        SELECT u.* FROM friendships f
        JOIN users u ON u.guid = f.friend_guid
        WHERE f.user_guid = ?
        ORDER BY u.guid ASC
        """,
        (user_guid,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def is_friend(user_guid: int, friend_guid: int) -> bool:
    conn = get_db()
    row = conn.execute(
        "SELECT 1 FROM friendships WHERE user_guid = ? AND friend_guid = ?",
        (user_guid, friend_guid),
    ).fetchone()
    conn.close()
    return row is not None


def add_friendship(user_guid: int, friend_guid: int):
    if user_guid == friend_guid:
        return
    now = time.strftime("%H:%M:%S %d/%m/%Y")
    conn = get_db()
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO friendships (user_guid, friend_guid, created_at) VALUES (?, ?, ?)",
            (user_guid, friend_guid, now),
        )
        conn.execute(
            "INSERT OR IGNORE INTO friendships (user_guid, friend_guid, created_at) VALUES (?, ?, ?)",
            (friend_guid, user_guid, now),
        )
    conn.close()


def render_layout(title: str, current_user: dict, body_html: str, flash_msg: str = "", flash_type: str = "info") -> str:
    users = get_all_users()
    ts = str(int(time.time()))
    token = f"elgg_token_{current_user['guid']}_9f8e7d6c5b4a"

    elgg_script = f"""
    <script>
      // Đối tượng toàn cục tương thích chuẩn mạng xã hội Elgg (SEED Labs)
      window.elgg = {{
        session: {{
          user: {{
            guid: {current_user['guid']},
            name: {json.dumps(current_user['name'], ensure_ascii=False)},
            username: {json.dumps(current_user['username'], ensure_ascii=False)}
          }}
        }},
        security: {{
          token: {{
            __elgg_ts: {json.dumps(ts)},
            __elgg_token: {json.dumps(token)}
          }}
        }}
      }};
    </script>
    """

    switch_options = []
    for u in users:
        selected = "selected" if u["guid"] == current_user["guid"] else ""
        switch_options.append(
            f'<option value="{u["guid"]}" {selected}>{html.escape(u["name"])} (@{html.escape(u["username"])} - GUID: {u["guid"]})</option>'
        )

    flash_html = ""
    if flash_msg:
        bg = "#dcfce7" if flash_type == "success" else "#fee2e2" if flash_type == "error" else "#dbeafe"
        fg = "#166534" if flash_type == "success" else "#991b1b" if flash_type == "error" else "#1e40af"
        border = "#86efac" if flash_type == "success" else "#fca5a5" if flash_type == "error" else "#93c5fd"
        flash_html = f"""
        <div style="background:{bg};color:{fg};border:1px solid {border};padding:12px 16px;border-radius:8px;margin-bottom:20px;font-weight:500;">
          {html.escape(flash_msg)}
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} — Elgg Social Network Lab</title>
  {elgg_script}
  <style>
    :root {{
      --primary: #1d4ed8;
      --primary-hover: #1e40af;
      --bg: #f1f5f9;
      --card: #ffffff;
      --border: #e2e8f0;
      --text: #0f172a;
      --muted: #64748b;
      --danger: #dc2626;
      --success: #16a34a;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    .topbar {{
      background: #0f172a;
      color: #f8fafc;
      padding: 8px 20px;
      font-size: 0.85rem;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
    }}
    .topbar-controls {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .topbar select {{
      padding: 4px 8px;
      border-radius: 6px;
      border: 1px solid #334155;
      background: #1e293b;
      color: #f8fafc;
      font-size: 0.84rem;
    }}
    .navbar {{
      background: var(--primary);
      color: #ffffff;
      padding: 14px 20px;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
    }}
    .navbar-inner {{
      max-width: 1120px;
      margin: 0 auto;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
    }}
    .brand {{
      font-size: 1.35rem;
      font-weight: 700;
      color: #ffffff;
      text-decoration: none;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .nav-links {{
      display: flex;
      gap: 18px;
      align-items: center;
      flex-wrap: wrap;
    }}
    .nav-links a {{
      color: #e0e7ff;
      text-decoration: none;
      font-weight: 600;
      font-size: 0.95rem;
      padding: 6px 10px;
      border-radius: 6px;
    }}
    .nav-links a:hover {{
      background: rgba(255, 255, 255, 0.14);
      color: #ffffff;
    }}
    .container {{
      max-width: 1120px;
      margin: 24px auto;
      padding: 0 20px 48px;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 22px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 8px 16px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.9rem;
      text-decoration: none;
      border: none;
      cursor: pointer;
    }}
    .btn-primary {{ background: var(--primary); color: #ffffff; }}
    .btn-primary:hover {{ background: var(--primary-hover); }}
    .btn-success {{ background: var(--success); color: #ffffff; }}
    .btn-danger {{ background: var(--danger); color: #ffffff; }}
    .btn-outline {{
      background: #ffffff;
      color: var(--text);
      border: 1px solid var(--border);
    }}
    .btn-outline:hover {{ background: #f8fafc; }}
    .avatar {{
      width: 64px;
      height: 64px;
      border-radius: 50%;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      font-weight: 700;
      font-size: 1.5rem;
      flex-shrink: 0;
    }}
    .profile-layout {{
      display: grid;
      grid-template-columns: 310px 1fr;
      gap: 22px;
    }}
    @media (max-width: 820px) {{
      .profile-layout {{ grid-template-columns: 1fr; }}
    }}
    .field-block {{
      padding: 14px 16px;
      border: 1px solid var(--border);
      border-radius: 10px;
      margin-bottom: 14px;
      background: #f8fafc;
    }}
    .field-label {{
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--muted);
      font-weight: 700;
      margin-bottom: 6px;
      display: flex;
      justify-content: space-between;
    }}
    .field-value {{
      font-size: 0.98rem;
      color: var(--text);
      word-break: break-word;
    }}
    .badge {{
      display: inline-block;
      padding: 3px 9px;
      border-radius: 999px;
      font-size: 0.76rem;
      font-weight: 600;
    }}
    .badge-vuln {{
      background: #fef3c7;
      color: #92400e;
      border: 1px solid #fde68a;
    }}
    input[type="text"], input[type="password"], textarea, select.form-control {{
      width: 100%;
      padding: 10px 12px;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      font-size: 0.95rem;
      font-family: inherit;
    }}
    label.form-label {{
      display: block;
      font-weight: 600;
      margin-bottom: 6px;
      font-size: 0.92rem;
    }}
  </style>
</head>
<body>
  <!-- Thanh công cụ hỗ trợ thực hành Lab -->
  <div class="topbar">
    <div>
      <span>🎓 <strong>Môi trường thực hành Elgg Social Network</strong></span>
      <span style="color:#94a3b8;margin-left:10px;">| Đang đăng nhập: <strong style="color:#38bdf8;">{html.escape(current_user['name'])}</strong> (GUID: <code>{current_user['guid']}</code>)</span>
    </div>
    <div class="topbar-controls">
      <form method="POST" action="/switch-user" style="margin:0;display:inline-flex;align-items:center;gap:6px;">
        <label for="quick-switch" style="color:#cbd5e1;">Đổi nhanh tài khoản:</label>
        <select id="quick-switch" name="guid" onchange="this.form.submit()">
          {"".join(switch_options)}
        </select>
      </form>
      <a href="/login" style="color:#93c5fd;text-decoration:none;padding:4px 8px;">Đăng nhập bằng mật khẩu</a>
      <form method="POST" action="/reset-lab" style="margin:0;" onsubmit="return confirm('Khôi phục toàn bộ hồ sơ và bạn bè về trạng thái gốc?');">
        <button type="submit" class="btn btn-danger" style="padding:4px 10px;font-size:0.8rem;">🔄 Reset dữ liệu gốc</button>
      </form>
    </div>
  </div>

  <!-- Thanh điều hướng chính của Mạng xã hội -->
  <nav class="navbar">
    <div class="navbar-inner">
      <a class="brand" href="/">🌐 Elgg Social Network</a>
      <div class="nav-links">
        <a href="/">👥 Thành viên (Members)</a>
        <a href="/profile/{html.escape(current_user['username'])}">👤 Hồ sơ của tôi ({html.escape(current_user['name'])})</a>
        <a href="/profile/{html.escape(current_user['username'])}/edit">✏️ Sửa hồ sơ (Edit Profile)</a>
        <a href="/friends/{html.escape(current_user['username'])}">🤝 Bạn bè (Friends)</a>
      </div>
    </div>
  </nav>

  <main class="container">
    {flash_html}
    {body_html}
  </main>
</body>
</html>
"""


class SocialLabHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        super().end_headers()

    def get_current_user(self) -> dict:
        cookie_header = self.headers.get("Cookie", "")
        c = cookies.SimpleCookie()
        try:
            c.load(cookie_header)
        except cookies.CookieError:
            pass
        if "elgg_uid" in c:
            try:
                uid = int(c["elgg_uid"].value)
                user = get_user_by_guid(uid)
                if user:
                    return user
            except ValueError:
                pass
        # Mặc định đăng nhập tài khoản Samy (59) khi mới mở lần đầu
        return get_user_by_guid(59) or get_all_users()[0]

    def send_html(self, html_content: str, status: int = 200, set_uid: int | None = None):
        data = html_content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        if set_uid is not None:
            self.send_header("Set-Cookie", f"elgg_uid={set_uid}; Path=/; SameSite=Lax")
        self.end_headers()
        self.wfile.write(data)

    def redirect(self, location: str, set_uid: int | None = None):
        self.send_response(303)
        self.send_header("Location", location)
        if set_uid is not None:
            self.send_header("Set-Cookie", f"elgg_uid={set_uid}; Path=/; SameSite=Lax")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        qs = parse_qs(parsed.query)
        current_user = self.get_current_user()
        msg = qs.get("msg", [""])[0]
        msg_type = qs.get("type", ["info"])[0]

        # 1. Endpoint kết bạn chuẩn Elgg: GET /action/friends/add?friend=<guid>
        if path == "/action/friends/add":
            friend_guid_str = qs.get("friend", [""])[0]
            try:
                friend_guid = int(friend_guid_str)
                target_friend = get_user_by_guid(friend_guid)
                if target_friend:
                    add_friendship(current_user["guid"], friend_guid)
            except ValueError:
                pass

            # Nếu gọi bằng trình duyệt thông thường thì redirect về trang profile, nếu gọi bằng AJAX thì trả JSON/200
            if "XMLHttpRequest" in self.headers.get("X-Requested-With", "") or self.headers.get("Accept", "") == "*/*":
                body = json.dumps({"status": 0, "message": "Friend added"}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            ref = self.headers.get("Referer") or f"/profile/{current_user['username']}"
            self.redirect(ref)
            return

        # 2. Trang chủ / Danh sách thành viên
        if path in ("/", "/members"):
            users = get_all_users()
            cards = []
            for u in users:
                friends = get_friends_of(u["guid"])
                already_friend = is_friend(current_user["guid"], u["guid"])
                is_self = u["guid"] == current_user["guid"]

                if is_self:
                    action_btn = f'<a class="btn btn-outline" href="/profile/{u["username"]}/edit">✏️ Sửa hồ sơ</a>'
                elif already_friend:
                    action_btn = '<span class="badge" style="background:#dcfce7;color:#166534;padding:6px 12px;">✓ Đã kết bạn</span>'
                else:
                    action_btn = f'<a class="btn btn-success" href="/action/friends/add?friend={u["guid"]}">+ Kết bạn</a>'

                cards.append(
                    f"""
                    <div class="card" style="display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;">
                      <div style="display:flex;align-items:center;gap:16px;">
                        <div class="avatar" style="background:{u['avatar_color']};">{html.escape(u['name'][0])}</div>
                        <div>
                          <h3 style="margin:0 0 4px;font-size:1.12rem;">
                            <a href="/profile/{html.escape(u['username'])}" style="color:var(--primary);text-decoration:none;">
                              {html.escape(u['name'])}
                            </a>
                            <span style="font-size:0.84rem;color:var(--muted);font-weight:normal;">(@{html.escape(u['username'])} • GUID: {u['guid']})</span>
                          </h3>
                          <div style="font-size:0.9rem;color:var(--muted);margin-bottom:4px;">
                            <strong>Brief Description:</strong> {html.escape(u['briefdescription'][:80])}{'...' if len(u['briefdescription']) > 80 else ''}
                          </div>
                          <div style="font-size:0.85rem;color:#475569;">
                            <strong>About me:</strong> {html.escape(u['description'][:100])}
                          </div>
                          <div style="font-size:0.82rem;color:var(--primary);margin-top:4px;font-weight:600;">
                            🤝 Số bạn bè: {len(friends)}
                          </div>
                        </div>
                      </div>
                      <div style="display:flex;gap:8px;align-items:center;">
                        <a class="btn btn-primary" href="/profile/{html.escape(u['username'])}">Xem Profile</a>
                        {action_btn}
                      </div>
                    </div>
                    """
                )

            body = f"""
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;flex-wrap:wrap;gap:12px;">
              <div>
                <h1 style="margin:0;font-size:1.5rem;">Danh sách thành viên mạng xã hội (Members)</h1>
                <p style="margin:4px 0 0;color:var(--muted);">Bấm vào tên thành viên hoặc nút <strong>Xem Profile</strong> để truy cập trang hồ sơ cá nhân của thành viên đó.</p>
              </div>
            </div>
            <div style="display:grid;gap:14px;">
              {"".join(cards)}
            </div>
            """
            self.send_html(render_layout("Danh sách thành viên", current_user, body, msg, msg_type))
            return

        # 3. Trang Đăng nhập (/login)
        if path == "/login":
            body = """
            <div class="card" style="max-width:460px;margin:20px auto;">
              <h1 style="margin:0 0 8px;font-size:1.35rem;">Đăng nhập tài khoản</h1>
              <p style="margin:0 0 18px;color:var(--muted);font-size:0.9rem;">
                Tài khoản mẫu: <code>alice</code> / <code>seedalice</code>, <code>boby</code> / <code>seedboby</code>, <code>charlie</code> / <code>seedcharlie</code>, <code>samy</code> / <code>seedsamy</code>
              </p>
              <form method="POST" action="/login">
                <div style="margin-bottom:14px;">
                  <label class="form-label" for="username">Tên đăng nhập (Username)</label>
                  <input id="username" name="username" type="text" required placeholder="alice / boby / charlie / samy">
                </div>
                <div style="margin-bottom:18px;">
                  <label class="form-label" for="password">Mật khẩu (Password)</label>
                  <input id="password" name="password" type="password" required placeholder="seed...">
                </div>
                <button type="submit" class="btn btn-primary" style="width:100%;">Đăng nhập</button>
              </form>
            </div>
            """
            self.send_html(render_layout("Đăng nhập", current_user, body, msg, msg_type))
            return

        # 4. Trang Xem Profile (/profile/<username>)
        if path.startswith("/profile/") and not path.endswith("/edit"):
            username = path.split("/profile/", 1)[1]
            profile_user = get_user_by_username(username)
            if not profile_user:
                self.send_html(render_layout("Không tìm thấy", current_user, "<div class='card'><h2>404 - Không tìm thấy thành viên</h2></div>"), 404)
                return

            friends = get_friends_of(profile_user["guid"])
            is_self = profile_user["guid"] == current_user["guid"]
            already_friend = is_friend(current_user["guid"], profile_user["guid"])

            if is_self:
                profile_actions = f'<a class="btn btn-primary" style="width:100%;" href="/profile/{html.escape(profile_user["username"])}/edit">✏️ Chỉnh sửa hồ sơ (Edit Profile)</a>'
            elif already_friend:
                profile_actions = '<div class="btn btn-outline" style="width:100%;cursor:default;color:var(--success);border-color:#86efac;background:#f0fdf4;">✓ Đã là bạn bè (Friends)</div>'
            else:
                profile_actions = f'<a class="btn btn-success" style="width:100%;" href="/action/friends/add?friend={profile_user["guid"]}">+ Kết bạn (Add Friend)</a>'

            if friends:
                friends_list_html = "".join(
                    f"""
                    <a href="/profile/{html.escape(f['username'])}" style="display:flex;align-items:center;gap:10px;padding:8px;border-radius:8px;text-decoration:none;color:var(--text);border:1px solid var(--border);margin-bottom:8px;">
                      <div class="avatar" style="width:36px;height:36px;font-size:0.95rem;background:{f['avatar_color']};">{html.escape(f['name'][0])}</div>
                      <div>
                        <div style="font-weight:600;font-size:0.9rem;">{html.escape(f['name'])}</div>
                        <div style="font-size:0.78rem;color:var(--muted);">@{html.escape(f['username'])} (GUID: {f['guid']})</div>
                      </div>
                    </a>
                    """
                    for f in friends
                )
            else:
                friends_list_html = '<p style="color:var(--muted);font-size:0.9rem;margin:0;">Chưa có người bạn nào.</p>'

            # LƯU Ý QUAN TRỌNG THEO ĐỀ BÀI:
            # Trường Brief Description (briefdescription) có lỗ hổng Stored XSS nên được hiển thị trực tiếp không escape!
            brief_raw = profile_user["briefdescription"]
            about_escaped = html.escape(profile_user["description"])

            body = f"""
            <div class="profile-layout">
              <!-- Cột trái: Thông tin định danh & Danh sách bạn bè -->
              <div>
                <div class="card" style="text-align:center;margin-bottom:18px;">
                  <div class="avatar" style="width:88px;height:88px;font-size:2.1rem;background:{profile_user['avatar_color']};margin:0 auto 12px;">
                    {html.escape(profile_user['name'][0])}
                  </div>
                  <h2 style="margin:0 0 4px;">{html.escape(profile_user['name'])}</h2>
                  <p style="margin:0 0 14px;color:var(--muted);font-size:0.9rem;">
                    @{html.escape(profile_user['username'])} • GUID: <strong>{profile_user['guid']}</strong>
                  </p>
                  {profile_actions}
                </div>

                <div class="card">
                  <h3 style="margin:0 0 12px;font-size:1.05rem;">🤝 Danh sách bạn bè ({len(friends)})</h3>
                  {friends_list_html}
                </div>
              </div>

              <!-- Cột phải: Chi tiết hồ sơ (Profile Fields) -->
              <div class="card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;border-bottom:1px solid var(--border);padding-bottom:12px;">
                  <h1 style="margin:0;font-size:1.35rem;">Hồ sơ cá nhân của {html.escape(profile_user['name'])}</h1>
                  <span style="font-size:0.85rem;color:var(--muted);">Profile ID: #{profile_user['guid']}</span>
                </div>

                <!-- Trường Brief Description: Giới hạn 250 ký tự & Có lỗ hổng Stored XSS -->
                <div class="field-block" style="border-color:#fde68a;background:#fffbeb;">
                  <div class="field-label">
                    <span>Brief Description (Mô tả ngắn)</span>
                    <span class="badge badge-vuln">Stored XSS • Độ dài: {len(brief_raw)}/{BRIEF_MAX_LEN} ký tự</span>
                  </div>
                  <div class="field-value" id="profile-briefdescription">
                    {brief_raw}
                  </div>
                </div>

                <!-- Trường About me (description) -->
                <div class="field-block">
                  <div class="field-label">
                    <span>About me (Giới thiệu bản thân)</span>
                    <span>Field: <code>description</code></span>
                  </div>
                  <div class="field-value" id="profile-description" style="white-space:pre-wrap;">{about_escaped}</div>
                </div>

                <div class="field-block">
                  <div class="field-label"><span>Contact Email</span></div>
                  <div class="field-value">{html.escape(profile_user['email'])}</div>
                </div>

                <div class="field-block" style="margin-bottom:0;">
                  <div class="field-label"><span>Location</span></div>
                  <div class="field-value">{html.escape(profile_user['location'])}</div>
                </div>
              </div>
            </div>
            """
            self.send_html(render_layout(f"Profile: {profile_user['name']}", current_user, body, msg, msg_type))
            return

        # 5. Trang Chỉnh sửa Profile (/profile/<username>/edit)
        if path.startswith("/profile/") and path.endswith("/edit"):
            username = path.split("/profile/", 1)[1].rsplit("/edit", 1)[0]
            profile_user = get_user_by_username(username)
            if not profile_user:
                self.send_html(render_layout("Không tìm thấy", current_user, "<div class='card'><h2>404 - Không tìm thấy thành viên</h2></div>"), 404)
                return

            ts = str(int(time.time()))
            token = f"elgg_token_{current_user['guid']}_9f8e7d6c5b4a"

            body = f"""
            <div class="card" style="max-width:760px;margin:0 auto;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;border-bottom:1px solid var(--border);padding-bottom:12px;">
                <div>
                  <h1 style="margin:0;font-size:1.35rem;">Chỉnh sửa hồ sơ: {html.escape(profile_user['name'])}</h1>
                  <p style="margin:4px 0 0;color:var(--muted);font-size:0.9rem;">Endpoint xử lý: <code>POST /action/profile/edit</code></p>
                </div>
                <a class="btn btn-outline" href="/profile/{html.escape(profile_user['username'])}">← Quay lại Profile</a>
              </div>

              <form method="POST" action="/action/profile/edit">
                <input type="hidden" name="__elgg_ts" value="{ts}">
                <input type="hidden" name="__elgg_token" value="{token}">
                <input type="hidden" name="guid" value="{profile_user['guid']}">

                <div style="margin-bottom:16px;">
                  <label class="form-label" for="name-input">Tên hiển thị (Display Name - <code>name</code>)</label>
                  <input id="name-input" name="name" type="text" value="{html.escape(profile_user['name'])}" required>
                </div>

                <div style="margin-bottom:16px;padding:14px;border:1px solid #fde68a;background:#fffbeb;border-radius:10px;">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                    <label class="form-label" for="brief-input" style="margin:0;">
                      Brief Description (<code>briefdescription</code>) — <span style="color:#b45309;">Giới hạn tối đa {BRIEF_MAX_LEN} ký tự</span>
                    </label>
                    <span id="brief-counter" style="font-size:0.85rem;font-weight:700;color:#b45309;">
                      {len(profile_user['briefdescription'])} / {BRIEF_MAX_LEN} ký tự
                    </span>
                  </div>
                  <input
                    id="brief-input"
                    name="briefdescription"
                    type="text"
                    maxlength="{BRIEF_MAX_LEN}"
                    value="{html.escape(profile_user['briefdescription'])}"
                    oninput="document.getElementById('brief-counter').textContent = this.value.length + ' / {BRIEF_MAX_LEN} ký tự';"
                    placeholder="Nhập mô tả ngắn hoặc payload XSS (tối đa 250 ký tự)..."
                  >
                  <p style="margin:6px 0 0;font-size:0.82rem;color:#92400e;">
                    💡 Do giới hạn {BRIEF_MAX_LEN} ký tự, trường này không đủ chứa toàn bộ mã Self-contained XSS Worm mà cần nhúng thẻ <code>&lt;script src=&quot;http://...:8000/worm.js&quot;&gt;&lt;/script&gt;</code>.
                  </p>
                </div>

                <div style="margin-bottom:18px;">
                  <label class="form-label" for="desc-input">About me (Giới thiệu bản thân - <code>description</code>)</label>
                  <textarea id="desc-input" name="description" rows="4">{html.escape(profile_user['description'])}</textarea>
                </div>

                <div style="display:flex;gap:10px;">
                  <button type="submit" class="btn btn-primary">💾 Lưu hồ sơ (Save Profile)</button>
                  <a class="btn btn-outline" href="/profile/{html.escape(profile_user['username'])}">Hủy</a>
                </div>
              </form>
            </div>
            """
            self.send_html(render_layout(f"Edit Profile: {profile_user['name']}", current_user, body, msg, msg_type))
            return

        # 6. Trang Bạn bè (/friends/<username>)
        if path.startswith("/friends/"):
            username = path.split("/friends/", 1)[1]
            target_user = get_user_by_username(username) or current_user
            friends = get_friends_of(target_user["guid"])
            items = "".join(
                f"""
                <div class="card" style="display:flex;justify-content:space-between;align-items:center;">
                  <div style="display:flex;align-items:center;gap:14px;">
                    <div class="avatar" style="background:{f['avatar_color']};">{html.escape(f['name'][0])}</div>
                    <div>
                      <h3 style="margin:0;"><a href="/profile/{html.escape(f['username'])}" style="color:var(--primary);text-decoration:none;">{html.escape(f['name'])}</a></h3>
                      <div style="color:var(--muted);font-size:0.88rem;">@{html.escape(f['username'])} • GUID: {f['guid']}</div>
                    </div>
                  </div>
                  <a class="btn btn-primary" href="/profile/{html.escape(f['username'])}">Xem Profile</a>
                </div>
                """
                for f in friends
            )
            if not items:
                items = '<div class="card"><p style="margin:0;color:var(--muted);">Chưa có bạn bè nào trong danh sách.</p></div>'

            body = f"""
            <h1 style="margin:0 0 16px;font-size:1.4rem;">🤝 Danh sách bạn bè của {html.escape(target_user['name'])} ({len(friends)})</h1>
            <div style="display:grid;gap:12px;">{items}</div>
            """
            self.send_html(render_layout(f"Friends: {target_user['name']}", current_user, body, msg, msg_type))
            return

        self.send_html(render_layout("404", current_user, "<div class='card'><h2>404 - Trang không tồn tại</h2></div>"), 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8", errors="replace")
        form = parse_qs(raw_body, keep_blank_values=True)
        current_user = self.get_current_user()

        # 1. Chuyển nhanh tài khoản trên thanh công cụ
        if path == "/switch-user":
            guid_str = form.get("guid", ["59"])[0]
            try:
                target_user = get_user_by_guid(int(guid_str))
                if target_user:
                    self.redirect(f"/profile/{target_user['username']}", set_uid=target_user["guid"])
                    return
            except ValueError:
                pass
            self.redirect("/")
            return

        # 2. Đăng nhập bằng username / password
        if path == "/login":
            username = form.get("username", [""])[0].strip().lower()
            password = form.get("password", [""])[0].strip()
            user = get_user_by_username(username)
            if user and user["password"] == password:
                self.redirect(f"/profile/{user['username']}?msg=Đăng+nhập+thành+công&type=success", set_uid=user["guid"])
            else:
                self.redirect("/login?msg=Sai+tên+đăng+nhập+hoặc+mật+khẩu&type=error")
            return

        # 3. Reset dữ liệu gốc của bài Lab
        if path == "/reset-lab":
            init_db(reset=True)
            self.redirect("/?msg=Đã+khôi+phục+toàn+bộ+hồ+sơ+và+danh+sách+bạn+bè+về+trạng+thái+ban+đầu!&type=success")
            return

        # 4. Endpoint cập nhật Profile chuẩn Elgg: POST /action/profile/edit
        if path == "/action/profile/edit":
            guid_str = form.get("guid", [str(current_user["guid"])])[0]
            try:
                target_guid = int(guid_str)
            except ValueError:
                target_guid = current_user["guid"]

            target_user = get_user_by_guid(target_guid) or current_user
            new_name = form.get("name", [target_user["name"]])[0].strip() or target_user["name"]
            new_brief = form.get("briefdescription", [target_user["briefdescription"]])[0]
            new_desc = form.get("description", [target_user["description"]])[0]

            # Kiểm tra giới hạn tối đa 250 ký tự trên trường Brief Description
            if len(new_brief) > BRIEF_MAX_LEN:
                self.redirect(
                    f"/profile/{target_user['username']}/edit?msg=Lỗi:+Trường+Brief+Description+vượt+quá+giới+hạn+250+ký+tự+({len(new_brief)}/250)!&type=error"
                )
                return

            conn = get_db()
            with conn:
                conn.execute(
                    "UPDATE users SET name = ?, briefdescription = ?, description = ? WHERE guid = ?",
                    (new_name, new_brief, new_desc, target_user["guid"]),
                )
            conn.close()

            self.redirect(f"/profile/{target_user['username']}?msg=Đã+lưu+thông+tin+hồ+sơ+cá+nhân!&type=success")
            return

        self.send_html("404 Not Found", 404)


def get_local_ips():
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


class _WSGIHeaderAdapter:
    def __init__(self, headers_dict: dict):
        self._headers = {k.lower(): v for k, v in headers_dict.items()}

    def get(self, name: str, default: str = "") -> str:
        return self._headers.get(name.lower(), default)


class _WSGIRequestShim(SocialLabHandler):
    """Bộ chuyển đổi giúp chạy trực tiếp SocialLabHandler trên PythonAnywhere (chuẩn WSGI)."""

    def __init__(self, environ: dict):
        path_info = environ.get("PATH_INFO", "/") or "/"
        query_string = environ.get("QUERY_STRING", "")
        self.path = f"{path_info}?{query_string}" if query_string else path_info
        self.command = environ.get("REQUEST_METHOD", "GET").upper()

        hdrs = {}
        if "CONTENT_TYPE" in environ and environ["CONTENT_TYPE"]:
            hdrs["Content-Type"] = environ["CONTENT_TYPE"]
        if "CONTENT_LENGTH" in environ and environ["CONTENT_LENGTH"]:
            hdrs["Content-Length"] = environ["CONTENT_LENGTH"]
        for k, v in environ.items():
            if k.startswith("HTTP_"):
                header_name = k[5:].replace("_", "-")
                hdrs[header_name] = v
        self.headers = _WSGIHeaderAdapter(hdrs)

        wsgi_input = environ.get("wsgi.input")
        content_len = int(hdrs.get("Content-Length") or "0")
        body_bytes = wsgi_input.read(content_len) if (wsgi_input and content_len > 0) else b""
        self.rfile = io.BytesIO(body_bytes)
        self.wfile = io.BytesIO()

        self._status_code = 200
        self._response_headers = []

    def send_response(self, code: int, message: str | None = None):
        self._status_code = code

    def send_header(self, keyword: str, value: str):
        self._response_headers.append((keyword, value))

    def end_headers(self):
        self._response_headers.append(("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0"))


def application(environ: dict, start_response):
    """Entry-point chuẩn WSGI dùng cho PythonAnywhere."""
    init_db(reset=False)
    shim = _WSGIRequestShim(environ)
    if shim.command == "POST":
        shim.do_POST()
    else:
        shim.do_GET()

    status_map = {
        200: "200 OK",
        303: "303 See Other",
        400: "400 Bad Request",
        404: "404 Not Found",
        500: "500 Internal Server Error",
    }
    status_line = status_map.get(shim._status_code, f"{shim._status_code} OK")
    start_response(status_line, shim._response_headers)
    return [shim.wfile.getvalue()]


# Bí danh cho các dịch vụ tìm biến `app`
app = application


def main():
    init_db(reset=False)
    server = HTTPServer(("0.0.0.0", PORT), SocialLabHandler)
    print("=" * 72)
    print("[+] TRANG WEB MẠNG XÃ HỘI MỤC TIÊU (Elgg Social Network Lab) ĐANG CHẠY")
    print(f"[+] Cổng (Port): {PORT}")
    print("-" * 72)
    for ip in get_local_ips():
        print(f"    • Mở trên trình duyệt: http://{ip}:{PORT}/")
    print("=" * 72, flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    main()
