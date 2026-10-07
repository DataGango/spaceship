"""Generate a standalone local dashboard from collected article records."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def build(public=False):
    articles = [json.loads(path.read_text(encoding="utf-8")) for path in sorted((ROOT / "storage/articles").glob("*.json"))]
    events_path = ROOT / "storage/latest_run.json"
    events = json.loads(events_path.read_text(encoding="utf-8")) if events_path.exists() else []
    newspaper_log = ROOT / "storage/newspaper_run.json"
    if newspaper_log.exists():
        events.extend(json.loads(newspaper_log.read_text(encoding="utf-8")))
    x_log = ROOT / "storage/x_run.json"
    if x_log.exists():
        events.extend(json.loads(x_log.read_text(encoding="utf-8")))
    if public:
        articles = [{key: record.get(key) for key in ("title", "publisher", "url", "published_at", "retrieved_at", "content_kind")} for record in articles]
        for record in articles:
            record["text"] = "Read this article at its original publisher using the source link above."
        events = [{key: event[key] for key in ("url", "status") if key in event} for event in events]
        previous = ROOT / "public/index.html"
        if previous.exists():
            from html.parser import HTMLParser

            class SnapshotParser(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.active = False
                    self.parts = []

                def handle_starttag(self, tag, attrs):
                    if tag == "script" and dict(attrs).get("id") == "collected-data":
                        self.active = True

                def handle_endtag(self, tag):
                    if tag == "script":
                        self.active = False

                def handle_data(self, text):
                    if self.active:
                        self.parts.append(text)

            parser = SnapshotParser()
            parser.feed(previous.read_text(encoding="utf-8"))
            earlier = json.loads("".join(parser.parts)).get("articles", [])
            merged = {record["url"]: record for record in earlier}
            merged.update({record["url"]: record for record in articles})
            articles = list(merged.values())
            for record in articles:
                record["text"] = "Read this article at its original publisher using the source link above."
    template = (ROOT / "dashboard_template.html").read_text(encoding="utf-8")
    payload = json.dumps({"articles": articles, "events": events, "public": public, "generated_at": datetime.now(timezone.utc).isoformat()}, ensure_ascii=True).replace("<", "\\u003c")
    output = ROOT / "public/index.html" if public else ROOT / "dashboard.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(template.replace("__COLLECTED_DATA__", payload), encoding="utf-8")
    print("Dashboard: {} ({} articles)".format(output, len(articles)))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public", action="store_true", help="Export titles and source links only, without private chats or scraped text")
    build(public=parser.parse_args().public)