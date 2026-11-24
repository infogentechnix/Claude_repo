#!/usr/bin/env bash
# Scan a repo, URL, archive or directory with NVIDIA SkillSpector before installing it.
#
#   bash skillspector/scan.sh <git-url | path | zip>           # static scan, records the verdict
#   bash skillspector/scan.sh --accept <git-url | path | zip>  # user explicitly accepts a REJECT verdict
#
# Exit codes: 0 = APPROVE or CAUTION (recorded as scanned), 1 = REJECT (not recorded), 2 = scan error.
# Verdicts are logged to .claude/skillspector/scanned.log, which the install gate hook reads.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT/.claude/skillspector"
LOG="$LOG_DIR/scanned.log"
REPORT_DIR="${TMPDIR:-/tmp}/skillspector-reports"

ACCEPT=0
if [[ "${1:-}" == "--accept" ]]; then ACCEPT=1; shift; fi
TARGET="${1:-}"
if [[ -z "$TARGET" ]]; then
  echo "usage: $0 [--accept] <git-url | path | zip>" >&2
  exit 2
fi

if ! command -v skillspector >/dev/null 2>&1; then
  echo "skillspector not found; installing with uv..." >&2
  uv tool install --python 3.13 git+https://github.com/NVIDIA/SkillSpector.git >/dev/null 2>&1 || {
    echo "Could not install skillspector. Install it manually, then rerun." >&2
    exit 2
  }
fi

mkdir -p "$LOG_DIR" "$REPORT_DIR"
KEY="$(python3 "$ROOT/.claude/hooks/skillspector-install-gate.py" --key "$TARGET")"
REPORT="$REPORT_DIR/$(echo "$KEY" | tr '/:' '__').json"

skillspector scan "$TARGET" --no-llm --format json --output "$REPORT" >/dev/null 2>&1
SCAN_EXIT=$?
if [[ ! -s "$REPORT" ]]; then
  echo "SkillSpector scan failed (exit $SCAN_EXIT) and wrote no report for: $TARGET" >&2
  exit 2
fi

read -r SCORE SEVERITY VERDICT MAXSEV COUNT < <(python3 -I - "$REPORT" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
r = d.get("risk_assessment", {})
print(r.get("score", "?"), r.get("severity", "?"), r.get("recommendation", "?"),
      r.get("max_issue_severity", "NONE"), len(d.get("issues", [])))
PY
)

echo "SkillSpector: $TARGET"
echo "  verdict=$VERDICT  score=$SCORE/100  severity=$SEVERITY  max_issue=$MAXSEV  findings=$COUNT"
echo "  report: $REPORT"
python3 -I - "$REPORT" <<'PY'
import json, sys
issues = json.load(open(sys.argv[1])).get("issues", [])
rank = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
issues.sort(key=lambda i: rank.get(str(i.get("severity", "")).upper(), 9))
for i in issues[:10]:
    loc = i.get("location") or {}
    where = f"{loc.get('file', '')}:{loc.get('start_line', '')}" if isinstance(loc, dict) else str(loc)
    print(f"  - [{i.get('severity', '?')}] {i.get('id', '')} {i.get('pattern', '')}: "
          f"{i.get('explanation', '')} ({where})")
if len(issues) > 10:
    print(f"  ... {len(issues) - 10} more in the report")
PY

STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
if [[ "$VERDICT" == "REJECT" && $ACCEPT -eq 0 ]]; then
  echo "REJECT: do not install. Only rerun with --accept if the user explicitly accepts the risk." >&2
  exit 1
fi
[[ $ACCEPT -eq 1 ]] && VERDICT="$VERDICT(user-accepted)"
printf '%s\t%s\t%s\t%s\n' "$KEY" "$VERDICT" "$SCORE" "$STAMP" >> "$LOG"
echo "Recorded $KEY as scanned ($VERDICT). Installs of it are now allowed by the gate."
exit 0
