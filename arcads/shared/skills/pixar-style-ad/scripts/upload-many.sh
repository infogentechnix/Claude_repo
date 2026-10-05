#!/bin/bash
# Upload N copies of the same file to separate temp presigned URLs.
# Echoes one filePath per line. Arcads temp uploads are single-use, so each
# parallel generation call needs its own copy.
#
# Usage: ./upload-many.sh <local-file> <mime-type> <count>
# Example: ./upload-many.sh stills/brent.png image/png 3
set -euo pipefail

set -a; source "${ENV_FILE:-$RUN_DIR/.env}" 2>/dev/null || source "$(git rev-parse --show-toplevel 2>/dev/null)/workspace/.env"; set +a

BASE="${ARCADS_BASE_URL:-https://external-api.arcads.ai}"
AUTH_HDR="Authorization: ${ARCADS_BASIC_AUTH:-Basic $(printf '%s:' "$ARCADS_API_KEY" | base64)}"

LOCAL_FILE="$1"; MIME="$2"; N="$3"

for _ in $(seq 1 "$N"); do
  resp=$(curl -sS -H "$AUTH_HDR" -H "Content-Type: application/json" \
    -X POST "$BASE/v1/file-upload/get-presigned-url" \
    -d "{\"fileType\":\"$MIME\"}")
  PRE=$(echo "$resp" | jq -r .presignedUrl)
  FP=$(echo "$resp" | jq -r .filePath)
  curl -sS -X PUT "$PRE" -H "Content-Type: $MIME" --data-binary "@$LOCAL_FILE" >/dev/null
  echo "$FP"
done
