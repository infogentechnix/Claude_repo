# Arcads setup on Windows

Claude Code on Windows runs hooks with Git Bash, so install [Git for Windows](https://git-scm.com/download/win) and Python 3.10+ first.

1. Open **Git Bash** in this `arcads` folder and run:
   ```bash
   ./scripts/setup.sh
   ```
   Paste your Arcads API key (from https://app.arcads.ai/settings/api) when asked. It is saved to `.env`, which is never committed.
2. Start Claude Code in this folder:
   ```bash
   claude
   ```
   The SessionStart banner should show `✓ .env`, `✓ MASTER_CONTEXT.md` and 6 synced skills.
3. Try: "Generate a Nano Banana image ad for [your product]".

Optional tools, only for some workflows:
- Video stitching, Pixar-style and claymation ads, captions: `winget install Gyan.FFmpeg` and `winget install jqlang.jq`
- Captions: `py -m pip install openai-whisper`, plus Node.js
- Publishing to Meta: `py -m pip install -r shared/skills/meta-ad-builder/scripts/requirements.txt`
