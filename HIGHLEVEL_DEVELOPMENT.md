# Custom development page: launch notes

Canonical page: https://lcbridge.app/highlevel-development/
Audience: software brands entering HighLevel first; agencies second.
Conversion: qualified project-fit conversations, followed by proposals and won value.

## Inquiry form handoff

The page currently provides a working email contact at `#inquiry-form`. Replace
that block with the supplied HighLevel custom-development form embed, retaining
an email fallback below it. Do not repurpose a product trial form or calendar.
Use the embed markup supplied by HighLevel and load its resize script once.

Required fields: name, email, company, project description.
Optional fields: product URL, target launch date, indicative budget.
Confirmation: "Thank you. Our team will review your project brief and follow up
about fit and next steps." Do not promise a response deadline.

Configure the CRM workflow to identify custom-development inquiries and classify
software-vendor and agency leads separately. Verify that the chosen form records
the landing page and UTM values using its supported attribution settings. Do not
attempt to read cross-origin iframe fields or treat a CTA click as a submission.
Keep inquiry follow-up separate from optional marketing subscriptions.

After embedding, test required-field validation, submission, confirmation, CRM
record creation, mobile resizing, and failure behavior. Use a clearly identified
test lead, then remove it from reporting. No live form was supplied during the
initial implementation, so these checks are pending.

## Measurement

There is no site analytics integration configured in this repository. Use confirmed
HighLevel form submissions and CRM stages as the conversion source of truth once
the form is connected. Establish a baseline before setting rate targets.

Monthly, review Search Console impressions/clicks and relevant commercial queries;
software-vendor versus agency inquiries; fit conversations; proposals; and won
project value. Preserve available landing-page and campaign attribution on the
lead. An email-link click is intent, not a recorded inquiry.

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

- DocuSign screenshots reuse existing `docusign-integration/img` assets.
- Community Agents preview is a frame from the existing YouTube product demo
  (`yKUq4eHN9J0`, approximately 27 seconds), labelled illustrative because the
  video uses illustrated scenes and example conversations, not a live app capture.
- DocuSign demo uses the owner-supplied video `xPoWEYjnhdY`. Community Agents
  uses `yKUq4eHN9J0`. No videos or social posts were published by this change.
- The service social card has an editable SVG source and a generated PNG.

Implementation stays in the static HTML stack and existing brand system. Existing
uncommitted work was retained. This file is excluded from the published Jekyll site.
