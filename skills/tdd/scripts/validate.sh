#!/usr/bin/env bash
set -euo pipefail

skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

for path in SKILL.md agents/openai.yaml references/trellis-boundary.md templates/tdd-cycle.md examples/feature-cycle.md; do
  if [[ ! -f "$skill_dir/$path" ]]; then
    printf 'missing required file: %s\n' "$path" >&2
    exit 1
  fi
done

printf 'tdd skill: OK\n'
