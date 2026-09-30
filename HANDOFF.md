# HANDOFF — lcbridge.app

Marketing site for **LC Bridge** (legal entity: GoCSM Innovations Private Limited,
trading as LCBridge). Sells white-labeled integrations that HighLevel / LeadConnector
agencies embed as their own.

Repo: `https://github.com/urbangabbar/docusign-static`  (the GitHub slug still says docusign-static)
Local checkout: `~/dev/Personal/lcbridge-website`  (renamed 2026-09-10 — the slug and the folder no longer match)
Live: `https://lcbridge.app`
Last verified: 11 September 2026.

---

## 1. Stack & build

**There is no build step. None. It is hand-written static HTML.**

- No `package.json`, no `node_modules`, no bundler, no `.github/workflows`.
- `_config.yml` exists but configures **nothing except an exclude list** — it keeps
  `HANDOFF.md` out of the published site. It is not a build config.
- No package manager is used by this project at all.
- 43 `.html` files, 1 `.css` file (`assets/brand.css`), **0 `.js` files** in the repo.
  The only JavaScript on the site is inline `<script>` in a few pages plus two
  third-party scripts (see §6).

### Serving it locally

```bash
cd ~/dev/Personal/lcbridge-website
python3 -m http.server 8000
# http://localhost:8000/index.html
```

That is the entire dev loop. Edit an `.html` file, reload the browser.

**Local server caveat — this will bite you.** `python3 -m http.server` does *not*
resolve extensionless URLs. `http://localhost:8000/docusign-integration/pricing`
404s locally but is 200 in production. Locally you must request
`/docusign-integration/pricing.html`. See §3 for why. When link-checking locally,
map extensionless → `.html` yourself or you will chase phantom 404s.

### Pinned versions actually in use

| Tool | Version | Used for |
|---|---|---|
| Python | 3.14.1 | local server only; not a dependency of the site |
| git | 2.49.0 | |
| gh | 2.94.0 | needed for the deploy account switch, see §4 |

No runtime is required to *serve* the site — GitHub Pages serves the files as-is.

---

## 2. Repo map

### Where pages live

Every page is a complete standalone HTML document: its own `<head>`, its own
inline `<style>` block, its own nav and footer markup. There are **no partials,
no includes, no layouts, no components**. A change to shared chrome (nav, footer)
means editing every file that has it.

```
index.html                                  brand homepage
products/index.html                         product listing
blog/index.html                             blog index
blog/<slug>/index.html                      3 posts
brand/index.html                            internal brand reference page
book-a-call/index.html                      brand-level booking page
404.html

docusign-integration/                       PRODUCT 1 (live, sellable)
  index.html                                  product page
  pricing.html  insurance.html  real-estate.html
  book-a-call.html                            product-level booking page
  privacy.html  terms.html  refund.html       legal (Paddle-verified)
  docs/index.html                             docs index
  docs/getting-started/index.html             video-led guide
  img/*.png                                   7 product screenshots used by docs

google-sheets-integration/index.html        PRODUCT 2 (pre-launch, waitlist)
community-agents/index.html                 PRODUCT 3 (in build, waitlist)

assets/                                     see below
sitemap.xml  robots.txt  llms.txt  CNAME
```

### Where COPY lives

**Inline in the HTML. There are no content files.** No markdown, JSON or YAML
drives any rendered page. To change a headline you edit the `<h1>` in the page.

Two `.md` files exist but are **not** the source of any page:

- `blog-drafts/*.md` — drafts that were hand-converted into `blog/<slug>/index.html`.
  Editing the `.md` changes nothing on the published post.
- `brand/brand-guidelines.md` — **publicly served, returns 200** (no front matter, so
  Jekyll copies it verbatim). Flagged, not fixed.

**Both draft files are public too.** They carry YAML front matter, so Jekyll renders
them to `/blog-drafts/<slug>.html` — live, 200, and indexable. If drafts should not
be public, add them to `exclude` in `_config.yml`.

### CSS

- `assets/brand.css` is the only stylesheet — the "Refined Cobalt" design system:
  design tokens on `:root`, plus `.lcb-*` components (`.lcb-btn`, `.lcb-card`,
  `.lcb-badge`, `.lcb-section`, `.lcb-logo`, `.lcb-ai`).
