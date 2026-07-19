#!/usr/bin/env bash

set -euo pipefail

usage() {
  printf '%s\n' 'Usage: install-graphify.sh [--dry-run|--apply] [--replace] [--backup-dir PATH]' >&2
}

fail_usage() {
  printf 'ERROR: %s\n' "$1" >&2
  usage
  exit 2
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=install-lib.sh
source "$script_dir/install-lib.sh"

target="$HOME/.agents/skills/graphify"
backup_dir="$HOME/.agents/.ai-workflow-backups"
mode="dry-run"
replace=0

while (($#)); do
  case "$1" in
    --dry-run) mode="dry-run" ;;
    --apply) mode="apply" ;;
    --replace) replace=1 ;;
    --backup-dir)
      (($# >= 2)) || fail_usage '--backup-dir requires a path'
      backup_dir="$2"
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *) fail_usage "unrecognized option: $1" ;;
  esac
  shift
done

if [[ "$mode" == "dry-run" ]]; then
  printf 'DRY-RUN: Graphify global Skill -> %s (graphify install --platform agents)\n' "$target"
  if [[ -e "$target" || -L "$target" ]]; then
    printf 'CONFLICT: existing Graphify Skill at %s\n' "$target" >&2
    printf '%s\n' 'Use --replace to back up and replace it.' >&2
  fi
  exit 0
fi

if ! command -v graphify >/dev/null 2>&1; then
  printf '%s\n' 'ERROR: Graphify CLI is unavailable; install graphifyy before running this component.' >&2
  exit 1
fi

backup_path=""
if [[ -e "$target" || -L "$target" ]]; then
  if ((replace == 0)); then
    printf 'CONFLICT: existing Graphify Skill at %s\n' "$target" >&2
    printf '%s\n' 'Use --replace to back up and replace it.' >&2
    exit 1
  fi
  install_lib_backup_file "$target" "$backup_dir" "graphify" || exit 1
  backup_path="$INSTALL_BACKUP_PATH"
  rm -rf "$target" || {
    install_lib_restore_backup "$backup_path" "$target" || true
    exit 1
  }
fi

if ! graphify install --platform agents; then
  printf '%s\n' 'ERROR: Graphify global Skill installation failed.' >&2
  if [[ -n "$backup_path" ]]; then
    install_lib_restore_backup "$backup_path" "$target" || true
  fi
  exit 1
fi

if [[ ! -f "$target/SKILL.md" ]]; then
  printf 'ERROR: Graphify CLI completed without creating %s\n' "$target/SKILL.md" >&2
  if [[ -n "$backup_path" ]]; then
    rm -rf "$target" || true
    install_lib_restore_backup "$backup_path" "$target" || true
  fi
  exit 1
fi

printf 'INSTALLED: Graphify global Skill -> %s\n' "$target"
