#!/usr/bin/env python3
"""Generate posts/index.json from Markdown files.

The script intentionally uses a tiny front matter parser instead of external
dependencies, so it works in a static-site folder without setup.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "posts"
INDEX_PATH = POSTS_DIR / "index.json"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9\u4e00-\u9fa5]+", "-", value.strip().lower())
    return slug.strip("-") or "post"


def parse_scalar(value: str):
    value = value.strip().strip('"').strip("'")
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if "," in value:
        return [part.strip() for part in value.split(",") if part.strip()]
    return value


def parse_front_matter(markdown: str) -> tuple[dict, str]:
    if not markdown.startswith("---\n"):
        return {}, markdown

    end = markdown.find("\n---", 4)
    if end == -1:
        return {}, markdown

    raw = markdown[4:end].strip()
    body = markdown[end + 4 :].lstrip()
    data = {}
    for line in raw.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = parse_scalar(value)
    return data, body


def first_heading(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        match = re.match(r"^#\s+(.+)$", line.strip())
        if match:
            return match.group(1).strip()
        match = re.match(r"^##\s+(.+)$", line.strip())
        if match:
            return match.group(1).strip()
    return fallback


def estimate_minutes(markdown: str) -> str:
    text = re.sub(r"[#>*_`\[\]()!<>{}/-]", "", markdown)
    words = len(re.findall(r"[\w\u4e00-\u9fa5]+", text))
    return str(max(1, round(words / 450)))


def post_entry(path: Path) -> dict:
    markdown = path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(markdown)
    title = str(meta.get("title") or first_heading(body, path.stem))
    stat = path.stat()
    date = datetime.fromtimestamp(stat.st_mtime).strftime("%Y年%-m月%-d日")

    return {
        "id": str(meta.get("id") or slugify(path.stem)),
        "title": title,
        "subtitle": str(meta.get("subtitle") or "这篇文章来自 Markdown 文件。"),
        "author": str(meta.get("author") or "林晚舟"),
        "date": str(meta.get("date") or date),
        "minutes": str(meta.get("minutes") or estimate_minutes(body)),
        "cover": str(meta.get("cover") or "Markdown 封面占位"),
        "tags": meta.get("tags") if isinstance(meta.get("tags"), list) else [],
        "status": str(meta.get("status") or "published"),
        "featured": bool(meta.get("featured", False)),
        "file": str(path.relative_to(ROOT)),
    }


def main() -> None:
    POSTS_DIR.mkdir(exist_ok=True)
    posts = [post_entry(path) for path in sorted(POSTS_DIR.glob("*.md"))]
    INDEX_PATH.write_text(
        json.dumps(posts, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {INDEX_PATH.relative_to(ROOT)} with {len(posts)} post(s).", flush=True)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_rss.py")], check=True)


if __name__ == "__main__":
    main()