- **Not every page loads it.** `index.html`, `products/index.html`, `blog/*`,
  `docusign-integration/{index,pricing,book-a-call,insurance,real-estate}.html`,
  `community-agents/`, `book-a-call/` and `brand/` do. The legal pages
  (`privacy/terms/refund`), `docs/*` and `google-sheets-integration/` are
  **fully standalone** with their own token names (`--ink`, `--brand`, `--line`
  rather than `--lcb-*`). Check which system a page uses before editing its CSS.
- Product pages override `--lcb-primary` in a page-scoped `:root` block:
  DocuSign `#4C00FF`, Sheets `#0B8043`, Community Agents `#6938EF`.
  `--lcb-ai` (violet) is reserved by the design system for AI features that are
  always labelled — Community Agents uses it as its page primary deliberately.

### Assets

| File | Status |
|---|---|
| `assets/brand.css` | the design system |
| `assets/docusign-logo.svg`, `docusign-mark.svg`, `docusign-favicon.svg` | official DocuSign artwork, extracted from their public brand kit. **Do not redraw.** See §6. |
| `assets/lcbridge-lockup-{black,white,dark}.{svg,png}` | LC Bridge lockups. `-black` is in every product header, `-white` in every footer. |
| `assets/og-docusign.png` | social card, referenced by 3 pages |
| `assets/arun-headshot.jpg` | founder photo on both booking pages |
| `docusign-integration/img/*.png` | 7 product screenshots, used by the docs guide |
| `assets/docusign-icon.svg`, `docusign-icon-180.png` | **unreferenced.** The old invented DocuSign glyph. Possibly the marketplace listing icon — confirm before deleting. |
| `assets/lcbridge-logo.{svg,png}`, `lcbridge-lockup-dark.svg` | **unreferenced.** |
| `hero-01.png` (repo root) | **unreferenced.** Tracked but used by nothing. |
| `b9376d9be31b0aff65a979156b81b9e6.txt` | domain-verification token. **Never delete** — deleting it can un-verify the domain with whichever provider issued it (Paddle or DocuSign). |

---

## 3. Routing

GitHub Pages (`build_type: legacy`, i.e. Jekyll) resolves a request in this order:

1. exact file → 2. `<path>.html` → 3. `<path>/index.html`

There is no router, no redirect config, no `_redirects` file. Three mechanisms
are in play and you need to know which one a given URL uses:

| URL | Served by | Mechanism |
|---|---|---|
| `/docusign-integration/` | `docusign-integration/index.html` | directory index |
| `/docusign-integration/pricing` | `docusign-integration/pricing.html` | **extensionless → `.html`** |
| `/docusign-integration/docs/` | `docusign-integration/docs/index.html` | directory index |
| `/docusign-integration/docs/getting-started/` | `.../getting-started/index.html` | directory index |
| `/community-agents/` | `community-agents/index.html` | directory index |

**Convention: link directories with a trailing slash.** `/products/`, `/blog/`,
`/book-a-call/`, `/docusign-integration/docs/`. Without it Pages issues a real 301
to add the slash — one wasted round trip on every click. Flat `.html` files
(`pricing`, `terms`, `insurance`) are linked **without** an extension and
**without** a slash, because they are files, not directories.

### Pages served by a different mechanism — 22 redirect stubs

These are **meta-refresh + canonical**, not 301s. GitHub Pages cannot issue a real
301 for an arbitrary path. Every one of these is a tiny HTML file whose only job
is to forward:

```
/product/docusign-integration/*   ->  /docusign-integration/*      (10 stubs)
/product/google-sheets-integration/ -> /google-sheets-integration/
/product/                          ->  /products/
/docusign/*                        ->  /docusign-integration/*      (6 stubs)
/pricing/                          ->  /docusign-integration/pricing
/google-sheets/                    ->  /google-sheets-integration/
/lcbridge.html                     ->  /
/docusign-integration-insurance-quility.html     -> /docusign-integration/insurance
/docusign-integration-real-estate-rei-reply.html -> /docusign-integration/real-estate
```

Rules when you touch these:

- **Never chain them.** A stub must point at a live page, never at another stub.
  If you move a page again, update the stubs that point at it in the same commit.
