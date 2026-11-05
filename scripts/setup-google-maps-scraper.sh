#!/usr/bin/env bash
# Set up gosom/google-maps-scraper in this checkout. Safe to run repeatedly:
# it clones only if missing, rebuilds only if the binary is missing or older
# than HEAD, and refreshes the browser symlinks every time.
#
# Usage: scripts/setup-google-maps-scraper.sh [--update] [--no-build]
#   --update    git pull the existing clone before building
#   --no-build  skip clone/build, only refresh the Playwright browser links
#
# Env overrides:
#   GMS_DIR              clone location (default: <repo>/google-maps-scraper)
#   PW_SRC               preinstalled browsers (default: /opt/pw-browsers)
#   PLAYWRIGHT_BROWSERS_PATH  where the scraper looks (default: ~/.cache/ms-playwright)
#   PW_CHROMIUM_REV      revision the scraper's Playwright driver expects
#                        (default: read from the driver's browsers.json, else 1228)
#   PW_FFMPEG_REV        same for ffmpeg (default: browsers.json, else 1011)
set -euo pipefail

REPO_URL="https://github.com/gosom/google-maps-scraper.git"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GMS_DIR="${GMS_DIR:-$ROOT/google-maps-scraper}"
PW_SRC="${PW_SRC:-/opt/pw-browsers}"
PW_DST="${PLAYWRIGHT_BROWSERS_PATH:-$HOME/.cache/ms-playwright}"

update=0
build=1
for arg in "$@"; do
  case "$arg" in
    --update) update=1 ;;
    --no-build) build=0 ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

log() { printf '[gms-setup] %s\n' "$*"; }

if [ "$build" -eq 1 ]; then
  command -v git >/dev/null || { echo "git is required" >&2; exit 1; }
  command -v go >/dev/null || { echo "go is required (any version; GOTOOLCHAIN=auto fetches the one go.mod needs)" >&2; exit 1; }

  if [ -d "$GMS_DIR/.git" ]; then
    log "clone exists at $GMS_DIR"
    if [ "$update" -eq 1 ]; then
      log "pulling latest"
      git -C "$GMS_DIR" pull --ff-only
    fi
  elif [ -e "$GMS_DIR" ]; then
    echo "$GMS_DIR exists but is not a git clone; move it aside and rerun" >&2
    exit 1
  else
    log "cloning $REPO_URL"
    git clone --depth 1 "$REPO_URL" "$GMS_DIR"
  fi

  bin="$GMS_DIR/google-maps-scraper"
  head_time="$(git -C "$GMS_DIR" log -1 --format=%ct)"
  if [ -x "$bin" ] && [ "$(stat -c %Y "$bin")" -ge "$head_time" ]; then
    log "binary is up to date, skipping build"
  else
    log "building (first run downloads the Go toolchain from go.mod)"
    (cd "$GMS_DIR" && GOTOOLCHAIN=auto go build -o google-maps-scraper .)
  fi
fi

# Playwright's CDN is blocked in cloud sessions, so point the scraper at the
# browsers that ship in the image. The driver looks for <name>-<its revision>,
# which differs from the preinstalled revision, hence the symlinks.
browsers_json="$(ls -1d "$HOME"/.cache/ms-playwright-go/*/package/browsers.json 2>/dev/null | sort -V | tail -n1 || true)"
rev_from_json() {
  [ -n "$browsers_json" ] || return 0
  python3 -c 'import json,sys
for b in json.load(open(sys.argv[1]))["browsers"]:
    if b["name"] == sys.argv[2]: print(b["revision"]); break' "$browsers_json" "$1" 2>/dev/null || true
}
chromium_rev="${PW_CHROMIUM_REV:-$(rev_from_json chromium)}"
chromium_rev="${chromium_rev:-1228}"
ffmpeg_rev="${PW_FFMPEG_REV:-$(rev_from_json ffmpeg)}"
ffmpeg_rev="${ffmpeg_rev:-1011}"

latest() { ls -1d "$PW_SRC/$1"-[0-9]* 2>/dev/null | sort -V | tail -n1; }

mkdir -p "$PW_DST"
linked=0
for name in chromium chromium_headless_shell ffmpeg; do
  src="$(latest "$name")"
  if [ -z "$src" ]; then
    log "no $name in $PW_SRC, skipping"
    continue
  fi
  rev="$chromium_rev"
  [ "$name" = ffmpeg ] && rev="$ffmpeg_rev"
  dst="$PW_DST/$name-$rev"
  if [ "$src" = "$dst" ]; then continue; fi
  if [ -e "$dst" ] && [ ! -L "$dst" ]; then
    log "$dst is a real install, leaving it"
    continue
  fi
  ln -sfn "$src" "$dst"
  log "linked $dst -> $src"
  linked=$((linked + 1))
done
log "$linked browser link(s) refreshed in $PW_DST"

cat <<EOF
[gms-setup] done. Run it with:
  PLAYWRIGHT_BROWSERS_PATH=$PW_DST $GMS_DIR/google-maps-scraper -input queries.txt -results results.csv -depth 1 -exit-on-inactivity 3m
[gms-setup] scraping needs www.google.com allowed in the environment's network settings.
EOF
