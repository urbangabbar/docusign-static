---
name: lcbridge-search-sync
description: Keep lcbridge.app public pages, URL migrations, sitemap, llms.txt, robots.txt and Google Search Console synchronized after website content, URL, or publishing changes.
---

# LC Bridge search maintenance

The user wants every public canonical page discoverable and individually submitted to Google, including `/blog/`, `/products/` and documentation hubs. Google controls actual indexing. Never report submission as indexing or inspections as submission.

Work in the website repository using `AGENTS.md` for GitHub identity. Read `data/search-policy.json`; every non-redirect HTML page is public unless explicitly classified internal. Keep internal sources excluded by `_config.yml`.

Before publishing:

- Give public pages self-canonicals that match GitHub Pages routing: directory index URLs end in `/`; flat HTML URLs have neither `.html` nor a trailing slash.
- Link new pages from their public hub. Run `python3 scripts/sync-search.py --write`, then `python3 scripts/sync-search.py` and `python3 scripts/check-site.py`. The generator inventories all public pages and keeps lastmod stable for unchanged content.
- For a moved URL, preserve the old path as an instant meta-refresh + canonical stub pointing directly to the final public page. GitHub Pages does not support arbitrary HTTP redirect rules. Prefer server-side 301/308 if the hosting later supports them. Do not introduce chains or use noindex on migration stubs.
- For an intentionally deleted URL with no replacement, delete the page so it returns 404 and add an explanation keyed by its absolute URL in `data/search-removals.json`. Do not redirect unrelated deletions to the homepage.
- Commit discovery files and `search-manifest.json` with the change. `.github/workflows/publish.yml` regenerates and validates before deploying, including edits made outside Codex.

GitHub Pages currently also uses legacy main-branch publishing. The workflow waits for that build before deploying its validated artifact, so generated metadata wins the race. An administrator can select GitHub Actions as the sole Pages source for strict pre-publication gating. The required `karthik-sheetstack` account has push access but cannot change that setting; never silently switch accounts to change it.

After successful publication:

1. Read the live `search-manifest.json`; verify live sitemap, robots, llms and changed pages. Work from deployed content, not another task's uncommitted checkout.
2. Submit `https://lcbridge.app/sitemap.xml` with GSC Wizard for `sc-domain:lcbridge.app` when the deployed manifest changes. Reconcile the Indexing Tracker: add every public canonical URL and remove retired or redirect-source URLs from the public tracker. Inspect migration sources separately to verify canonical transfer.
3. Run `python3 scripts/reconcile-search.py --live` to maintain a private per-URL ledger in `output/search-maintenance/state.json`, keyed by URL and deployed contentHash. Initially enqueue every public page; on later runs enqueue added or changed pages. Retain already accepted requests across runs; do not repeat requests for an unchanged accepted contentHash. Record removed URLs and redirects separately. Use `--record URL --status accepted --detail 'Google UI confirmed Indexing requested'` only after visible confirmation; `--status quota` leaves that URL pending and sets a 24-hour retry delay. Honor `submissionRetryAfter` before further UI submissions. The script prepares the queue; it does not itself submit to Google.
4. For each pending URL, use the signed-in LC Bridge Google Search Console browser UI, inspect the exact URL, and click Request indexing. Record `accepted` only when Google visibly confirms Indexing requested. If Google denies the request, record its reason and diagnose it. If quota is exhausted, stop submissions and leave remaining URLs pending for the next day. If Google presents a CAPTCHA or login requiring the user, preserve the tab and request the needed interaction. Never bypass Google quotas, reuse accounts to evade them, or invoke private browser endpoints.
5. Use GSC Wizard URL inspections to track eventual index coverage and Google-selected canonical independently. Inspect pending/unindexed/migrating URLs regularly within quotas; unchanged indexed pages need only a weekly check. Notify the user about actionable errors or meaningful progress, not unchanged statuses.

Google's URL Inspection API reads indexed status; it cannot request indexing. Google's Indexing API supports JobPosting and livestream BroadcastEvent pages, not this marketing/documentation site. IndexNow is not Google submission. Do not add fake supported schema or make unsupported API calls.

The hourly Codex heartbeat reconciles new deployments and resumes the submission ledger. Browser access and Google quotas can delay individual requests. Do not claim fully unattended individual Google indexing when a run is blocked. Keep the persistent heartbeat active after indexing succeeds so future changes are covered.

References: [Google recrawl requests](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl), [redirects](https://developers.google.com/search/docs/crawling-indexing/301-redirects), [Indexing API scope](https://developers.google.com/search/apis/indexing-api/v3/using-api).