- `/docusign` doubles as a **vanity URL** for marketing (say it on a call). It is
  a stub, so don't build backlinks to it — link the canonical
  `/docusign-integration/`.
- **Upgrade path:** putting Cloudflare in front of Pages (free) gives real 301s and
  lets all 22 stubs be deleted. Discussed with the owner, not yet done.

---

## 4. Deploy

| | |
|---|---|
| Host | GitHub Pages |
| Source | branch `main`, path `/` |
| Build | `legacy` (Jekyll), `_config.yml` is exclude-only, no `.nojekyll` |
| Custom domain | `lcbridge.app` via `CNAME`, HTTPS enforced |
| Auto-deploy | **yes — push to `main` publishes** |
| Preview URL | **none.** There is no staging. `main` is production. |
| Build time | ~30–60 s after push |

### Pushing requires a GitHub account switch

`git push` uses `gh` as its credential helper, so the **active `gh` account** is what
authenticates — not `user.name`/`user.email`, which are already correct
(`karthik-sheetstack` / `karthik@sheetstack.ai`) and will mislead you.

Two accounts are in the keyring. `sunny-gocsm` is usually active and **has no write
access** — it fails with `403 Permission to urbangabbar/docusign-static.git denied
to sunny-gocsm`. Only `karthik-sheetstack` can push.

```bash
gh auth switch --user karthik-sheetstack
git push origin main
gh auth switch --user sunny-gocsm     # restore what the owner had active
```

### Verifying a deploy

Poll production; don't assume. Pages serves the old build for up to a minute.

```bash
# example: confirm a new page is live
for i in $(seq 1 20); do
  c=$(curl -s -o /dev/null -w '%{http_code}' https://lcbridge.app/community-agents/)
  echo "try $i: $c"; [ "$c" = "200" ] && break; sleep 15
done
```

**Diagnose from production, not the working tree.** Twice in this repo's history a
reported "bug" was simply unpushed work. Before debugging any "the site still shows
X" report, run `git log --oneline origin/main -1` against `HEAD` and `curl` the live
URL.

---

## 5. Current state

### Shipped and live

- **DocuSign Integration** — the only sellable product. Product page with a hero
  demo video, pricing, two industry pages (insurance, real estate), a booking page,
  docs, and Paddle-compliant legal pages.
- **Google Sheets Integration** — pre-launch. Page is live, CTA is "Join the
  waitlist" everywhere.
- **Community Agents** — in build. Full marketing page live at `/community-agents/`,
  waitlist open. Built from two research PDFs in `~/Downloads/` (not in the repo):
  `Community Agents Phase 1 Research.pdf` and `Community Agent Demo Design.pdf`.
  Those are the source of truth for the product's claims — the page cites
  third-party benchmarks (63.3% Hivebrite, 5.8% RetentionCheck, 1-in-50 FeverBee)
  attributed on-page.
- **Docs tree** — `docusign-integration/docs/` with `getting-started/` inside it,
  led by a 6-minute YouTube walkthrough (`fZ4Qpj5K-Lo`).
- **Conversion routing** — settled and consistent. Every CTA does what it says:

  | Promise | Asset | Where |
  |---|---|---|
  | "Start free trial" | form `iUnmDsvilWzcsbWQ35I9` | `/docusign-integration/#apply` |
  | "Book a call" (brand) | calendar `SDbUWZSRSHw3ZtB6mDOy` | `/book-a-call/` |
  | "Book a call" (product) | calendar `VbUUZSpipvw56s9pRtNs` | `/docusign-integration/book-a-call` |
  | "Join the waitlist" (Sheets) | form `na1YK5kycU0nLOzNtWMf` | `/google-sheets-integration/#apply` |
  | "Join the waitlist" (Agents) | form `2615pqHKzf12eCD1ZDOC` | `/community-agents/#waitlist` |

### Half-finished / recently changed — read before touching

- **The site-wide pop-up was deleted.** `assets/book-modal.js` is gone and no page
  has a `data-book` trigger. Do not reintroduce it. HighLevel form
  `TO5PG5GbMdM5I72xnUX0` is now unreferenced by the site and can be retired in GHL.
