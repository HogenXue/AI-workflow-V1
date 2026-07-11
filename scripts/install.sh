#!/usr/bin/env bash

set -euo pipefail

usage() {
  printf '%s\n' 'Usage: install.sh <skills|agents|config> [component options]' >&2
  printf '%s\n' 'Run "install.sh <component> --help" for component-specific options.' >&2
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if (($# == 0)); then
  usage
  exit 2
fi

component="$1"
shift

case "$component" in
  skills)
    exec bash "$script_dir/install-skills.sh" "$@"
    ;;
  agents)
    exec bash "$script_dir/install-agents.sh" "$@"
    ;;
  config)
    exec bash "$script_dir/install-config.sh" "$@"
    ;;
  --help|-h|help)
    usage
    exit 0
    ;;
  *)
    printf 'ERROR: unknown installer component: %s\n' "$component" >&2
    usage
    exit 2
    ;;
esac
