# LC Bridge — Brand Guidelines (v1 · "Refined Cobalt")

LC Bridge (legal: **Lead Connector Bridge**) builds white-label integrations that run inside the HighLevel (GoHighLevel) CRM. The **product** is a white-label chameleon — it inherits each agency's HighLevel branding at runtime. This guide governs the **LC Bridge marketing identity only**; it never needs to match the product UI.

- **Source of truth:** `/assets/brand.css` (tokens + components). Build pages from it; don't hardcode hex/px.
- **Visual reference:** `/brand/` (rendered guidelines page).

---

## 1. Logo
- Bridge glyph in a gradient tile + **"LC Bridge"** wordmark (Inter Tight 700).
- **DocuSign product icon (the document + signature glyph):** `/assets/docusign-icon.svg` (+ raster `/assets/docusign-icon-180.png`, 180×180, transparent). Synced from the product repo (`~/dev/docusign-product`, the "DocuSign Integration by LCBridge" mark), this glyph marks the DocuSign CTA **inside the product** — it is not the corporate brand logo.
- **LC Bridge brand logo (the bridge mark):** `/assets/lcbridge-logo.svg` (+ social-ready raster `/assets/lcbridge-logo.png`, 1024×1024, transparent). The bridge glyph on the cobalt→violet gradient tile, exactly as shown on the leadconnectorbridge.com home page. Use this for the corporate identity and social profiles; do not redraw the glyph.
- **Per-product pages re-brand:** product landing pages (`/docusign/*`, `/google-sheets/`) lead with that product's own colors + logo (DocuSign = Cobalt `#4C00FF` / Inkwell `#130032` / Poppy Red `#FF5252`; Google Sheets = green `#0F9D58`) so the page instantly maps to the integration. LC Bridge's cobalt identity is reserved for the home/corporate page and the "by LC Bridge" byline.
- Always two words: **LC Bridge**. Use the full legal name **Lead Connector Bridge** only at first mention, in footers, and in schema.
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
- **Display:** Inter Tight (700), tracking `-0.03em` → `-0.025em`.
- **Text:** Inter (400/500/600), line-height ~1.55.
- **Eyebrows / labels / figures:** JetBrains Mono (600), `.14em`, UPPERCASE for kickers; tabular nums for prices/counts.
- Hierarchy comes from **weight + scale**, never from color.

## 4. Components (in `/assets/brand.css`)
`lcb-wrap` · `lcb-eyebrow` · `lcb-btn` (`--primary` / `--ghost` / `--lg`) · `lcb-badge` (`is-completed|ontrack|attention|declined|draft`) · `lcb-ai` · `lcb-card` (`--hover`) · `lcb-logo` · `lcb-section` (`--soft` / `--dark`) · type helpers `lcb-display` / `lcb-h2` / `lcb-lede` / `lcb-num`.
Radii: sm 7 · md 11 · lg 14 · xl 18 · pill. Motion: 180ms `cubic-bezier(.4,0,.2,1)`; honor `prefers-reduced-motion`.

## 5. Voice & tone
Calm, plain, operator-to-operator. **Sentence case. No emoji.** Concrete over abstract. Tabular numbers. Honest claims — say **"inherits your HighLevel white-label branding,"** not "detects your theme"; no fabricated stats/logos. One focal idea per screen — don't make the reader think.

## 6. Do / Don't
**Do:** flat decisive cobalt on white · hierarchy by weight/scale · violet only for labelled AI · shared status hues · real product visuals + honest numbers · the single gradient on the logo mark only.

**Don't:** blue→violet gradients on heroes/headings/buttons (the #1 AI tell) · a thick colored border down one side of a card (a top AI-UI tell) · generic indigo `#6366F1` or rainbow accents · the Space Grotesk + Inter default combo · emoji / Title Case / hype adjectives · glassmorphism + neon glow.

---
*v1 · Refined Cobalt · chosen 2026-06-22. Supersedes the prior blue→violet-gradient marketing look.*
