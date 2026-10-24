# LC Bridge — Brand Guidelines (v2 · "Refined Cobalt")

LC Bridge builds products and custom software for GoHighLevel (also called HighLevel or GHL). The **product** is a white-label chameleon — it inherits each agency's HighLevel branding at runtime. This guide governs the **LC Bridge marketing identity only**; it never needs to match the product UI.

- **Source of truth:** `/assets/brand.css` (tokens + components). Build pages from it; don't hardcode hex/px.
- **Visual reference:** `/brand/` (rendered guidelines page).

---

## 1. Logo
- Bridge glyph in a gradient tile + **"LC Bridge"** wordmark. Use the approved artwork rather than recreating its lettering.
- **DocuSign product icon (the document + signature glyph):** `/assets/docusign-icon.svg` (+ raster `/assets/docusign-icon-180.png`, 180×180, transparent). Synced from the product repo (`~/dev/docusign-product`, the "DocuSign Integration by LCBridge" mark), this glyph marks the DocuSign CTA **inside the product** — it is not the corporate brand logo.
- **LC Bridge brand logo (the bridge mark):** `/assets/lcbridge-logo.svg` (+ social-ready raster `/assets/lcbridge-logo.png`, 1024×1024, transparent). The bridge glyph on the cobalt→violet gradient tile, exactly as shown on the lcbridge.app home page. Use this for the corporate identity and social profiles; do not redraw the glyph.
- **Company and product hierarchy:** keep the shared LC Bridge navigation above each product’s local navigation, and the shared company footer below the product content. Google Sheets, Community Agents and DocuSign retain their approved product logos and palettes. Product discovery follows that order; the company homepage introduces the full portfolio.
- Always two words: **LC Bridge**. Do not invent a registered legal name or an ownership relationship. Use LC Bridge’s own identity and contact details in copy, footers and schema.
- The gradient `linear-gradient(135deg,#2A41D8,#6938EF)` is the **only** sanctioned gradient and lives on the **mark only** — never on text, buttons, or backgrounds.
- Clear space ≥ the mark's height. Minimum mark size 24px (favicon/UI); minimum full lockup ~120px wide. Never stretch, rotate, or recolor the wordmark.

## 2. Color
**One brand color (cobalt). Violet is AI-only and always labelled. Status hues are shared verbatim with the product.**

| Role | Hex | Use |
|---|---|---|
| Cobalt — Primary | `#2A41D8` | Buttons, links, focal accents |
| Cobalt — Press | `#2235B5` | Hover / active |
| Ink | `#0B1220` | Headlines, body |
| Ink-2 | `#475467` | Sub-copy |
| Ink-3 | `#667085` | Meta, captions |
| Canvas | `#FFFFFF` | Default background |
| Soft | `#F5F7FA` | Alternating sections |
| Cobalt tint | `#EEF1FE` | Icon tiles, subtle fills |
| Dark | `#0B1120` | Hero / footer ground |
| Line | `#E2E5EC` / `#EAECF2` | Borders, dividers |

**AI accent (violet — AI moments only):** `#6938EF` (mark) · `#5925DC` (text) · `#F5F3FF` (bg) · `#DDD6FE` (border). Always paired with a label ("AI summary", "AI read", "Drafted by AI").

**Status (hue + label + dot — never colour alone):**
| State | fg | bg | dot | border |
|---|---|---|---|---|
| Completed | `#027A48` | `#ECFDF3` | `#17B26A` | `#ABEFC6` |
| On track | `#175CD3` | `#EFF8FF` | `#2E90FA` | `#B2DDFF` |
| Needs attention | `#B54708` | `#FFFAEB` | `#F79009` | `#FEC84B` |
| Declined | `#B42318` | `#FEF3F2` | `#F04438` | `#FECDCA` |
| Draft | `#344054` | `#F2F4F7` | `#98A2B3` | `#EAECF0` |

## 3. Typography

| Role | Face and weight | Size / leading | Spacing and case |
|---|---|---|---|
| Company display headings | Poppins 700 | Responsive; see `lcb-display` and `lcb-h2` | Tracking `-0.03em` to `-0.025em`; sentence case |
| Body and navigation | Inter 400/500/600 | Body 16px / 1.55; longer paragraphs up to 1.75 | Normal spacing; sentence case |
| Eyebrows, section labels and short captions | Inter 600 | **13px / 1.5**, including mobile | **`.01em`**, sentence case |
| Supporting captions and badges | Inter 400/500/600 | 12–13px / 1.5 or more | Normal spacing; sentence case |
| Prices, metrics and counts | Inter with tabular numerals | Match the surrounding hierarchy | Use `lcb-num`; numbers do not require a monospace face |
| Code, record IDs and aligned technical data | JetBrains Mono 400/500/600 | At least 12px in readable content | Preserve exact code/identifier casing |

**Reusable label role:** `--lcb-font-label`, `--lcb-label-size`, `--lcb-label-weight`, `--lcb-label-leading` and `--lcb-label-tracking` in `/assets/brand.css`. Use `.lcb-eyebrow` for section introductions and `.lcb-label` for other short labels. Page-specific components should consume these tokens rather than introduce another label font.

