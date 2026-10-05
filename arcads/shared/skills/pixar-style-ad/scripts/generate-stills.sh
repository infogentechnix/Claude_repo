#!/bin/bash
# Fire N gpt-image-2 image generation calls in parallel.
# Each call uses a different prompt; optionally each can pull a different
# reference image (for character continuity between beats).
#
# Reads jobs from STDIN, one per line:
#   <slot>::<prompt-text>::<optional-comma-separated-reference-image-filePaths>
#
# Example:
#   cat <<EOF | ./generate-stills.sh stills/batch-a
#   pain-cpm::Pixar-style $47.83 dollar amount character...::
#   brent-reveal::Pixar-style mid-30s man holding laptop...::external-api-temp-uploads/abc.png
#   EOF
#
# Required env: ARCADS_BASIC_AUTH, PRODUCT_ID, PROJECT_ID, RUN_DIR
set -euo pipefail

set -a; source "${ENV_FILE:-$RUN_DIR/.env}" 2>/dev/null || source "$(git rev-parse --show-toplevel 2>/dev/null)/workspace/.env"; set +a

BASE="${ARCADS_BASE_URL:-https://external-api.arcads.ai}"
AUTH_HDR="Authorization: ${ARCADS_BASIC_AUTH:-Basic $(printf '%s:' "$ARCADS_API_KEY" | base64)}"
MODEL="${IMAGE_MODEL:-gpt-image-2}"   # or nano-banana, nano-banana-2
ASPECT="${ASPECT_RATIO:-9:16}"

SUBDIR="$1"
OUT_DIR="$RUN_DIR/$SUBDIR/_resp"
mkdir -p "$OUT_DIR"

post_one() {
  local slot="$1" prompt="$2" refs_csv="$3"
  local refs_json='[]'
  if [[ -n "$refs_csv" ]]; then
    refs_json=$(echo "$refs_csv" | tr ',' '\n' | jq -R . | jq -s .)
  fi
  local body
  body=$(jq -n \
    --arg model "$MODEL" --arg productId "$PRODUCT_ID" --arg projectId "$PROJECT_ID" \
    --arg prompt "$prompt" --arg aspectRatio "$ASPECT" --argjson refs "$refs_json" \
    '{model:$model, productId:$productId, projectId:$projectId, prompt:$prompt, aspectRatio:$aspectRatio} + (if ($refs|length)>0 then {referenceImages:$refs} else {} end)')

  local resp
  resp=$(curl -sS -H "$AUTH_HDR" -H "Content-Type: application/json" \
    -X POST "$BASE/v2/images/generate" -d "$body")
  echo "$resp" > "$OUT_DIR/$slot.json"
  local id; id=$(echo "$resp" | jq -r '.id // empty')
  local status; status=$(echo "$resp" | jq -r '.status // empty')
  echo "[$slot] id=$id status=$status"
}

export -f post_one
export BASE AUTH_HDR PRODUCT_ID PROJECT_ID MODEL ASPECT OUT_DIR

PIDS=()
while IFS=$'\n' read -r line; do
  [[ -z "$line" || "$line" =~ ^# ]] && continue
  slot="${line%%::*}"; rest="${line#*::}"
  prompt="${rest%%::*}"; refs="${rest#*::}"
  post_one "$slot" "$prompt" "$refs" &
  PIDS+=($!)
done
for pid in "${PIDS[@]}"; do wait "$pid"; done

echo "=== Issued ${#PIDS[@]} stills. Now run poll-and-download.sh with the returned IDs. ==="
