# Claude_repo

## Arcads (AI video and image ads)

The Arcads skill pack lives in `arcads/` (vendored from krusemediallc/arcads-claude-code, MIT).

- For any Arcads task, work from inside `arcads/` and follow @arcads/CLAUDE.md.
- Skills are synced to `arcads/.claude/skills/` by the SessionStart hook; resync with `bash arcads/scripts/sync-skill.sh`.
- Credentials go in `arcads/.env` (gitignored). If it is missing, have the user run `bash arcads/scripts/setup.sh`.
- Check connectivity with `bash arcads/scripts/check-arcads-env.sh`.

## Kimi K3

`kimi/kimi_k3.py` calls `moonshotai/kimi-k3` on NVIDIA's API; it reads `NVIDIA_API_KEY` from the environment or `kimi/.env`.

## OpenRouter free models

`openrouter/free-models.md` is a reference list of OpenRouter's `:free` models, rate limits and deprecations (from gist rlnorthcutt/e6f392cd1ffb1339cc42dfb024c3cf7f). Several models listed there were slated for deprecation in July 2026; check https://openrouter.ai/models before relying on one.

`openrouter/openrouter_chat.py` calls OpenRouter's chat API (default model `openrouter/free`, override with `--model`); it reads `OPENROUTER_API_KEY` from the environment or `openrouter/.env`.

## Agent Skills (engineering workflows)

`.claude/skills/` also holds the 25 engineering skills from addyosmani/agent-skills (MIT, v0.6.13; license in `.claude/references/AGENT-SKILLS-LICENSE`): spec, planning, TDD, code review, security, performance, shipping, etc. Start with `using-agent-skills` to pick one. Shared checklists live in `.claude/references/`, and the `code-reviewer`, `security-auditor`, `test-engineer` and `web-performance-auditor` subagents in `.claude/agents/`. The upstream slash commands and hooks were not vendored (`/review` clashes with the built-in); to get them, install the plugin with `/plugin marketplace add addyosmani/agent-skills` then `/plugin install agent-skills@addy-agent-skills`.

## GSD Core

GSD Core 1.16.0 (open-gsd/gsd-core, MIT) is installed project-locally in `.claude/` (agents, `/gsd-*` commands, `gsd-core/`, hooks wired in `.claude/settings.local.json`).

- Start with `/gsd-onboard` (existing code) or `/gsd-new-project`; `/gsd-health` checks the install.
- Reinstall/upgrade from the repo root: `npx @opengsd/gsd-core@latest --claude --local`. Installed files contain absolute `/home/user/Claude_repo` paths.