**Permanent rules:**

- No decorative monospace for marketing eyebrows, badges, navigation, captions or footer headings. Do not style these like terminal output.
- No widely spaced all-caps kickers. Write sentence case in HTML; keep proper names and acronyms such as **LC Bridge**, **GoHighLevel**, **AI**, **CRM** and **API** intact. Do not force capitalization through CSS.
- Keep labels at 13px by default and **never reduce them below 12px at a mobile breakpoint**. Allow wrapping instead of shrinking text to fit.
- Build hierarchy with weight, size and spacing. Use color as supporting emphasis with readable contrast.
- Keep approved product typography inside each product container; shared LC Bridge chrome uses the company system. Do not override code blocks, data tables or actual product UI just to change marketing labels.
- Use the existing self-hosted WOFF2 faces in `/assets/fonts.css` and preload the critical text/display faces. This label role uses the already loaded Inter face and adds no font download.
- Before shipping, inspect desktop and mobile screenshots, check the actual computed font/size/spacing, and confirm that labels wrap without clipping or horizontal page overflow.

Examples: **“LC Bridge / Built for GoHighLevel”**, **“LC Bridge products”**, **“01 / Our products”**. Avoid their all-caps, tracked monospace equivalents.

## 4. Components (in `/assets/brand.css`)
`lcb-wrap` · `lcb-label` · `lcb-eyebrow` · `lcb-btn` (`--primary` / `--ghost` / `--lg`) · `lcb-badge` (`is-completed|ontrack|attention|declined|draft`) · `lcb-ai` · `lcb-card` (`--hover`) · `lcb-logo` · `lcb-section` (`--soft` / `--dark`) · type helpers `lcb-display` / `lcb-h2` / `lcb-lede` / `lcb-num`.
Radii: sm 7 · md 11 · lg 14 · xl 18 · pill. Motion: 180ms `cubic-bezier(.4,0,.2,1)`; honor `prefers-reduced-motion`.

## 5. Voice & tone
Calm, plain, operator-to-operator. **Sentence case. No emoji.** Concrete over abstract. Tabular numbers. Honest claims — say **"inherits your HighLevel white-label branding,"** not "detects your theme"; no fabricated stats/logos. One focal idea per screen — don't make the reader think.

## 6. Do / Don't
**Do:** flat decisive cobalt on white · hierarchy by weight/scale · violet only for labelled AI · shared status hues · real product visuals + honest numbers · the single gradient on the logo mark only.

**Don't:** blue→violet gradients on heroes/headings/buttons (the #1 AI tell) · a thick colored border down one side of a card (a top AI-UI tell) · generic indigo `#6366F1` or rainbow accents · the Space Grotesk + Inter default combo · emoji / Title Case / hype adjectives · glassmorphism + neon glow.


## 7. Google Sheets integration: the highlighter look
The approved marketing look for the Google Sheets integration, first used in the LevelUp 2026 v2 ads, landing page and report carousel (approved by Karthik on 2026-10-24). It applies to ads, social posts, carousels, landing pages and product marketing pages. It does **not** apply inside the product UI.

**The highlighter**
- `#FFE14D` behind the 2–5 words that carry the point: the pain or the payoff. Text inside stays near-black (`#111111`, or Forest Ink `#17392B` on web), in light and dark mode.
- At most once per headline and once per section. Never on body copy, buttons, links, numbers in tables or legal text.
- Web: `<mark class="hl">` (`background:#ffe14d; padding:0 .12em; border-radius:2px; box-decoration-break:clone`) so it wraps cleanly across lines.

**High contrast, native feel**
- White ground, near-black heavy type (Roboto or Inter 800–900, tight tracking), green only on actions (Action Green `#106F43`) and good-news cells.
- Product frames in ads use a 4px black border and a soft neutral shadow, so the sheet reads at phone size. Errors show as red `#N/A` / `#REF!` cells, results as green cells.
- Label anything illustrative as **Sample data**.

**Ad structure (shorts and carousels)**
- Frame 0 already shows the pain: a headline plus the broken sheet. No logo intro, no blank or dark first frame.
- The same object is fixed by about 3 seconds ("Same sheet. Matched for you.").
- The objection line ("Two-way with HighLevel. No Zapier. No CSVs.") comes before the offer card.
- Offer card in Action Green: **See 25 free report templates · No signup · lcbridge.app**. Do not say "Get early access" in ads or hero films.
- 9:16: keep all text above the bottom 20% (y < 1536 px of 1920). Carousels: 1:1, one question per card, one readable mini dashboard.

**Do not:** add a second highlight colour, highlight whole sentences, put the highlighter on green, or use it as decoration without a point.

Reference files: `sheets-sync-prototype/marketing/levelup/ads/review/v2-mock.html`, `ads/build_v2.py`, `ads/carousel/carousel.html`; live on `/google-sheets-integration/` and `/google-sheets-integration/levelup/`.

---
*v2 · Google Sheets highlighter look added 2026-10-24. Typography revised 2026-10-16: readable Inter labels replace decorative monospace. Refined Cobalt chosen 2026-06-22.*
