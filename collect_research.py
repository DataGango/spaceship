"""Collect arXiv physics and mathematics preprint abstracts for local retrieval."""

import argparse
import json
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup

from scrape import Collector, ROOT, store_article


FEEDS = {"physics": "https://rss.arxiv.org/rss/physics", "mathematics": "https://rss.arxiv.org/rss/math"}


def parse_papers(content, topic):
    papers = []
    for item in ET.fromstring(content).iter():
        if item.tag.split("}")[-1] != "item":
            continue
        fields = {element.tag.split("}")[-1]: element.text or "" for element in item}
        url = fields.get("link", "").replace("http://", "https://", 1)
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname != "arxiv.org" or not parsed.path.startswith("/abs/"):
            continue
        title = fields.get("title", "").strip()
        abstract = BeautifulSoup(fields.get("description", ""), "html.parser").get_text(" ", strip=True)
        if title and abstract:
            papers.append((url, {"title": title, "text": abstract, "publisher": "arXiv / " + topic,
                                 "published_at": fields.get("pubDate") or fields.get("date") or None,
                                 "content_kind": "preprint_abstract", "topic": topic}))
    return papers


def collect(topic="all", limit=10):
    if topic not in {*FEEDS, "all"} or not 1 <= limit <= 30:
        raise ValueError("Select physics, mathematics or all and a limit of 1–30 per topic")
    collector = Collector({"rss.arxiv.org"}, delay=3)
    events = []
    for name, url in FEEDS.items():
        if topic != "all" and topic != name:
            continue
        try:
            allowed, delay = collector.allowed(url)
            if not allowed:
                raise ValueError("Feed disallowed by robots.txt")
            papers = parse_papers(collector.fetch(url, delay), name)[:limit]
            for paper_url, record in papers:
                saved = store_article(ROOT / "storage/articles", paper_url, record)
                events.append({"url": paper_url, "status": "saved" if saved else "already_stored", "topic": name})
            if not papers:
                events.append({"url": url, "status": "empty"})
        except (requests.RequestException, ValueError, OSError, ET.ParseError) as error:
            events.append({"url": url, "status": "failed", "reason": str(error)})
    (ROOT / "storage").mkdir(parents=True, exist_ok=True)
    (ROOT / "storage/research_run.json").write_text(json.dumps(events, indent=2), encoding="utf-8")
    return events


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", choices=[*FEEDS, "all"], default="all")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    results = collect(args.topic, args.limit)
    print(json.dumps(results, indent=2))
    raise SystemExit(0 if any(event["status"] in {"saved", "already_stored"} for event in results) else 1)