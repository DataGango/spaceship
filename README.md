# Space Article Collector

Collect a bounded selection of public NASA and ESA articles for local research.
Trusted publishers are a starting point, not an automated guarantee of article quality.
This collector reads configured RSS/Atom feeds; it does not scrape entire websites.

## Run

```sh
cd ~/Downloads/agentic_rag_git_jira_framework/space
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scrape.py --max-articles 10
python -m unittest -v
```

## Dashboard

### Public dashboard

The public article index is hosted at https://datagango.github.io/spaceship/ after
the Pages workflow completes. It displays titles, dates, publisher counts and
original-source links only. It does not expose full scraped text, saved chats,
credentials, or the localhost chatbot. Regenerate the public snapshot after a
collection with `.venv/bin/python build_dashboard.py --public`, then commit
`public/index.html`. Pages deploys only the `public/` directory.

### SpaceX and X

SpaceX's updates page is configured in `sources.json`. Collection fails closed
when robots.txt cannot be fetched; the live SpaceX attempt returned a robots.txt
404, so no SpaceX records were saved. X requires official developer access and
`X_BEARER_TOKEN` in the collector's environment (never in browser code or Git).
Run `.venv/bin/python collect_x.py --username SpaceX --limit 10`.
API access may cost money; no X posts were collected without a token.

## Historical Newspapers

```sh
.venv/bin/python collect_newspapers.py --query astronomy --limit 10
```

This optional collector stores Library of Congress newspaper discovery metadata,
not full article text. It respects robots.txt; if search is blocked, it records
the failure in `storage/newspaper_run.json` without bypassing the restriction.
The dashboard includes that log. Historical reporting is not current scientific
evidence. The live archive search was blocked during validation, so no historical
newspaper records were collected. Existing articles remain stored locally.

For a broader bounded modern collection, use
`python scrape.py --max-articles 20 --max-per-feed 10` so each feed gets a turn.

### Live Chat Agent

```sh
.venv/bin/python server.py --port 8770
```

Open <http://127.0.0.1:8770/> for article browsing, chat, saved answers, and bounded
source refreshes. All collected articles and successful responses are stored under
`storage/`. Without a model key, chat returns labeled source excerpts instead of
generated answers. The collection does not cover everything about space.

For LLM answers, set `OPENAI_API_KEY` privately in the server's shell before starting
it. `OPENAI_MODEL` defaults to `gpt-4o-mini`. Do not paste keys into chat, commit them,
or place them in browser code. Questions and excerpts are sent to the configured
OpenAI model; API use may cost money. The backend binds only to localhost and does
not serve credentials, source code, or arbitrary files. This is a personal local
tool, not an authenticated public service. Retrieval is lexical and citations are
prompted, not a guarantee of factual accuracy: check the linked original sources.

After collecting articles, regenerate the local reading dashboard:

```sh
.venv/bin/python build_dashboard.py
open dashboard.html
```

The dashboard embeds the saved records, supports text search and publisher filtering,
and shows original URLs, dates, full extracted text, JSON downloads, and the latest
run log. It works without a server. Regenerate it after each collection to refresh
the snapshot. Keep it local unless you have permission to redistribute the text.

Each article is stored as JSON in `storage/articles/`, with title, publisher, source
URL, publication date when present, retrieval timestamp, and readable text.
SHA-256 URL identifiers prevent duplicate storage. `storage/latest_run.json` lists
saved, skipped, and failed requests. Existing article files are not overwritten.

Edit `sources.json` to change feeds and explicitly approved HTTPS hostnames.
Feeds may change or redirect: configure their final URLs if a redirect is reported.
The collector respects robots.txt and crawl-delay, limits request sizes and counts,
and refuses to crawl when robots.txt cannot be fetched. It skips pages without an
article/main region or substantial text. JavaScript-only pages are not supported.

Store full text locally only where publisher terms permit it. Robots.txt permission
does not grant copyright permission. Attribute sources and check reuse rights before
publishing extracts; do not bypass authentication, paywalls, or access restrictions.
No API keys are required. No files are pushed to GitHub by this project.