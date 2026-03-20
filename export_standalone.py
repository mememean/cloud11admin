#!/usr/bin/env python3
"""
Cloud 11 — Export standalone website
Run:   python3 export_standalone.py
Output: site.html  (single file, no server needed — share with anyone)
"""

import json, base64, re
from pathlib import Path

BASE       = Path(__file__).parent
DATA_FILE  = BASE / "data"   / "content.json"
ADMIN_FILE = BASE / "admin"  / "index.html"
OUT        = BASE / "site.html"

MIME = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png",  ".gif":  "image/gif",
    ".svg": "image/svg+xml", ".webp": "image/webp",
}

# ── 1. Read content & admin ────────────────────────────────────
with open(DATA_FILE, encoding="utf-8") as f:
    content = json.load(f)

with open(ADMIN_FILE, encoding="utf-8") as f:
    admin_html = f.read()

# Extract largest <script> block (the main one)
blocks = re.findall(r"<script[^>]*>(.*?)</script>", admin_html, re.DOTALL)
main_script = max(blocks, key=len) if blocks else ""

# ── 2. Collect all image paths from data ──────────────────────
def collect_paths(obj):
    paths = set()
    if isinstance(obj, dict):
        for v in obj.values():
            if isinstance(v, str) and v.startswith("/uploads/"):
                paths.add(v)
            else:
                paths.update(collect_paths(v))
    elif isinstance(obj, list):
        for item in obj:
            paths.update(collect_paths(item))
    return paths

paths = collect_paths(content)
# Hardcoded paths inside section builders
paths.update(["/uploads/bgspace.png", "/uploads/logo-gradient.svg"])

# ── 3. Build base64 image map ─────────────────────────────────
img_map = {}  # "http://localhost:8080/uploads/x.png" → "data:image/png;base64,..."
print("Embedding images:")
for path in sorted(paths):
    fp = BASE / path.lstrip("/")
    if fp.exists():
        mime = MIME.get(fp.suffix.lower(), "image/octet-stream")
        b64  = base64.b64encode(fp.read_bytes()).decode()
        img_map[f"http://localhost:8080{path}"] = f"data:{mime};base64,{b64}"
        print(f"  ✓  {path}  ({fp.stat().st_size // 1024} KB)")
    else:
        print(f"  ✗  {path}  (missing)")

# ── 4. Build HTML ──────────────────────────────────────────────
data_json    = json.dumps(content,  ensure_ascii=False)
img_map_json = json.dumps(img_map,  ensure_ascii=False)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Cloud 11</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; line-height: 1.5; overflow-x: hidden; }}
img {{ display: block; width: 100%; height: 100%; object-fit: cover; }}
a {{ cursor: pointer; }}
</style>
</head>
<body>

<!-- CMS section builders (extracted from admin) -->
<script>
{main_script}
</script>

<!-- Export runtime: override server-deps, embed images, render -->
<script>
(function() {{
  // ── Image map: localhost URLs → base64 data URIs ──────────
  var _IMG = {img_map_json};

  // Override absUrl to serve embedded images
  window.absUrl = function(u) {{
    if (!u) return '';
    var full = u.startsWith('http') ? u : 'http://localhost:8080' + u;
    return _IMG[full] || full;
  }};

  // Silence admin-specific functions that reference missing DOM
  var _noop = function() {{}};
  window.loadContent    = async function() {{}};
  window.showPage       = _noop;
  window.markDirty      = _noop;
  window.schedulePreviewRefresh = _noop;
  window.refreshPreview = _noop;
  window.populateAll    = _noop;
  window.clearDirty     = _noop;

  // Inject content data
  data = {data_json};

  // Helper: render HTML + re-execute any injected <script> tags
  function renderWithScripts(container, html) {{
    container.innerHTML = html;
    container.querySelectorAll('script').forEach(function(old) {{
      var s = document.createElement('script');
      s.textContent = old.textContent;
      old.parentNode.replaceChild(s, old);
    }});
  }}

  document.addEventListener('DOMContentLoaded', function() {{
    try {{
      var html = buildDashboardPreview(data);
      renderWithScripts(document.body, html);
    }} catch(e) {{
      document.body.innerHTML =
        '<div style="padding:40px;font-family:monospace;color:red">' +
        '<b>Export render error:</b><br>' + e.message + '</div>';
      console.error(e);
    }}
  }});
}})();
</script>

</body>
</html>"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

size_kb = OUT.stat().st_size / 1024
print(f"\n✓  Exported → {OUT}")
print(f"   Size: {size_kb:.0f} KB")
print(f"\n   Share 'site.html' — opens in any browser, no server needed.")
