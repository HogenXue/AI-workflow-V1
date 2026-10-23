#!/usr/bin/env bash
# Use the same native context resolver and exit status as the Windows command.
set -euo pipefail
hook_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$hook_dir/session-start.py"
