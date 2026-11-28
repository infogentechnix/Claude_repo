#!/usr/bin/env bash
# Refresh the vendored free-for.dev list from upstream (ripienaar/free-for-dev, master).
# Only the Markdown list is fetched; nothing is executed. Review `git diff free-for-dev/README.md` after.
set -euo pipefail
dir="$(cd "$(dirname "$0")" && pwd)"
url="https://raw.githubusercontent.com/ripienaar/free-for-dev/master/README.md"
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

curl -fsSL --retry 3 "$url" -o "$tmp"
# Sanity check: the list should still look like free-for.dev with many entries.
head -1 "$tmp" | grep -q '^# free-for.dev' || { echo "unexpected README header; not updating" >&2; exit 1; }
count="$(grep -cE '^ *\* \[' "$tmp" || true)"
[ "$count" -ge 500 ] || { echo "only $count entries; not updating" >&2; exit 1; }

mv "$tmp" "$dir/README.md"
trap - EXIT
sed -i "s/^Last synced: .*/Last synced: $(date -u +%F)/" "$dir/SOURCE.md"
echo "Updated free-for-dev/README.md ($count bullets). Review with: git diff free-for-dev/README.md"