- **URLs moved twice.** `/docusign/*` → `/product/docusign-integration/*` (Jul 3)
  → `/docusign-integration/*` (Sep 8). Hence the 22 stubs. Do not move them a
  third time without a strong reason and a Cloudflare 301 layer first.
- **`community-agents/` has no OG image.** Deliberate — the only social card is
  DocuSign-branded. A brand OG card is worth making.
- **There is no analytics of any kind.** No GA, no GTM, no Plausible, no pixel, no
  click events, anywhere. Any claim about conversion is currently unmeasurable.

---

## 6. Constraints

### Do not touch

- `CNAME` — removing it drops the custom domain.
- `b9376d9be31b0aff65a979156b81b9e6.txt` — domain-verification token.
- `assets/docusign-logo.svg`, `docusign-mark.svg`, `docusign-favicon.svg` —
  extracted from DocuSign's official brand kit. **Never redraw, recolour or
  distort them.** If a new size or variant is needed, take it from the kit at
  `~/Downloads/Docusign {Horizontal,Vertical} Color Black/`. The site previously
  shipped hand-drawn fake DocuSign marks; that was fixed deliberately.
- `docusign-integration/{privacy,terms,refund}.html` — Paddle verified the domain
  against these. Changing the legal contact address or entity details can break
  payment-provider verification. The contact address is `arun@lcbridge.app`; the
  docs page separately uses `support@lcbridge.app`.

### Externally sourced — never edit the markup, only swap the ID

Five LeadConnector (HighLevel) widgets and one YouTube embed. The iframe markup and
`data-*` attributes come from GHL's embed code; `link.msgsndr.com/js/form_embed.js`
resizes the frames at runtime. Loaded by 5 pages.

```
booking/SDbUWZSRSHw3ZtB6mDOy   brand calendar        /book-a-call/
booking/VbUUZSpipvw56s9pRtNs   product calendar      /docusign-integration/book-a-call
form/iUnmDsvilWzcsbWQ35I9      DocuSign trial        /docusign-integration/#apply
form/na1YK5kycU0nLOzNtWMf      Sheets waitlist       /google-sheets-integration/#apply
form/2615pqHKzf12eCD1ZDOC      Agents waitlist       /community-agents/#waitlist
youtube-nocookie /embed/fZ4Qpj5K-Lo   docs walkthrough
```

The form fields, consent copy and downstream automations are configured **in
HighLevel, not here.** Changing a form's fields is a GHL task.

> **Known issue, owner's to fix:** the three forms carry three *different* consent
> strings — one grants marketing permission, one explicitly does not
> (`non-marketing`), one is a hybrid. They collect into the same CRM. If a workflow
> treats them alike, it is messaging people who declined. Raised with the owner;
> he owns the fix in GHL.

### Generated output

None. Nothing in the repo is generated by a build. `sitemap.xml` and `llms.txt` are
maintained **by hand** — add an entry when you add a page.

### Gitignored (never commit these)

`.playwright-mcp/`, `.gstack/`, `.DS_Store`, and QA screenshot patterns
(`ds-*.png`, `gs-*.png`, `*-desktop.png`, `*-mobile.png`, …). Headless captures
land in the repo root by default — check `git status` before `git add -A`.

---

## 7. Conventions

### Commits

Subject line is a sentence describing the *effect*, not the files touched.
Lowercase after the first word, no `feat:`/`fix:` prefixes, no scope tags.

```
Header byline carries the LC Bridge logo and links home
Docs become a tree; Getting started is now video-led
Contact address is now arun@lcbridge.app
```

Bodies are prose paragraphs — what was wrong, what changed, what was deliberately
left alone, and what was verified. They are long on purpose; this repo has no
tests, so the commit message is the record.

Every commit ends with:

```
Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
```

### Branches

Work has gone **directly to `main`** recently. Stale branches exist
(`docusign-hero-video-and-ia-cleanup`, `seo-site-structure`,
`origin/docusign-pricing-and-copy`) — all merged or abandoned, safe to ignore.
Since `main` is production with no preview environment, verify locally *before*
pushing.

### Lint / format

None configured. No ESLint, Prettier, stylelint, or editorconfig. Match the
surrounding file's style — indentation and quoting vary between the `.lcb-*` pages
and the standalone ones.

### Verification standard (this is the actual quality gate)

