#!/usr/bin/env bash
# Sets up Wan2GP (https://github.com/deepbeepmeep/Wan2GP) on a GPU machine
# and launches the web server bound to all interfaces.
#
# Usage: ./setup.sh [install-dir] [port]

set -euo pipefail

INSTALL_DIR="${1:-$HOME/Wan2GP}"
PORT="${2:-7860}"
REPO_URL="https://github.com/deepbeepmeep/Wan2GP"

if [ ! -d "$INSTALL_DIR/.git" ]; then
  git clone "$REPO_URL" "$INSTALL_DIR"
else
  echo "Wan2GP already cloned at $INSTALL_DIR, skipping clone."
fi

cd "$INSTALL_DIR"

if [ -x "./install.sh" ]; then
  ./install.sh
else
  echo "install.sh not found or not executable in $INSTALL_DIR" >&2
  exit 1
fi

python wgp.py --listen --server-name 0.0.0.0 --server-port "$PORT"

