#!/bin/bash
# Upload N copies of each storyboard still as Seedance startFrames.
# Writes a TSV mapping (slot, variation_index, filePath) to
# $RUN_DIR/references/seedance-startframes.txt for downstream use.
#
# Usage: ./upload-startframes.sh <variations-per-still>
# Reads still list from STDIN:
#   <slot>::<local-still-path>
#
# Example:
#   cat <<EOF | ./upload-startframes.sh 3
#   pain-cpm::stills/batch-a/pain-cpm.png
#   brent-reveal::stills/brent-final.png
#   EOF
set -euo pipefail

N="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UPLOAD="$SCRIPT_DIR/upload-many.sh"
MAP="$RUN_DIR/references/seedance-startframes.txt"
mkdir -p "$RUN_DIR/references"
: > "$MAP"

while IFS=$'\n' read -r line; do
  [[ -z "$line" || "$line" =~ ^# ]] && continue
  slot="${line%%::*}"
  path="${line#*::}"
  # Resolve relative paths against RUN_DIR
  [[ "$path" != /* ]] && path="$RUN_DIR/$path"
  mime="image/png"; [[ "$path" == *.jpg || "$path" == *.jpeg ]] && mime="image/jpeg"
  echo "uploading $N copies of $slot..." >&2
  paths=$("$UPLOAD" "$path" "$mime" "$N")
  i=1
  while IFS= read -r p; do
    echo "$slot:$i:$p" >> "$MAP"
    i=$((i+1))
  done <<< "$paths"
done

echo "Wrote $MAP ($(wc -l < "$MAP") entries)"
