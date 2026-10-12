# Custom development page: launch notes

Canonical page: https://lcbridge.app/highlevel-development/
Audience: software brands entering HighLevel first; agencies second.
Conversion: qualified project-fit conversations, followed by proposals and won value.

## Project inquiry form

`#inquiry-form` contains the user-supplied native HighLevel form,
“Custom Dev | Discuss your project”, ID `clx0Tvu6Bdx27ZtZRnQg`.
The iframe uses the supplied widget URL, layout and cookie-consent attributes.
HighLevel's official `form_embed.js` handles iframe resizing. The wrapper reserves
723 pixels while loading and permits the form to grow at narrower widths.
An email fallback remains below the embed.

Fields, validation, consent and confirmation are configured in HighLevel.
The old custom HTML form and `assets/project-inquiry.js` adapter are retired;
this page no longer loads the External Tracking capture script. Verify native
form submissions and follow-up workflows against this new form ID rather than
the former External Forms identifier `lcbridge-custom-development`.

Earlier test inquiries (12 October 2026) belong to the retired external form
and do not verify this replacement. Keep clearly labelled test inquiries out
of pipeline reporting.

## Measurement

The shared analytics adapter is present, with no GA4 measurement ID configured.
CTA clicks remain intent signals. The website does not inspect cross-origin form
fields or infer submissions from iframe loads. Use confirmed native HighLevel
submissions and CRM stages as the conversion source of truth. Establish a baseline
before setting rate targets and verify native-form attribution in HighLevel.

Monthly, review Search Console impressions/clicks and relevant commercial queries;
software-vendor versus agency inquiries; fit conversations; proposals; and won
project value. Preserve available landing-page and campaign attribution on the
lead. A CTA click is intent, not a recorded inquiry.

For an initial AI visibility check, use the same commercial prompts each month
(HighLevel integration development partner, GoHighLevel marketplace app developer,
HighLevel custom development agency), with multiple runs and recorded sample sizes.
Distinguish brand citations from recommendations. No ranking or visibility gains
have been measured during this implementation.

## Distribution drafts

### Founder post: DocuSign

We helped build HighLevel. Now we help software brands build on it.

Our DocuSign Integration shows what that can look like: send agreements, see
signing status, and connect signing events to workflows inside HighLevel.

The work involves the product experience as well as the API connection: field
mapping, status, actions, and the interface people actually use.

If your software company is planning a HighLevel integration, we can help define,
build, launch, and support it.

See the product demo and discuss your project:
https://lcbridge.app/highlevel-development/

### Founder post: Community Agents

Building AI agents for HighLevel starts with how people will use them.

In Community Agents, you configure knowledge and roles, preview responses
privately, and decide where agents participate. Member Insights surfaces possible
buying interest with conversation evidence for a person to review.

We built that product. Our former HighLevel team also builds custom AI agents,
integrations, SaaS extensions, and frontend experiences for other businesses.

See what we’ve shipped and tell us what you want to build:
https://lcbridge.app/highlevel-development/

### Demonstration clip briefs (not yet rendered or published)

- DocuSign: a 30–45 second sequence showing an agreement sent in HighLevel,
  status on the contact record, then a signing event connected to a workflow.
  End with "Bring your product into HighLevel" and the service page URL.
- Community Agents: a 30–45 second sequence showing knowledge and role
  configuration, a private response preview, then Member Insights with its
  supporting conversation. End with the same service page URL.
- Source the existing product demos. Verify timestamps and visible details before
  editing; do not use illustrative covers as evidence of a working screen.

## Next content releases

Publish these after the service page, once the team can supply and review the
firsthand technical details. Each article links back to the service page.

1. **Planning a HighLevel integration for your SaaS product**: user journey,
   API readiness, authentication, distribution, frontend, rollout, maintenance.
2. **What to scope before building a HighLevel marketplace app**: installation,
   permissions, account boundaries, event handling, testing, review preparation.
3. **How we brought DocuSign into the HighLevel contact record**: real UI,
   field mapping, status and workflow connections; document actual design choices.
4. **How we built Community Agents for HighLevel communities**: knowledge,
   controls, previews, conversation sync and evidence; document actual design choices.

For the planning article, add an ungated Integration Readiness Checklist covering
the user journey, data requirements, installation, account boundaries, frontend
needs, and ongoing ownership. Keep it usable in under ten minutes; an optional
download should not gate the article or create a competing CTA on the service page.

