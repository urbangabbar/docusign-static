# LC Bridge website maintenance

## Non-negotiable public brand separation

LC Bridge and every LC Bridge product or brand must remain separate from GoCSM and GovPreneurs in ALL public-facing work. Never disclose, imply, link, or describe an ownership, operator, parent-company, legal-entity, team, or brand relationship to either. Do not reuse their names, logos, domains, email addresses, social profiles, screenshots, customer examples, testimonials, or assets in LC Bridge material.

This covers websites, footers, About and policy pages, copy, docs, metadata, structured data, crawler files, images, videos, captions, downloads, public messages and external communications. Use LC Bridge's own identity and contact details. Do not invent a registered legal name or corporate relationship. Private GitHub authentication instructions are operational only and must never appear in published material.

Treat this as a standing user constraint across future tasks. Read it before creating public assets or communications. Never restore ownership text from history, drafts, handoffs, schema generators or other projects. An exception requires the user's explicit change to this rule.

Run `python3 scripts/check_brand_separation.py` before publication. `check-site.py` and the generated-site check enforce this rule. Media hashes in `data/approved-public-media.json` require review of visible text, metadata, and video/audio content before approving new or changed assets. Never automatically approve changed media just to pass a check.

## GitHub identity

This is a Community Agents-related repository. Use `karthik-sheetstack` for authenticated GitHub operations. Switch with `gh auth switch --hostname github.com --user karthik-sheetstack`, verify `gh api user --jq .login`, and verify the effective identity for Git credentials or environment overrides. Scope credentials per command if concurrent tasks could race. Preserve commit author settings.

## Platform naming

Use GoHighLevel as the primary platform name in public editorial copy, titles, descriptions and media context. Introduce GHL and HighLevel naturally as names for the same platform. The shared platform entity also records the spaced spellings Go High Level and High Level. Never assign these names to LC Bridge's organization identity or imply platform ownership. Preserve actual UI labels, quotations, transcript wording, legal trademark notices, URLs and code identifiers. Run `python3 scripts/check-platform-names.py`; `check-site.py` enforces page and media-discovery coverage.

## Website typography

Follow [LC Bridge's brand guidelines](brand/brand-guidelines.md) and the tokens in `assets/brand.css`. Marketing labels, eyebrows, badges and captions use Inter, sentence case and normal spacing. Use the shared label role (13px, weight 600, line-height 1.5, tracking .01em); do not shrink labels below 12px on mobile. Never use decorative monospace or widely spaced all-caps kickers. Reserve JetBrains Mono for code, IDs and aligned technical data. Keep Poppins for company display headings and preserve each product's established identity. Review desktop and mobile rendering before publishing typography changes.

## Every public content or URL change

Apply [lcbridge-search-sync](skills/lcbridge-search-sync/SKILL.md) whenever adding, changing, moving, or deleting public content. Run `python3 scripts/sync-search.py --write`, `python3 scripts/sync-search.py`, and `python3 scripts/check-site.py` before publishing. The publishing workflow repeats generation and validation automatically on every main push.

Ensure the working branch includes current production `origin/main` before publishing. Preserve other tasks' uncommitted edits; use a clean current checkout if they prevent a safe update. Never regenerate discovery files from a stale checkout and publish them over newer pages.

Every public page, including listing and hierarchy pages, must have a matching canonical, be crawlable, and be linked from the public site. Explicitly classify genuinely internal pages in `data/search-policy.json`. Never silently omit a public page because of missing SEO metadata or an accidental noindex.

After deployment, reconcile Google Search Console through GSC Wizard and individual Request indexing actions in Google's UI. The hourly LC Bridge search maintenance heartbeat handles changes made outside this task and pending quota-limited requests. An inspection or tracker registration is not an indexing request; record accepted requests and Google's eventual indexing separately.
