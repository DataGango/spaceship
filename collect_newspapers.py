"""Store historical newspaper discovery metadata, not unverified article text."""

import argparse
import json
from pathlib import Path
from urllib.parse import urlencode

import requests

from scrape import Collector, ROOT, store_article


def archive_record(item):
    url = item.get("id") or item.get("url")
    if not isinstance(url, str) or not url.startswith("https://www.loc.gov/"):
        raise ValueError("Missing Library of Congress item URL")
    description = item.get("description") or []
    if isinstance(description, str):
        description = [description]
    title = item.get("title") or "Historical newspaper"
    date = item.get("date")
    return url, {
        "title": title,
        "publisher": "Library of Congress newspaper archive",
        "published_at": date,
        "content_kind": "archive_metadata",
        "text": "Historical newspaper archive metadata, not full article text.\n"
        + "\n".join([title, "Date: " + str(date or "Unknown"), *description]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="astronomy")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    if not 1 <= args.limit <= 50:
        parser.error("--limit must be between 1 and 50")
    url = "https://www.loc.gov/search/?" + urlencode({
        "fo": "json", "fa": "original-format:newspaper", "q": args.query, "c": args.limit,
    })
    collector = Collector({"www.loc.gov"})
    events = []
    try:
        allowed, delay = collector.allowed(url)
        if not allowed:
            raise ValueError("Archive search disallowed by robots.txt")
        payload = json.loads(collector.fetch(url, delay))
        for item in payload.get("results", [])[:args.limit]:
            try:
                item_url, record = archive_record(item)
                saved = store_article(ROOT / "storage/articles", item_url, record)
                events.append({"url": item_url, "status": "saved" if saved else "already_stored", "kind": "archive_metadata"})
            except ValueError as error:
                events.append({"url": url, "status": "failed", "reason": str(error)})
    except (requests.RequestException, ValueError, OSError) as error:
        events.append({"url": url, "status": "failed", "reason": str(error)})
    directory = ROOT / "storage"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "newspaper_run.json").write_text(json.dumps(events, indent=2), encoding="utf-8")
    print(json.dumps(events, indent=2))
    return 0 if any(event["status"] != "failed" for event in events) else 1


if __name__ == "__main__":
    raise SystemExit(main())