## Asset provenance

- Hero and DocuSign preview reuse the existing multiple-signers documentation
  screenshots. They show the send panel and field mapping inside HighLevel;
  captions identify edited example contact details and template names.
- Community Agents preview reuses the illustrative Member Insights question
  from its product page, rendered as an explicitly labelled HTML illustration.
  It is not presented as a real product screenshot or customer conversation.
- DocuSign demo uses the owner-supplied video `xPoWEYjnhdY`. Community Agents
  uses `W-0UEIWMeM4`, matching the current product page. No videos or social posts were published by this change.
- The service social card has an editable SVG source and a generated PNG.

Implementation stays in the static HTML stack and existing brand system. Existing
uncommitted work was retained. This file is excluded from the published Jekyll site.

## Software-brand copy revision

The hero focuses on software brands, with agencies introduced in capabilities.
Both owned-product showcases describe the challenge, delivered capabilities, and
user result using existing product pages and documentation. No client commissions,
adoption metrics, tenure figures, technical internals, or ownership guarantees
were invented. Ownership, repository access, hosting, and handover are discussion
items during scoping. New FAQ answers match their JSON-LD counterparts.

The page has a project CTA immediately after the showcases and an About link for
company identity. The form keeps its original field names and transport, adds
visible textarea help, and explains the follow-up step. No new blog posts or
external messages were published.

Checked at 360, 390 and 1280 pixels: no horizontal overflow; edited-data and
illustrative labels remain visible; both demos mount their intended privacy-
enhanced YouTube iframe. Empty submission invokes browser validation without
loading tracking. Site/link/schema checks and analytics privacy checks pass.
The earlier verified CRM test remains the end-to-end transport check.

## Production SEO/AEO release — 12 October 2026

GSC Wizard property: `sc-domain:lcbridge.app` (verified owner, full access).
Baseline through 9 October: 28-day site totals 11 clicks, 475 impressions,
2.32% CTR, impression-weighted average position 17.51. These are site-wide
figures, not this service page's performance. The service page has zero
reported clicks/impressions and URL Inspection says “Discovered — currently
not indexed”, with no last crawl or reported Google-selected canonical.

Pre-release GSC Wizard crawl: HTTP 200, self-canonical, indexable, one H1,
title 54 characters and description 153 characters, no schema errors.
The crawler flags a decorative empty-alt logo; the release uses descriptive
logo alt text. Restored Service schema linked to the existing organization
and WebPage; matched visible FAQ answers; added a truthful last-modified date,
company/service identification in the opening paragraph, and descriptive
service heading. Existing sitemap entry and contextual internal links remain.

No special AI markup, invented reviews, price ranges, customer outcomes, or
claims of citations/rankings were added. Search and AI crawler access is already
allowed in robots.txt. `llms.txt` reflects the public offer and inquiry form.
Google AI features use ordinary SEO foundations; no AI-specific GSC reporting
is inferred. Custom pricing remains explicit in the scope/cost answer.

The release is based on the latest production branch and preserves the newer
Community Agents docs hub. GSC Wizard sitemap submission, URL tracking, and
IndexNow notification are checked after publication. IndexNow verification is
a public root text file; it is not a CRM or GitHub credential.

Official reference: https://developers.google.com/search/docs/appearance/ai-features

Primary monthly review: service-page queries, impressions and clicks; qualified
software-vendor inquiries, fit conversations, proposals and won value.
Track agencies separately. Use repeated, consistent prompts for future AI
citation/recommendation measurement; no cross-engine visibility baseline has
been measured here.

## Native form replacement and indexing monitor — 12 October 2026

The supplied native form replaces the custom submission adapter. Canonical,
service/FAQ schema, sitemap and public copy remain unchanged. The live robots.txt
already allows public crawling and references https://lcbridge.app/sitemap.xml.

Heartbeat `monitor-lc-bridge-page-indexing` checks the exact service URL through
GSC Wizard, property `sc-domain:lcbridge.app`, every six hours. It stays quiet
while unchanged, reports confirmed indexing or actionable failures, and pauses
itself after confirmation. Latest inspection reports “URL is unknown to Google”,
with no last crawl or Google-selected canonical; indexing is not confirmed.
