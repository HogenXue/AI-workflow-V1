#!/usr/bin/env bash

set -euo pipefail

usage() {
  printf '%s\n' 'Usage: config-check.sh [--codex-home PATH]' >&2
}

fail_usage() {
  printf 'ERROR: %s\n' "$1" >&2
  usage
  exit 2
}

codex_home="${CODEX_HOME:-$HOME/.codex}"

while (($#)); do
  case "$1" in
    --codex-home)
      if (($# < 2)) || [[ -z "$2" || "$2" == --* ]]; then
        fail_usage '--codex-home requires a path'
      fi
      codex_home="$2"
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      fail_usage "unrecognized option: $1"
      ;;
  esac
  shift
done

if command -v trellis >/dev/null 2>&1; then
  printf 'Trellis CLI: %s\n' "$(trellis --version 2>/dev/null || printf 'installed (version unavailable)')"
else
  printf '%s\n' 'Trellis CLI: not installed'
fi
printf 'Node: %s\n' "$(node --version 2>/dev/null || printf 'not found')"
printf 'Python: %s\n' "$(python3 --version 2>/dev/null || printf 'not found')"

for file in AGENTS.md config.toml hooks.json; do
  if [[ -f "$codex_home/$file" ]]; then
    printf 'Codex %s: present\n' "$file"
  else
    printf 'Codex %s: absent\n' "$file"
  fi
done

config_path="$codex_home/config.toml"
if [[ -f "$config_path" ]]; then
  servers=()
  while IFS= read -r server; do
    servers+=("$server")
  done < <(
    awk '
      /^\[mcp_servers\.[A-Za-z0-9_-]+\]$/ {
        section = $0
        sub(/^\[mcp_servers\./, "", section)
        sub(/\]$/, "", section)
        print section
      }
    ' "$config_path"
  )
  if ((${#servers[@]})); then
    printf 'MCP servers: '
    for index in "${!servers[@]}"; do
      if ((index > 0)); then
        printf ', '
      fi
      printf '%s' "${servers[index]}"
    done
    printf '\n'
  else
    printf '%s\n' 'MCP servers: none configured'
  fi
else
  printf '%s\n' 'MCP servers: config missing'
fi
