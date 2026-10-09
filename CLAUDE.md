# Claude_repo

## Arcads (AI video and image ads)

The Arcads skill pack lives in `arcads/` (vendored from krusemediallc/arcads-claude-code, MIT).

- For any Arcads task, work from inside `arcads/` and follow @arcads/CLAUDE.md.
- Skills are synced to `arcads/.claude/skills/` by the SessionStart hook; resync with `bash arcads/scripts/sync-skill.sh`.
- Credentials go in `arcads/.env` (gitignored). If it is missing, have the user run `bash arcads/scripts/setup.sh`.
- Check connectivity with `bash arcads/scripts/check-arcads-env.sh`.

## Kimi K3

`kimi/kimi_k3.py` calls `moonshotai/kimi-k3` on NVIDIA's API; it reads `NVIDIA_API_KEY` from the environment or `kimi/.env`.

## YouTube agent skills

`.claude/skills/yt-*` (vendored from Jakeschincariol/youtube-agent-skill, MIT): `/yt-script`, `/yt-package`, `/yt-edit`, `/yt-comment`, `/yt-plan`, `/yt-viral`, `/yt-retention`, `/yt-shorts`, `/yt-seo`, `/yt-chapters`, `/yt-audit`. Their Python tools are stdlib-only (`python3 hookscore.py --hook "..."` in `yt-script/`). Skills read the voice profile at `~/.claude/youtube/voice.md`; a blank template is in `.claude/youtube/voice.md.template`.
