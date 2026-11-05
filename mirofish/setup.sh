#!/usr/bin/env bash
# Installs MiroFish (https://github.com/666ghj/MiroFish) into mirofish/app/.
# Called by the SessionStart hook in .claude/settings.json so a fresh cloud
# session gets MiroFish back. Does nothing when the install is already complete.
#
#   bash mirofish/setup.sh            # install if missing (runs in foreground)
#   bash mirofish/setup.sh --bg       # same, but detached; log at mirofish/install.log
#   bash mirofish/setup.sh --force    # wipe mirofish/app and reinstall
#
# Env overrides: MIROFISH_REPO (git URL), MIROFISH_REF (branch/tag, default main).
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
APP="$DIR/app"
LOG="$DIR/install.log"
MARKER="$APP/.mirofish-installed"
LOCK="$DIR/.install.lock"
REPO="${MIROFISH_REPO:-https://github.com/666ghj/MiroFish.git}"
REF="${MIROFISH_REF:-main}"

link_env() {
  # Keep secrets in mirofish/.env (gitignored); MiroFish reads app/.env.
  if [[ -f "$DIR/.env" && -d "$APP" ]]; then
    ln -sf "$DIR/.env" "$APP/.env"
  fi
}

case "${1:-}" in
  --bg)
    [[ -f "$MARKER" ]] && { link_env; exit 0; }
    nohup bash "$0" >"$LOG" 2>&1 </dev/null &
    echo "MiroFish not installed yet; installing in background (log: mirofish/install.log)"
    exit 0 ;;
  --force)
    rm -rf -- "$APP" ;;
esac

if [[ -f "$MARKER" ]]; then
  link_env
  echo "MiroFish already installed at $APP"
  exit 0
fi

# One installer at a time.
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "Another MiroFish install is running; skipping"
  exit 0
fi

for tool in git node npm; do
  command -v "$tool" >/dev/null 2>&1 || { echo "MiroFish setup: $tool not found" >&2; exit 1; }
done
if ! command -v uv >/dev/null 2>&1; then
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "[$(date -u +%FT%TZ)] Installing MiroFish ($REF) into $APP"
if [[ ! -d "$APP/.git" ]]; then
  rm -rf -- "$APP"
  git clone --depth 1 --branch "$REF" "$REPO" "$APP"
fi

cd "$APP"
# Root deps (concurrently) + frontend deps.
npm install --no-audit --no-fund
(cd frontend && npm install --no-audit --no-fund)
# Backend needs Python 3.11/3.12; uv fetches a matching interpreter if needed.
(cd backend && uv sync --python 3.12)

link_env
date -u +%FT%TZ > "$MARKER"
echo "[$(date -u +%FT%TZ)] MiroFish install complete"
