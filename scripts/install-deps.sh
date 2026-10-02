#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python_cmd=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 && \
    "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    python_cmd="$candidate"
    break
  fi
done
if [[ -z "$python_cmd" ]]; then
  printf '%s\n' 'ERROR: Python 3.10+ is required; install Python before deps --apply.' >&2
  exit 1
fi
exec "$python_cmd" "$script_dir/lib/install_dependencies.py" "$@"
