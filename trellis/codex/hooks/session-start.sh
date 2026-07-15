#!/usr/bin/env bash
# Minimal project hook: emit Trellis overview when available.
set -euo pipefail
if [[ -f .trellis/scripts/get_context.py ]]; then
  python3 .trellis/scripts/get_context.py 2>/dev/null || true
else
  printf '%s\n' 'No .trellis/ in this project; skip session context.'
fi
