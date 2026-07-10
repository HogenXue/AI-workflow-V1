#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
python3 "$repo_root/scripts/validate-all-skills.py" --skill "$(basename "$(dirname "$(dirname "$0")")")"
