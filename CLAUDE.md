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
