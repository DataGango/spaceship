"""Collect a bounded set of SpaceX posts through the official X API."""

import argparse
import json
import os
import re

import requests

from scrape import ROOT, USER_AGENT, store_article


def post_record(post, username):
    identifier = post.get("id", "")
    text = post.get("text", "")
    if not isinstance(identifier, str) or not identifier.isdigit() or not isinstance(text, str) or not text.strip():
        raise ValueError("Post is missing a valid ID or text")
    return "https://x.com/{}/status/{}".format(username, identifier), {
        "title": "@{}: {}".format(username, text[:100]),
        "text": text,
        "publisher": "X / @" + username,
        "published_at": post.get("created_at"),
        "content_kind": "social_post",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", default="SpaceX")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_]{1,15}", args.username) or not 5 <= args.limit <= 100:
        parser.error("Use a valid X username and a limit between 5 and 100")
    events = []
    token = os.getenv("X_BEARER_TOKEN")
    if not token:
        events.append({"url": "https://x.com/" + args.username, "status": "failed", "reason": "X_BEARER_TOKEN not configured; no X posts collected"})
    else:
        session = requests.Session()
        session.headers.update({"Authorization": "Bearer " + token, "User-Agent": USER_AGENT})
        try:
            user = session.get("https://api.x.com/2/users/by/username/" + args.username, timeout=30)
            user.raise_for_status()
            user_id = user.json()["data"]["id"]
            response = session.get("https://api.x.com/2/users/{}/tweets".format(user_id), params={"max_results": args.limit, "tweet.fields": "created_at", "exclude": "retweets,replies"}, timeout=30)
            response.raise_for_status()
            payload = response.json()
            if payload.get("errors"):
                raise ValueError("X returned API errors; check developer access and account permissions")
            for post in payload.get("data", [])[:args.limit]:
                url, record = post_record(post, args.username)
                saved = store_article(ROOT / "storage/articles", url, record)
                events.append({"url": url, "status": "saved" if saved else "already_stored", "kind": "social_post"})
            if not events:
                events.append({"url": "https://x.com/" + args.username, "status": "empty", "reason": "API returned no posts"})
        except requests.RequestException:
            events.append({"url": "https://x.com/" + args.username, "status": "failed", "reason": "X API request failed; check developer plan, credentials and rate limits"})
        except (ValueError, KeyError):
            events.append({"url": "https://x.com/" + args.username, "status": "failed", "reason": "Invalid X API response"})
        finally:
            session.close()
    directory = ROOT / "storage"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "x_run.json").write_text(json.dumps(events, indent=2), encoding="utf-8")
    print(json.dumps(events, indent=2))
    return 1 if any(event["status"] == "failed" for event in events) else 0


if __name__ == "__main__":
    raise SystemExit(main())