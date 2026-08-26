#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从权威媒体页面抓取最近三天时政新闻，生成 assets/data/news.json。
用于 GitHub Actions 定时更新，也可在本地手动运行。
"""
import datetime
import html
import json
import os
import re
import ssl
import sys
import urllib.request
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

SOURCES = [
    {
        "name": "人民网",
        "url": "http://politics.people.com.cn/GB/1024/index.html",
        "pattern": r"/n1/(\d{4})/(\d{2})(\d{2})/",
    },
    {
        "name": "新华网",
        "url": "http://www.news.cn/politics/",
        "pattern": r"/(\d{4})(\d{2})(\d{2})/",
    },
]

OUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "data", "news.json"
)


def fetch(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        return resp.read().decode("utf-8", "ignore")


def extract_items(html_text, base_url, source_name, date_pattern):
    items = []
    for m in re.finditer(r"<a[^>]+href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", html_text, re.S):
        href = m.group(1).strip()
        raw_title = re.sub(r"<[^>]+>", "", m.group(2))
        title = html.unescape(raw_title).strip()
        if not title or len(title) < 6:
            continue
        dm = re.search(date_pattern, href)
        if not dm:
            continue
        year, month, day = dm.group(1), dm.group(2), dm.group(3)
        try:
            date = datetime.date(int(year), int(month), int(day))
        except ValueError:
            continue
        full_url = urljoin(base_url, href)
        items.append({
            "title": title,
            "url": full_url,
            "source": source_name,
            "date": date.strftime("%Y-%m-%d"),
        })
    return items


def main():
    today = datetime.date.today()
    cutoff = today - datetime.timedelta(days=3)
    all_items = []

    for src in SOURCES:
        try:
            page = fetch(src["url"])
            items = extract_items(page, src["url"], src["name"], src["pattern"])
            print(f"[{src['name']}] fetched {len(items)} items")
            all_items.extend(items)
        except Exception as exc:
            print(f"[{src['name']}] ERROR: {exc}", file=sys.stderr)

    # 去重 + 过滤最近三天 + 按日期倒序
    seen = set()
    filtered = []
    for item in all_items:
        key = item["url"]
        if key in seen:
            continue
        seen.add(key)
        try:
            d = datetime.date.fromisoformat(item["date"])
        except ValueError:
            continue
        if cutoff <= d <= today:
            filtered.append(item)

    filtered.sort(key=lambda x: x["date"], reverse=True)
    # 保留最多 200 条，前端可无限滚动加载
    filtered = filtered[:200]

    if not filtered:
        print("No recent news found, keeping existing news.json")
        return

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(filtered)} items to {OUT_PATH}")


if __name__ == "__main__":
    main()
