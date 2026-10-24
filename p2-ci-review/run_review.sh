#!/bin/bash
# Multi-pass review: one pass per file, then one integration pass.
set -e
cd "$(dirname "$0")/../p1-team-setup"
OUT=../p2-ci-review/out
mkdir -p "$OUT"
CRITERIA="$(cat ../p2-ci-review/criteria.md)"
SCHEMA="$(cat ../p2-ci-review/review-schema.json)"

for f in src/orders/service.py src/orders/api.py src/orders/models.py; do
  name=$(basename "$f" .py)
  echo "Pass 1 (per file): $f"
  claude -p "$CRITERIA

Review only this file: $f. Ignore every other file." \
    --allowedTools "Read,Grep,Glob" \
    --output-format json --json-schema "$SCHEMA" > "$OUT/$name.json"
done

PREVIOUS="$(cat "$OUT"/service.json "$OUT"/api.json "$OUT"/models.json)"
echo "Pass 2 (integration)"
claude -p "$CRITERIA

You are the integration reviewer for src/orders/service.py, api.py and models.py.
Per-file reviews already ran. Their findings are below. Do NOT repeat them.
Report ONLY problems BETWEEN files: a caller that passes the wrong type or value to another module, names or types that do not match across files, errors that break across a call.

Per-file findings:
$PREVIOUS" \
  --allowedTools "Read,Grep,Glob" \
  --output-format json --json-schema "$SCHEMA" > "$OUT/integration.json"

echo "Done. Results in p2-ci-review/out/"
