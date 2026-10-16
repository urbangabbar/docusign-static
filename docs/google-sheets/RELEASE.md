# Google Sheets website release — October 16, 2026

Published: https://lcbridge.app/google-sheets-integration/

Release commit: `0bfa8a51d5a95aa538627a0d291e4455d8c738d6`.

The publishing workflow and deployment succeeded at 04:20 UTC. The new site includes the landing page, pricing and calculator, 25 report previews, supported data, documentation hub and seven guides, two early-access notices, and 12 original launch articles. A total of 51 generated HTML pages replaces the previous product destination and extends the site to 87 public canonical pages. Existing products and the current production homepage were preserved.

## Review destinations

- [Product](https://lcbridge.app/google-sheets-integration/)
- [Pricing and calculator](https://lcbridge.app/google-sheets-integration/pricing/)
- [All 25 interactive reports](https://lcbridge.app/google-sheets-integration/templates/)
- [Supported data](https://lcbridge.app/google-sheets-integration/data/)
- [Documentation](https://lcbridge.app/google-sheets-integration/docs/)
- [Twelve launch articles in the Blog hub](https://lcbridge.app/blog/)
- [Sales with Google Sheets context](https://lcbridge.app/book-a-call/?product=google-sheets)

The 90-day strategy and backlog are in `CONTENT-STRATEGY.md`; build and production-metering requirements are in `IMPLEMENTATION.md`. The page register identifies each URL, intent, keyword, owner, source evidence, CTA and canonical.

## Verification

- All 20 Python publishing tests passed.
- Five Node pricing/report suites passed, including allowance and all tier boundaries, rounding, fresh executions versus retries, and 300 combinations across the 25 report calculators.
- Analytics tests passed for consent boundaries, event allowlists, product attribution and exclusion of personal information/query strings. Accepted requests are never inferred from an iframe load.
- All 25 report filters were exercised in the browser. Their mobile pages had no viewport overflow at 390px. Landing and pricing were reviewed at mobile widths, including 320px pricing; menu, consent dialog, library search/empty states and calculator error states worked.
- Live Team Performance retained its four charts and recalculated after owner selection. The live calculator returned $0.75 base usage for 300 transfers, with 250 included and 50 charged in the first band.
- All 66 live HTTP checks matched the exact release files: the 51 generated pages, homepage/Products/Blog hubs, and 12 assets/discovery destinations. JavaScript modules served with a JavaScript content type.
- Canonicals, unique metadata, matching structured data, headings, assets, links, inventory, platform-name coverage and brand separation passed. Maximum public click depth is two in the reconciled production site.
- GitHub Pages’ generated-site check confirmed every public page exists and private engineering sources are excluded.

Local evidence is retained under `output/google-sheets-2026-10-16/`: live-verification.json, screenshots, search-receipts.json, index-inspections.json and pagespeed-mobile.json. These audit files are excluded from public deployment.

## Search state

Google accepted the main sitemap and image sitemap. GSC Wizard tracking matches all 87 deployed URLs: 50 added and 37 already tracked, with no missing or extra URLs. The existing search-maintenance ledger was reconciled and its sitemap/tracker acknowledgement saved.

A Google URL Inspection of the existing product root reports its canonical as indexed. That reflects Google's indexed copy, not proof that the new content has already been recrawled. Sampled new destinations are unknown or discovered but not indexed. No new individual Request indexing action was attempted during this release because the previously observed daily quota cooldown remains active until October 16 at 21:38 UTC. The existing hourly maintenance process retains those requests. Tracker registration and sitemap acceptance are not indexing requests or indexing guarantees.

## External dependencies and scope

1. **Hosted waitlist configuration resolved October 16:** the editor loaded on retry. Saved email-only signup, removed phone/SMS and qualification fields, updated both policy links, and clarified the accepted-submission message. Verified the public widget and required-email validation. The original collection destination is preserved. No real test lead or booking was submitted, so end-to-end accepted delivery has not been asserted.
2. **Analytics:** no confirmed GA4 measurement ID is configured. Product events and consent are tested locally; actual accepted provider records and Search Console remain the available measurement sources. A trusted provider acceptance callback is required before emitting the accepted-request conversion hook.
3. **Performance scores:** PageSpeed Insights returned HTTP 429; GSC Wizard reports no CrUX API key. No LCP, INP or CLS pass is asserted. Browser responsiveness/layout checks and static asset checks are lab observations, not field Core Web Vitals. The performance targets remain LCP ≤2.5s, INP ≤200ms and CLS ≤0.1 when measurable.
4. **Production application:** live CRM/Sheets delivery, source acceptance, billing metering, custom subscription contracts and Marketplace readiness are separate work. Their required changes are documented without modifying production integration code.

Existing unrelated uncommitted work remains in the original checkout. Publication used a clean release checkout based on current production, with only this implementation merged into it. The temporary release checkout and original baseline are documented in IMPLEMENTATION.md for recovery and comparison.
