# Site integration release — October 16, 2026

Google Sheets leads the homepage hero, the complete product sections, the Products hub, and every shared product switcher. Community Agents follows, then DocuSign. Existing product destinations, install flows and homepage #next and #depth anchors remain intact.

`data/site-navigation.json` defines the product order and destinations. `scripts/site_chrome.py` renders a single static footer, a company return bar for product families, and shared preferences. The Google Sheets generator uses the same renderer. Run `python3 scripts/sync-site-chrome.py --write` after page or navigation changes and its check without `--write` before publishing. CI repeats both. All 87 public canonical pages share the exact footer, product links, docs, company contact and clearly scoped product notices. Product pages have an explicit link back to `/`. No new public media was added.

The search parser now excludes accessible SVG chart titles from document titles. This fixes polluted report titles in the search manifest and llms.txt while preserving the chart captions in the page.

## Waitlist resolved

The original hosted form editor loaded on retry. Its existing form ID and collection destination remain unchanged. Saved required email as the only input, “Get early access,” real product privacy/terms links, and a clear provider acceptance message. Removed name, phone, company, account count, and phone marketing/SMS language. Qualification happens in follow-up. Verified the saved public widget and empty-email validation, including the embedded mobile layout. No actual lead or appointment was submitted; real accepted delivery, notification workflows and network-error retention are not claimed as tested.

## Verification

- 24 Python tests, including shared footer equality, all public page idempotency, product ordering, parent return paths and SVG-title regression.
- Five Node suites covering pricing boundaries, execution/retry counting and the complete 25-report controls/calculations.
- Analytics consent, PII exclusion and trusted acceptance checks.
- Search sync, all 87 canonical pages, internal links/fragments, platform aliases, brand/media separation and whitespace checks.
- Browser checks: desktop homepage/menu; mobile homepage/menu; homepage → Sheets → LC Bridge; common preferences; footer/overflow on Products, Sheets, Community Agents, DocuSign and DocuSign docs. Required email validation and provider policy destinations checked separately.

## Remaining dependencies

- A confirmed GA4 stream and a trusted accepted-form callback are still absent. Accepted provider records and Search Console are the available evidence.
- Search Console indexing is queued under the existing daily quota cooldown. Sitemaps/tracked URLs are distinct from accepted indexing requests and eventual indexing.
- Field Core Web Vitals need sufficient data and an available measurement service; no score is asserted.
- Live integration delivery, production metering, billing and marketplace readiness remain separate from the website.
