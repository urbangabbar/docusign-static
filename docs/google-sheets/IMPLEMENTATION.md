# Google Sheets website implementation and production handoff

Reviewed October 16, 2026. Website implementation only. No production integration repository, real CRM operation, live billing configuration, or Marketplace listing was modified.

## Build and source ownership

- `scripts/build-sheets-site.py` generates 51 HTML pages, the pricing Markdown companion, pricing JSON, page registers, and a marked Google Sheets section in the existing Blog hub.
- `scripts/render-sheets-samples.mjs` renders the 25 report fixtures into meaningful static HTML with the same renderer used for interactive previews.
- Run Node 22+ and Python 3.12+; no frontend framework, bundler, package install or new signup backend is required.
- Normal build: `node scripts/render-sheets-samples.mjs`, `python3 scripts/build-sheets-site.py`, followed by the existing search generation and checks.
- `scripts/import-sheets-prototype.mjs /absolute/path/to/sheets-sync-prototype` is a deliberate maintenance import of the owned synthetic report engine. It is not a CI requirement and never connects to the prototype’s app or a real CRM. Inspect source changes before re-importing. The seven imported modules contain pure sample calculations, fixtures and library definitions.
- `data/product-facts.json` owns identity, availability, allowance, rates, and transfer-counting rules. `assets/google-sheets/pricing.json`, visible pricing and `google-sheets-integration/pricing.md` are generated from that same definition. Edit the facts and rebuild rather than editing generated pricing separately.
- `data/google-sheets-reports.json` contains the one 25-report catalog with default settings/results. Report-specific narrative is in `data/google-sheets-report-copy.json`. Existing chart order, KPI definitions, summary/record tables and calculations are retained. Invoice Aging remains a register without invented charts. Team Performance retains four charts. Workflow Performance is excluded.
- SEO generator skips the `data-sheets-generated` pages so it cannot replace their authors, product facts or product-specific artwork. The shared search generator still inventories every public page and validates reachability.

## Commercial model: production change required

The website intentionally supersedes the prototype’s monthly-distinct-record proposal. Count **successful primary-record deliveries per execution**. The same record in another execution counts again. The 250 included units and graduated bands accumulate per connected account per UTC calendar month; those periods do not deduplicate record identities.

| Billable transfers after allowance | USD per transfer |
|---|---:|
| First 1,000 | 0.015 |
| Next 1,000 | 0.012 |
| Next 3,000 | 0.009 |
| Next 25,000 | 0.0075 |
| Remaining | 0.0045 |

Use integer micro-USD for accumulated estimates and round only the final presented total to cents. The production billing/settlement contract must state its actual rounding point and any markup/tax. The public rates are planned early-access base rates and must be accepted before billing.

Required production work, deliberately not performed here:

1. Replace any monthly set of record IDs with accepted-delivery receipts. A receipt needs tenant/account, execution, operation/chunk and primary record identity, delivery outcome, accepted timestamp, unit count and pricing version. Do not expose private record IDs in public telemetry.
2. Count delivery only after the destination accepts the primary record. A partial chunk must charge only the delivered records. Support delayed/uncertain acknowledgements without assuming success from a timeout. Reconcile before retrying.
3. Make retries idempotent at the delivery-operation/record receipt level. A retry must not create a second charge, while an explicitly new execution does count the same record again. Partial progress must not block later uncharged successful rows in the same execution.
4. Bundle supporting lookups and embedded invoice/order lines with their primary records. Define how separate primary-object imports and each direction are identified. Avoid charging both a parent delivery and its display/formatting work.
5. Apply the allowance once per account/month and allocate remaining units progressively through every tier, under concurrent executions. Use an atomic ledger/settlement mechanism. Specify month-boundary behavior with UTC timestamps.
6. Keep source fetches, accepted destination deliveries, retry attempts, report recalculations and billable usage distinct in logs and support views. Recalculating a chart from an existing worksheet is not a new provider transfer.
7. Show preflight estimate versus delivered actual, allowance remaining and the operational reason for an adjustment. Do not promise a final charge based solely on source row count.
8. Test repeat executions, same-operation retries, partial delivery, mixed object families, line-item bundling, account/month separation, concurrency at allowance/tier boundaries, uncertain acknowledgements and billing-provider reconciliation before live billing.
9. Implement custom subscriptions through an agreed sales contract. This website does not create subscription prices, quotas, unlimited usage or contract commitments.

`assets/google-sheets/pricing.mjs` is a public estimation utility. Its small receipt helper tests the execution-versus-retry concept; it is not an implementation of production authorization, atomic settlement, partial-delivery accounting or a payment integration.

## Waitlist and sales

Every Get early access CTA leads to `/google-sheets-integration/#apply`. The form remains `na1YK5kycU0nLOzNtWMf` at the existing LeadConnector-hosted destination. No duplicate backend or alternate collection database is created. The website uses the form’s actual confirmation rather than synthesizing success from load/focus/click events.

Resolved October 16, 2026: the original form editor loaded on retry. Saved an email-only form with required-email validation and “Get early access,” removed name/phone/company/account-volume fields and SMS marketing language, and replaced both placeholder policy links with the product privacy notice and early-access terms. Updated the provider’s accepted-submission message to explain that joining does not activate a connection or subscription. Verified the actual public widget shows these saved changes and rejects an empty email. No real test lead was submitted; provider acceptance and error retention after a real network failure remain untested. Qualification can happen in the follow-up, rather than during signup.

Talk to Sales uses `/book-a-call/?product=google-sheets` and the existing LC Bridge calendar. The contextual page explains workloads, refresh frequency and custom subscriptions; its calendar asks visitors to mention Google Sheets in booking notes. Default booking behavior for other visitors is preserved. No appointment was booked during QA.

## Analytics and privacy

The shared adapter now classifies Google Sheets product pages, generated task guides, and product-context sales visits as `google_sheets`. It records allowlisted preview/filter, calculator, form-start/error and sales-intent events without row contents or form values. Template IDs are restricted to the 25 known IDs. Query strings are excluded. Consent remains required for any configured analytics transmission, and product pages offer an accessible preferences dialog.

No confirmed GA4 stream is currently configured. Local queue/consent/PII tests passed; no measurement ID was invented. `confirmConversion('early_access_request_accepted','google_sheets')` is a hook for a trusted accepted provider flow. It is deliberately not called by the iframe’s load, focus or submit-button click. Accepted provider records and Search Console remain the available measurement sources until a real stream and trusted acceptance callback are connected.

## Review and release

The root checkout had substantial unrelated uncommitted work. A baseline was retained in `/private/tmp/lcbridge-sheets-baseline`. A separate release checkout in `/private/tmp/lcbridge-sheets-publish` starts at the current production main and merges only this implementation’s changes. The newer production homepage, naming work, documentation and discovery infrastructure are preserved.

Required checks: Node report/pricing tests, analytics boundary tests, Python search/brand/platform tests, schema checks, reproducible generation, complete search inventory, local assets/links, and media review. The social artwork is original, visually reviewed and hashed after review. Public source and media checks prohibit cross-brand references.

Browser QA covers all 25 report interactions, mobile overflow, search/empty states, calculator error retention and sales context. Performance observations are lab results and do not establish field Core Web Vitals. New production URLs need real user data before a field result is possible.

After deployment: verify the live 87-page inventory, page responses and discovery assets; submit sitemaps and reconcile GSC Wizard tracking; use actual Google UI Request indexing for pending changed pages; record accepted requests separately from eventual indexed status. Preserve the shared submission queue and quota backoff. The existing hourly maintenance process handles pending requests; it must not be represented as a guaranteed indexing date.
