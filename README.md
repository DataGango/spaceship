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