---
name: free-for-dev
description: Find free-tier developer services (hosting, databases, CI/CD, email, auth, monitoring, logging, storage, CDN, DNS, APIs, generative AI, analytics, forms, payments, etc.) from the vendored free-for.dev list. Use whenever a task needs a third-party service, SaaS, API or infrastructure and cost matters, or the user asks for something "free", a "free tier", or alternatives to a paid tool.
---

# free-for-dev

The vendored list in `free-for-dev/README.md` (from ripienaar/free-for-dev) has about 1,400 services with free tiers, in 57 sections.

## How to use it

1. Search it rather than reading the 1,800-line README:
   ```bash
   python3 free-for-dev/search.py <keywords...>          # every keyword must match
   python3 free-for-dev/search.py --section "web hosting"
   python3 free-for-dev/search.py --sections             # list sections with counts
   python3 free-for-dev/search.py postgres -n 0          # all matches
   ```
   Exit code 1 means nothing matched. Try fewer or broader keywords, or a `--section`.
2. Shortlist 2–4 options that fit the task (limits, region, signup needs) and give the user the name, link and free-tier limit for each.
3. Free tiers change. Before wiring a service into code or recommending it firmly, check its pricing page (WebFetch) and say when a limit is unverified. `free-for-dev/SOURCE.md` has the sync date.
4. Prefer services already used in this repo (OpenRouter, NVIDIA API, Vercel, and others) when they fit.

## Maintenance

- Refresh the list: `bash free-for-dev/update.sh`, then review `git diff free-for-dev/README.md`.
- Tests: `python3 -m pytest free-for-dev -q`.
- Do not open PRs to upstream from here: it does not accept AI-made contributions.
