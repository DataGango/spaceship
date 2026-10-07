"""Collect a bounded selection of articles from configured space-science feeds."""

import argparse
import hashlib
import ipaddress
import json
import socket
import time
import urllib.robotparser
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent
USER_AGENT = "SpaceArticleCollector/1.0"
MAX_BYTES = 5 * 1024 * 1024


def validate_url(url, hosts):
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in hosts or parsed.username or parsed.password:
        raise ValueError("URL must use HTTPS and an explicitly approved host")
    if parsed.port not in (None, 443):
        raise ValueError("Only the default HTTPS port is allowed")
    for address in socket.getaddrinfo(parsed.hostname, 443):
        if not ipaddress.ip_address(address[4][0]).is_global:
            raise ValueError("Private or local network destinations are not allowed")


def feed_links(content):
    root = ET.fromstring(content)
    urls = []
    for item in root.iter():
        if item.tag.split("}")[-1] not in ("item", "entry"):
            continue
        for element in item:
            if element.tag.split("}")[-1] == "link":
                if element.attrib.get("rel", "alternate") != "alternate":
                    continue
                url = element.attrib.get("href") or (element.text or "").strip()
                if url and url not in urls:
                    urls.append(url)
    return urls


def extract_article(content):
    soup = BeautifulSoup(content, "html.parser")
    for unwanted in soup.select("script, style, nav, footer, header, aside, form, noscript"):
        unwanted.decompose()
    heading = soup.find("h1") or soup.find("title")
    title = heading.get_text(" ", strip=True) if heading else "Untitled article"
    main = soup.find("article") or soup.find("main")
    if main is None:
        raise ValueError("No article or main content region found")
    paragraphs = [element.get_text(" ", strip=True) for element in main.select("h2, h3, p, li")]
    text = "\n\n".join(dict.fromkeys(part for part in paragraphs if part))
    if len(text) < 200:
        raise ValueError("Insufficient readable article text")
    published = soup.find("meta", attrs={"property": "article:published_time"})
    return {"title": title, "text": text, "published_at": published.get("content") if published else None}


def store_article(directory, url, article):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (hashlib.sha256(url.encode("utf-8")).hexdigest() + ".json")
    if path.exists():
        return False
    record = dict(article, url=url, retrieved_at=datetime.now(timezone.utc).isoformat())
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)
    return True


class Collector:
    def __init__(self, hosts, delay=2):
        self.hosts = set(hosts)
        self.delay = max(1, delay)
        self.last_request = 0
        self.robots = {}
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT

    def fetch(self, url, delay=None):
        validate_url(url, self.hosts)
        interval = max(self.delay, delay or 0)
        time.sleep(max(0, interval - (time.monotonic() - self.last_request)))
        self.last_request = time.monotonic()
        with self.session.get(url, timeout=30, stream=True, allow_redirects=False) as response:
            response.raise_for_status()
            if 300 <= response.status_code < 400:
                raise ValueError("Redirect skipped; configure its final HTTPS URL explicitly")
            chunks = []
            size = 0
            for chunk in response.iter_content(65536):
                size += len(chunk)
                if size > MAX_BYTES:
                    raise ValueError("Response exceeds 5 MB limit")
                chunks.append(chunk)
            return b"".join(chunks)

    def allowed(self, url):
        origin = "https://" + urlsplit(url).netloc
        if origin not in self.robots:
            response = self.fetch(origin + "/robots.txt")
            parser = urllib.robotparser.RobotFileParser()
            parser.parse(response.decode("utf-8", errors="replace").splitlines())
            self.robots[origin] = parser
        parser = self.robots[origin]
        return parser.can_fetch(USER_AGENT, url), parser.crawl_delay(USER_AGENT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "sources.json")
    parser.add_argument("--output", type=Path, default=ROOT / "storage")
    parser.add_argument("--max-articles", type=int, default=10, help="Maximum saved articles across all feeds")
    parser.add_argument("--delay", type=float, default=2)
    parser.add_argument("--max-per-feed", type=int, default=10)
    args = parser.parse_args()
    if args.max_articles < 1 or args.max_per_feed < 1:
        parser.error("Article limits must be positive")
    sources = json.loads(args.config.read_text(encoding="utf-8"))
    collector = Collector([host for source in sources for host in source["allowed_hosts"]], args.delay)
    saved = 0
    events = []
    for source in sources:
        try:
            allowed, delay = collector.allowed(source["feed"])
            if not allowed:
                raise ValueError("Feed disallowed by robots.txt")
            if source.get("type") == "page":
                links = [source["feed"]]
            else:
                links = feed_links(collector.fetch(source["feed"], delay))
        except (requests.RequestException, ValueError, ET.ParseError, OSError) as error:
            events.append({"url": source["feed"], "status": "failed", "reason": str(error)})
            continue
        for url in links[:args.max_per_feed]:
            if saved >= args.max_articles:
                break
            try:
                validate_url(url, set(source["allowed_hosts"]))
                allowed, delay = collector.allowed(url)
                if not allowed:
                    raise ValueError("Article disallowed by robots.txt")
                article = extract_article(collector.fetch(url, delay))
                article["publisher"] = source["name"]
                article["content_kind"] = source.get("content_kind", "article_text")
                created = store_article(args.output / "articles", url, article)
                saved += int(created)
                events.append({"url": url, "status": "saved" if created else "already_stored"})
            except (requests.RequestException, ValueError, OSError) as error:
                events.append({"url": url, "status": "failed", "reason": str(error)})
        if saved >= args.max_articles:
            break
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "latest_run.json").write_text(json.dumps(events, indent=2), encoding="utf-8")
    print("Saved {} new articles. Run log: {}".format(saved, args.output / "latest_run.json"))
    for event in events:
        print(event["status"], event["url"], event.get("reason", ""))
    return 0 if saved or any(event["status"] == "already_stored" for event in events) else 1


if __name__ == "__main__":
    raise SystemExit(main())