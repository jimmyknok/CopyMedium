#!/usr/bin/env python3
"""Import Markdown files and media into this static blog.

Usage:
  python3 scripts/import_markdown_dir.py /path/to/source

The importer copies Markdown files into posts/, copies local image/video files
into assets/imported/<post-id>/, preserves online URLs, rewrites references, and
then rebuilds posts/index.json.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "posts"
ASSETS_DIR = ROOT / "assets" / "imported"
REPORT_PATH = ROOT / "import-report.json"
ONLINE_SCHEMES = {"http", "https", "data", "mailto"}
MEDIA_EXTENSIONS = {
    ".apng",
    ".avif",
    ".gif",
    ".jpeg",
    ".jpg",
    ".mov",
    ".mp4",
    ".mpeg",
    ".ogg",
    ".png",
    ".svg",
    ".webm",
    ".webp",
}


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


def front_matter(data: dict) -> str:
    lines = ["---"]
    for key in (
        "id",
        "title",
        "subtitle",
        "author",
        "date",
        "minutes",
        "cover",
        "tags",
        "status",
        "featured",
    ):
        value = data.get(key)
        if value is None or value == "":
            continue
        if isinstance(value, list):
            value = ", ".join(str(item) for item in value)
        elif isinstance(value, bool):
            value = "true" if value else "false"
        lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def first_heading(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        match = re.match(r"^#{1,2}\s+(.+)$", line.strip())
        if match:
            return match.group(1).strip()
    return fallback


def is_online(url: str) -> bool:
    return urlparse(url).scheme.lower() in ONLINE_SCHEMES


def is_media_path(url: str) -> bool:
    clean = unquote(url.split("#", 1)[0].split("?", 1)[0])
    return Path(clean).suffix.lower() in MEDIA_EXTENSIONS


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 2
    while True:
        candidate = parent / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def resolve_local_ref(source_md: Path, raw_url: str) -> Path | None:
    clean = unquote(raw_url.split("#", 1)[0].split("?", 1)[0])
    if clean.startswith("file://"):
        return Path(urlparse(clean).path)
    candidate = Path(clean)
    if candidate.is_absolute():
        return candidate
    return (source_md.parent / candidate).resolve()


def copy_media(source_md: Path, raw_url: str, post_id: str, report_item: dict) -> str:
    if is_online(raw_url):
        report_item["online"].append(raw_url)
        return raw_url
    if not is_media_path(raw_url):
        return raw_url

    source = resolve_local_ref(source_md, raw_url)
    if not source or not source.exists():
        report_item["missing"].append(raw_url)
        return raw_url

    target_dir = ASSETS_DIR / post_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target = unique_path(target_dir / source.name)
    shutil.copy2(source, target)
    new_url = target.relative_to(ROOT).as_posix()
    report_item["copied"].append({"from": str(source), "to": new_url})
    return new_url


def rewrite_media_refs(markdown: str, source_md: Path, post_id: str, report_item: dict) -> str:
    def replace_markdown_image(match: re.Match) -> str:
        alt, url = match.group(1), match.group(2).strip()
        return f"![{alt}]({copy_media(source_md, url, post_id, report_item)})"

    def replace_src(match: re.Match) -> str:
        before, url, after = match.group(1), match.group(2).strip(), match.group(3)
        return f'{before}{copy_media(source_md, url, post_id, report_item)}{after}'

    markdown = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_markdown_image, markdown)
    markdown = re.sub(
        r"(<(?:img|video|source)\b[^>]*\bsrc=[\"'])([^\"']+)([\"'][^>]*>)",
        replace_src,
        markdown,
        flags=re.IGNORECASE,
    )
    return markdown


def import_markdown(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(raw)
    title = str(meta.get("title") or first_heading(body, path.stem))
    post_id = str(meta.get("id") or slugify(path.stem))
    report_item = {
        "source": str(path),
        "post": f"posts/{post_id}.md",
        "copied": [],
        "online": [],
        "missing": [],
    }
    rewritten = rewrite_media_refs(body, path, post_id, report_item)
    next_meta = {
        "id": post_id,
        "title": title,
        "subtitle": meta.get("subtitle") or "这篇文章由导入脚本整理。",
        "author": meta.get("author") or "林晚舟",
        "date": meta.get("date") or "",
        "minutes": meta.get("minutes") or "",
        "cover": meta.get("cover") or "导入文章封面占位",
        "tags": meta.get("tags") if isinstance(meta.get("tags"), list) else [],
        "status": meta.get("status") or "published",
        "featured": bool(meta.get("featured", False)),
    }
    POSTS_DIR.mkdir(exist_ok=True)
    target = unique_path(POSTS_DIR / f"{post_id}.md")
    if target.stem != post_id:
        next_meta["id"] = target.stem
        report_item["post"] = target.relative_to(ROOT).as_posix()
    target.write_text(front_matter(next_meta) + rewritten, encoding="utf-8")
    return report_item


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Markdown directory into the blog.")
    parser.add_argument("source", help="Directory containing Markdown files")
    args = parser.parse_args()
    source = Path(args.source).expanduser().resolve()
    if not source.exists() or not source.is_dir():
        raise SystemExit(f"Source directory not found: {source}")

    md_files = sorted(source.rglob("*.md"))
    report = {
        "source": str(source),
        "imported": [],
        "summary": {"posts": 0, "copied": 0, "online": 0, "missing": 0},
    }
    for md_file in md_files:
        item = import_markdown(md_file)
        report["imported"].append(item)
        report["summary"]["posts"] += 1
        report["summary"]["copied"] += len(item["copied"])
        report["summary"]["online"] += len(item["online"])
        report["summary"]["missing"] += len(item["missing"])

    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_posts_index.py")], check=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "Imported {posts} post(s), copied {copied} local media, kept {online} online URL(s), missing {missing} resource(s).".format(
            **report["summary"]
        )
    )
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
