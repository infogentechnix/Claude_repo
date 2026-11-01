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

## graphify

graphify 0.9.97 (Graphify-Labs/graphify, Apache-2.0) is installed project-locally: skill in `.claude/skills/graphify/`, PreToolUse hooks in `.claude/settings.json`. The CLI is not vendored; a SessionStart hook installs it with `uv tool install graphifyy` when missing. Run `graphify update .` to rebuild `graphify-out/` (gitignored).

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.

## ECC (Everything Claude Code)

ECC 2.2.3 (affaan-m/ECC, MIT) is installed project-locally with its own installer, trimmed to this repo's stack with the `agent-sort` skill. `/plugin` is unavailable here, so this replaces `/plugin install ecc@ecc`. Install state is in `.claude/ecc/install-state.json`.

- **DAILY (installed, loaded every session):**
  - ECC modules `rules-core`, `hooks-runtime`, `platform-configs` and `shared-script-utils`: rules in `.claude/rules/ecc/`, hook scripts in `.claude/scripts/`, and hooks merged into `.claude/settings.json`.
  - 15 skills: agent-sort, configure-ecc, ecc-guide, skill-stocktake, context-budget, gateguard, security-scan, python-patterns, python-testing, api-connector-builder, cost-aware-llm-pipeline, content-engine, marketing-campaign, brand-voice, video-editing.
  - Install command, run from an ECC checkout at the repo root: `install.sh --target claude-project --modules rules-core,hooks-runtime,platform-configs,shared-script-utils --skills agent-sort,configure-ecc,ecc-guide,skill-stocktake,context-budget,gateguard,security-scan,python-patterns,python-testing,api-connector-builder,cost-aware-llm-pipeline,content-engine,marketing-campaign,brand-voice,video-editing --enable-hooks`.
- **DAILY agents:** `python-reviewer` and `marketing-agent` are plain copies in `.claude/agents/`. ECC can only install agents as one 70-agent module, so these two are not ECC-managed.
- **LIBRARY (kept, not loaded):** the other 299 ECC skills, 68 agents and 98 commands are in `.claude/skill-library/`. The `skill-library` router skill lists them by area and explains how to use one or promote it to DAILY.
  - Several library entries overlap with skills that are already installed, for example `tdd-workflow`, `git-workflow`, `security-review`, `deep-research`, `api-design` and the `/code-review` and `/plan` commands. The agent-skills pack, the built-in skills or GSD cover those.
  - `strategic-compact` was left in the library on purpose: ECC files it under the whole `workflow-quality` module, so installing it pulls in 51 other skills.
- **Rules:** `rules-core` installs every language rule pack. They are path-scoped, so only `common/` and the packs matching edited files, such as `python/`, load.
- **Hook commands** contain absolute `/home/user/Claude_repo` paths.
- **Managing the install** (from an ECC checkout): `node scripts/ecc.js doctor --target claude-project` checks it; `repair` and `uninstall` manage it. Re-running the installer does not remove skills dropped from the selection. To change the selection, run `uninstall`, delete `.claude/ecc/install-state.json`, then reinstall.
- **Local hardening:**
  - `env.ECC_SKIP_LLM_SUMMARY=1` in `.claude/settings.json` stops the Stop hook from spawning `claude -p` to summarise the transcript.
  - Remove the `includeCoAuthoredBy: false` setting that the installer adds on every install, so commit attribution is unchanged.
  - The library copies of `kotlin-test`, `rust-test` and `update-docs` contain no literal example credentials.
- **GateGuard:** the hook denies the first Edit/Write of each file in a session and asks for facts first; the retry goes through. To skip it, set `ECC_GATEGUARD=off` or add a glob to `GATEGUARD_EXEMPT_GLOBS`.
