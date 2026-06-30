#!/usr/bin/env python3
"""
Embed data/content.json into admin/index.html as a read-only fallback snapshot.

Why: on static hosts like Vercel there is no Python backend to serve /api/content,
so admin/index.html's loadContent() falls back to a <script id="inline-content-fallback">
tag if the fetch fails. This script (re)writes that tag with the current content.json.

Run this before each `git push` that should update the Vercel snapshot:
    python3 embed_content.py && git add admin/index.html && git commit -m "Refresh Vercel snapshot" && git push
"""

import json
import re
from pathlib import Path

BASE = Path(__file__).parent
ADMIN_FILE = BASE / "admin" / "index.html"
DATA_FILE = BASE / "data" / "content.json"

with open(DATA_FILE, encoding="utf-8") as f:
    content = json.load(f)

content_json = json.dumps(content, ensure_ascii=False).replace("</script>", "<\\/script>")
tag = f'<script type="application/json" id="inline-content-fallback">{content_json}</script>\n'

html = ADMIN_FILE.read_text(encoding="utf-8")

# Replace existing tag if present, else inject right after <body>
if 'id="inline-content-fallback"' in html:
    html = re.sub(
        r'<script type="application/json" id="inline-content-fallback">.*?</script>\n?',
        tag,
        html,
        count=1,
        flags=re.DOTALL,
    )
else:
    html = html.replace("<body>\n", "<body>\n" + tag, 1)

ADMIN_FILE.write_text(html, encoding="utf-8")
print(f"✓ Embedded {DATA_FILE.stat().st_size} bytes of content.json into admin/index.html")
