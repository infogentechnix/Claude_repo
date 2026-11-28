# free-for-dev (vendored)

Source: https://github.com/ripienaar/free-for-dev (site: https://free-for.dev)
Upstream commit: 6191ff673ba9beb5216519173c4cfb3e2f57f80c (2026-11-27)
Last synced: 2026-11-28

A community list of SaaS, PaaS and IaaS offerings with free tiers for developers (about 1,400 entries in 57 sections).

## What is here

- `README.md`, the list itself, unmodified. `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` are upstream files, also unmodified.
- `search.py` (ours): keyword and section search over the list. `test_search.py` holds its tests.
- `update.sh` (ours): refreshes `README.md` from upstream master.

Not vendored: `index.html` (the docsify website, which loads Google Analytics), `CNAME`, `logo.webp`, `.github/`.

## Notes

- Upstream has no LICENSE file. This copy is kept for reference; do not republish it as our own.
- Upstream does not accept AI-made contributions (see `CLAUDE.md`). Do not open PRs to it from here.
- Free tiers change often. Check the provider's own pricing page before relying on a limit.
- SkillSpector rated the repo DO_NOT_INSTALL. Every finding was a false positive from service descriptions: the word `.env` in the Dotenv entry, the PR template's HTML comment, and phrases like "unlimited requests". The repo has no executable code and no hidden Unicode. The user accepted the risk on 2026-11-28 (`skillspector/scan.sh --accept`).
