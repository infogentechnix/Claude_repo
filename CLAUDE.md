# Claude_repo

## Arcads (AI video and image ads)

The Arcads skill pack lives in `arcads/` (vendored from krusemediallc/arcads-claude-code, MIT).

- For any Arcads task, work from inside `arcads/` and follow @arcads/CLAUDE.md.
- Skills are synced to `arcads/.claude/skills/` by the SessionStart hook; resync with `bash arcads/scripts/sync-skill.sh`.
- Credentials go in `arcads/.env` (gitignored). If it is missing, have the user run `bash arcads/scripts/setup.sh`.
- Check connectivity with `bash arcads/scripts/check-arcads-env.sh`.

## Kimi K3

`kimi/kimi_k3.py` calls `moonshotai/kimi-k3` on NVIDIA's API; it reads `NVIDIA_API_KEY` from the environment or `kimi/.env`.

## GSD Core

GSD Core 1.16.0 (open-gsd/gsd-core, MIT) is installed project-locally in `.claude/` (agents, `/gsd-*` commands, `gsd-core/`, hooks wired in `.claude/settings.local.json`).

- Start with `/gsd-onboard` (existing code) or `/gsd-new-project`; `/gsd-health` checks the install.
- Reinstall/upgrade from the repo root: `npx @opengsd/gsd-core@latest --claude --local`. Installed files contain absolute `/home/user/Claude_repo` paths.
