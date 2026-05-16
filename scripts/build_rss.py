#!/usr/bin/env python3
"""Generate feed.xml from site.config.json and posts/index.json."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from xml.dom import minidom


ROOT = Path(__file__).resolve().parents[1]
SITE_CONFIG_PATH = ROOT / "site.config.json"
POSTS_INDEX_PATH = ROOT / "posts" / "index.json"
FEED_PATH = ROOT / "feed.xml"

DEFAULT_SITE_CONFIG = {
    "title": "素写",
    "description": "一个极简、可自托管的个人写作平台。",
    "url": "http://localhost:8766/",
    "language": "zh-CN",
    "rss": "feed.xml",
}


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def site_url(site: dict, path: str = "") -> str:
    base = str(site.get("url") or DEFAULT_SITE_CONFIG["url"]).rstrip("/") + "/"
    return base + path.lstrip("/")


def parse_date(value: str, fallback_path: Path | None = None) -> datetime:
    text = str(value or "").strip()
    patterns = (
        (r"^(\d{4})年(\d{1,2})月(\d{1,2})日$", "%Y-%m-%d"),
        (r"^(\d{4})-(\d{1,2})-(\d{1,2})$", "%Y-%m-%d"),
        (r"^(\d{4})/(\d{1,2})/(\d{1,2})$", "%Y-%m-%d"),
    )
    for pattern, fmt in patterns:
        match = re.match(pattern, text)
        if match:
            return datetime.strptime("-".join(match.groups()), fmt).astimezone()

    if fallback_path and fallback_path.exists():
        return datetime.fromtimestamp(fallback_path.stat().st_mtime).astimezone()
    return datetime.now().astimezone()


def append_text(parent: ET.Element, tag: str, text: str) -> ET.Element:
    element = ET.SubElement(parent, tag)
    element.text = str(text or "")
    return element


def pretty_xml(element: ET.Element) -> str:
    raw = ET.tostring(element, encoding="utf-8")
    parsed = minidom.parseString(raw)
    return parsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")


def main() -> None:
    site = {**DEFAULT_SITE_CONFIG, **read_json(SITE_CONFIG_PATH, {})}
    posts = read_json(POSTS_INDEX_PATH, [])
    published_posts = [post for post in posts if post.get("status", "published") == "published"]

    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    append_text(channel, "title", site["title"])
    append_text(channel, "link", site_url(site, "index.html#/"))
    append_text(channel, "description", site["description"])
    append_text(channel, "language", site.get("language", "zh-CN"))
    append_text(channel, "lastBuildDate", format_datetime(datetime.now().astimezone()))

    for post in published_posts:
        post_id = str(post.get("id") or "")
        if not post_id:
            continue

        post_path = ROOT / str(post.get("file") or "")
        link = site_url(site, f"index.html#/post/{post_id}")
        item = ET.SubElement(channel, "item")
        append_text(item, "title", post.get("title", post_id))
        append_text(item, "link", link)
        append_text(item, "guid", link).set("isPermaLink", "true")
        append_text(item, "description", post.get("subtitle", ""))
        append_text(item, "pubDate", format_datetime(parse_date(post.get("date", ""), post_path)))
        for tag in post.get("tags") or []:
            append_text(item, "category", tag)

    FEED_PATH.write_text(pretty_xml(rss), encoding="utf-8")
    print(f"Wrote {FEED_PATH.relative_to(ROOT)} with {len(published_posts)} item(s).")


if __name__ == "__main__":
    main()
