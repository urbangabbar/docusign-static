# LC Bridge website maintenance

## GitHub identity

This is a Community Agents-related repository. Use `karthik-sheetstack` for authenticated GitHub operations. Switch with `gh auth switch --hostname github.com --user karthik-sheetstack`, verify `gh api user --jq .login`, and verify the effective identity for Git credentials or environment overrides. Scope credentials per command if concurrent tasks could race. Preserve commit author settings.

## Every public content or URL change

Apply [lcbridge-search-sync](skills/lcbridge-search-sync/SKILL.md) whenever adding, changing, moving, or deleting public content. Run `python3 scripts/sync-search.py --write`, `python3 scripts/sync-search.py`, and `python3 scripts/check-site.py` before publishing. The publishing workflow repeats generation and validation automatically on every main push.

Every public page, including listing and hierarchy pages, must have a matching canonical, be crawlable, and be linked from the public site. Explicitly classify genuinely internal pages in `data/search-policy.json`. Never silently omit a public page because of missing SEO metadata or an accidental noindex.

After deployment, reconcile Google Search Console through GSC Wizard and individual Request indexing actions in Google's UI. The hourly LC Bridge search maintenance heartbeat handles changes made outside this task and pending quota-limited requests. An inspection or tracker registration is not an indexing request; record accepted requests and Google's eventual indexing separately.