There are no tests. The convention that replaced them: **drive the page in a
headless browser and read computed styles.** Static grepping misses cascade bugs —
the worst bug in this repo's history was `.lcb-body a` (0,1,1) beating
`.lcb-btn--primary` (0,1,0), invisible in the source.

Before pushing a visual change, check at **1280 and 390** minimum (360 if you touch
the nav):

- WCAG contrast on text and buttons (4.5:1, or 3:1 for ≥18.66px / ≥14px bold)
- `document.documentElement.scrollWidth > clientWidth` → horizontal overflow
- broken images, and stray text nodes in `<body>` (a malformed tag in `<head>`
  terminates head parsing and silently dumps the rest into the body)

Two traps that have produced false results here:

1. Use `waitUntil:'load'`, never `'domcontentloaded'` — stylesheets have not applied
   at DCL and every page reports phantom white-on-white failures.
2. The headless browser caches `/assets/brand.css`. Append a cache-buster query
   string to the page URL or a corrected stylesheet will keep rendering the old rule.

### Project CLAUDE.md

There is **no** `CLAUDE.md` in this repo. The rules that applied during recent work
live in the owner's global `~/.claude/CLAUDE.md`, and two are worth knowing:

- The `design-loop` skill is **explicit-request only** — do not auto-invoke it for
  general design work.
- Any substantial plan or decision gets a `devils-advocate` pass before it is
  handed over.

---

### Favicons

One mark sitewide, at the repo root: `favicon.ico` (16/32/48/64, each purpose-rendered),
`favicon.svg`, `apple-touch-icon.png` (180). Every page declares all three.

`favicon.svg` is a **deliberately simplified** variant of the brand mark — one centre
support instead of four piers, strokes at 2.6 rather than 1.6. The full four-pier
lockup dissolves into a smudge at the 16px Google renders in a result row. Do not
"restore" the detailed drawing here; the header and footer lockups carry it.

Google caches favicons independently of page crawls, often for weeks. A change here
will not show in search results quickly and there is no way to force it.

---

## 8. Open TODOs — already queued, do not duplicate

Ordered roughly by value. Items 1–3 need the owner; the rest are code.

1. **Unify the consent strings across the three GHL forms.** Compliance exposure,
   owner's task in HighLevel. See §6.
2. **Install analytics and tag the CTAs.** Plausible (~$9/mo, no cookie banner) was
   the recommendation. Nothing about conversion can be measured until this exists.
   The owner deferred it as a separate task.
3. **Retire two now-unused GHL assets:** form `TO5PG5GbMdM5I72xnUX0` and calendar
   `CwWPut2pYcgUSqeozTVA`. Both are unreferenced by the site.
4. **Nav-link contrast on the dark hero** — "About Us / Products / Blog / Contact"
   measure **3.01:1** against 4.5 required, on `index.html` and `products/index.html`,
   desktop only (hidden on mobile). Measured, reported, not fixed.
5. **Horizontal overflow at 360px** on `docusign-integration/insurance.html` and
   `real-estate.html`, caused by `.surface` blocks in the page body (not the nav).
   Confirmed pre-existing against `HEAD`.
6. **Decide the fate of unreferenced assets** — `assets/docusign-favicon.svg` (orphaned
   when favicons were consolidated to one sitewide mark), `assets/docusign-icon.svg`,
   `docusign-icon-180.png`, `lcbridge-logo.{svg,png}`, `lcbridge-lockup-dark.svg`,
   `hero-01.png`. Needs the owner to confirm the marketplace icon isn't among them.
7. **Internal markdown is publicly readable.** `brand/brand-guidelines.md` (200) and
   both `blog-drafts/*.md`, which Jekyll renders to `/blog-drafts/<slug>.html` (200,
   indexable). Decide whether that is intended; `_config.yml` `exclude` is the fix.
8. **Cloudflare in front of Pages** for real 301s, which retires all 22 redirect
   stubs. Recommended, not started.
9. **A brand-level OG image**, so `/book-a-call/` and `/community-agents/` stop
    sharing with no card.
10. **Fix the YouTube description on `fZ4Qpj5K-Lo`** — its chapter list runs to
    `13:30` but the video is `5:58`. Not a repo change; the timestamps are wrong on
    YouTube and break the chapter UI.
