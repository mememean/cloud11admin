#!/usr/bin/env python3
"""
Cloud 11 CMS Server
Run: python3 server.py
Then open: http://localhost:8080/admin/
"""

import http.server
import json
import os
import urllib.parse
import shutil
import mimetypes
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "content.json"
UPLOAD_DIR = BASE_DIR / "uploads"
ADMIN_DIR = BASE_DIR / "admin"
PORT = int(os.environ.get("PORT", 8080))

UPLOAD_DIR.mkdir(exist_ok=True)


def read_content():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def write_content(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class CMSHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_cors(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_cors()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)

        # API endpoints
        if path == "/api/content":
            try:
                data = read_content()
                self.send_json(data)
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
            return

        if path.startswith("/uploads/"):
            file_path = BASE_DIR / path.lstrip("/")
            self.serve_file(file_path)
            return

        # Public website
        if path == "/":
            self.serve_file(BASE_DIR / "public" / "index.html")
            return

        # Admin UI
        if path == "/admin" or path == "/admin/":
            file_path = ADMIN_DIR / "index.html"
        elif path.startswith("/admin/"):
            file_path = ADMIN_DIR / path[len("/admin/"):]
        else:
            file_path = BASE_DIR / path.lstrip("/")

        self.serve_file(file_path)

    def serve_viewer(self):
        import re, json
        try:
            with open(ADMIN_DIR / "index.html", encoding="utf-8") as f:
                admin_html = f.read()
            blocks = re.findall(r"<script[^>]*>(.*?)</script>", admin_html, re.DOTALL)
            main_script = max(blocks, key=len) if blocks else ""
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Cloud 11</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;line-height:1.5;overflow-x:hidden}}
img{{display:block;width:100%;height:100%;object-fit:cover}}
a{{cursor:pointer}}
</style>
</head>
<body>
<script>{main_script}</script>
<script>
(function(){{
  var _noop=function(){{}};
  window.loadContent=async function(){{}};
  window.showPage=_noop;
  window.markDirty=_noop;
  window.schedulePreviewRefresh=_noop;
  window.refreshPreview=_noop;
  window.populateAll=_noop;
  window.clearDirty=_noop;
  function renderWithScripts(container,html){{
    container.innerHTML=html;
    container.querySelectorAll('script').forEach(function(old){{
      var s=document.createElement('script');
      s.textContent=old.textContent;
      old.parentNode.replaceChild(s,old);
    }});
  }}
  document.addEventListener('DOMContentLoaded',function(){{
    fetch('/api/content')
      .then(function(r){{return r.json();}})
      .then(function(data){{
        var html=buildDashboardPreview(data);
        renderWithScripts(document.body,html);
      }})
      .catch(function(e){{
        document.body.innerHTML='<div style="padding:40px;color:red">Error: '+e.message+'</div>';
      }});
  }});
}})();
</script>
</body>
</html>"""
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def serve_file(self, file_path):
        file_path = Path(file_path)
        if not file_path.exists() or not file_path.is_file():
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return

        mime, _ = mimetypes.guess_type(str(file_path))
        mime = mime or "application/octet-stream"

        with open(file_path, "rb") as f:
            data = f.read()

        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", len(data))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/content":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body.decode("utf-8"))
                write_content(data)
                self.send_json({"ok": True})
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
            return

        if path == "/api/upload":
            try:
                content_type = self.headers.get("Content-Type", "")
                if "multipart/form-data" not in content_type:
                    self.send_json({"error": "Expected multipart/form-data"}, 400)
                    return

                # Parse boundary
                boundary = None
                for part in content_type.split(";"):
                    part = part.strip()
                    if part.startswith("boundary="):
                        boundary = part[9:].strip()
                        break

                if not boundary:
                    self.send_json({"error": "No boundary found"}, 400)
                    return

                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length)

                # Simple multipart parser
                boundary_bytes = ("--" + boundary).encode()
                parts = body.split(boundary_bytes)

                saved_files = []
                for part in parts[1:]:
                    if part in (b"", b"--\r\n", b"--"):
                        continue
                    if part.startswith(b"--"):
                        continue

                    # Split headers and content
                    if b"\r\n\r\n" in part:
                        headers_raw, content = part.split(b"\r\n\r\n", 1)
                    elif b"\n\n" in part:
                        headers_raw, content = part.split(b"\n\n", 1)
                    else:
                        continue

                    # Remove exactly the trailing \r\n before the next boundary
                    if content.endswith(b"\r\n"):
                        content = content[:-2]

                    headers_str = headers_raw.decode("utf-8", errors="ignore")

                    # Extract filename
                    filename = None
                    for line in headers_str.split("\r\n"):
                        if "filename=" in line:
                            idx = line.index("filename=")
                            filename = line[idx + 9:].strip().strip('"')
                            break

                    if not filename or not content:
                        continue

                    # Sanitize filename
                    filename = os.path.basename(filename)
                    save_path = UPLOAD_DIR / filename

                    # Avoid overwriting — add suffix if needed
                    stem = Path(filename).stem
                    suffix = Path(filename).suffix
                    counter = 1
                    while save_path.exists():
                        save_path = UPLOAD_DIR / f"{stem}_{counter}{suffix}"
                        counter += 1

                    with open(save_path, "wb") as f:
                        f.write(content)

                    saved_files.append(f"/uploads/{save_path.name}")

                if saved_files:
                    self.send_json({"urls": saved_files, "url": saved_files[0]})
                else:
                    self.send_json({"error": "No files saved"}, 400)

            except Exception as e:
                import traceback
                traceback.print_exc()
                self.send_json({"error": str(e)}, 500)
            return

        self.send_json({"error": "Not found"}, 404)

    def do_PUT(self):
        self.do_POST()


if __name__ == "__main__":
    server = http.server.HTTPServer(("", PORT), CMSHandler)
    print(f"Cloud 11 CMS running at http://localhost:{PORT}/admin/")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
