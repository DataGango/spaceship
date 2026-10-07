"""Generate a standalone local dashboard from collected article records."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def build():
    articles = [json.loads(path.read_text(encoding="utf-8")) for path in sorted((ROOT / "storage/articles").glob("*.json"))]
    events_path = ROOT / "storage/latest_run.json"
    events = json.loads(events_path.read_text(encoding="utf-8")) if events_path.exists() else []
    template = (ROOT / "dashboard_template.html").read_text(encoding="utf-8")
    payload = json.dumps({"articles": articles, "events": events}, ensure_ascii=True).replace("<", "\\u003c")
    output = ROOT / "dashboard.html"
    output.write_text(template.replace("__COLLECTED_DATA__", payload), encoding="utf-8")
    print("Dashboard: {} ({} articles)".format(output, len(articles)))
    return output


if __name__ == "__main__":
    build()