#!/usr/bin/env bash

set -euo pipefail

usage() {
  printf '%s\n' 'Usage: install-agents.sh [--dry-run|--apply] [--agents-home PATH] [--backup-dir PATH]' >&2
}

fail_usage() {
  printf 'ERROR: %s\n' "$1" >&2
  usage
  exit 2
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root_dir="$(cd "$script_dir/.." && pwd)"
source_file="$root_dir/trellis/AGENTS.global.md"
agents_home="${CODEX_HOME:-$HOME/.codex}"
backup_dir=""
mode="dry-run"
mode_selected=""

while (($#)); do
  case "$1" in
    --dry-run|--apply)
      requested_mode="${1#--}"
      if [[ -n "$mode_selected" && "$mode_selected" != "$requested_mode" ]]; then
        fail_usage '--dry-run and --apply cannot be used together'
      fi
      mode="$requested_mode"
      mode_selected="$requested_mode"
      ;;
    --agents-home|--codex-home|--backup-dir)
      option="$1"
      if (($# < 2)) || [[ -z "$2" || "$2" == --* ]]; then
        fail_usage "$option requires a path"
      fi
      if [[ "$option" == '--agents-home' || "$option" == '--codex-home' ]]; then
        agents_home="$2"
      else
        backup_dir="$2"
      fi
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

if [[ ! -f "$source_file" ]]; then
  printf 'ERROR: template not found: %s\n' "$source_file" >&2
  exit 1
fi

target_file="$agents_home/AGENTS.md"
if [[ -z "$backup_dir" ]]; then
  backup_dir="$agents_home/.trellis-template-backups"
fi

if [[ "$mode" == 'dry-run' ]]; then
  printf 'DRY-RUN: would copy %s -> %s\n' "$source_file" "$target_file"
  if [[ -e "$target_file" || -L "$target_file" ]]; then
    printf 'DRY-RUN: would back up %s under %s\n' "$target_file" "$backup_dir"
  fi
  printf '%s\n' 'DRY-RUN: config.toml is never modified'
  exit 0
fi

mkdir -p "$agents_home" || { printf 'ERROR: could not create agents home: %s\n' "$agents_home" >&2; exit 1; }

if [[ -e "$target_file" || -L "$target_file" ]]; then
  timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
  backup_root="$backup_dir/$timestamp"
  if [[ -e "$backup_root" || -L "$backup_root" ]]; then
    printf 'ERROR: backup destination already exists: %s\n' "$backup_root" >&2
    exit 1
  fi
  mkdir -p "$backup_root" || { printf 'ERROR: could not create backup directory: %s\n' "$backup_root" >&2; exit 1; }
  cp -p "$target_file" "$backup_root/AGENTS.md" || { printf 'ERROR: could not back up existing AGENTS.md\n' >&2; exit 1; }
  printf 'BACKUP: %s\n' "$backup_root/AGENTS.md"
fi

cp "$source_file" "$target_file" || { printf 'ERROR: could not install AGENTS template\n' >&2; exit 1; }
printf 'INSTALLED: %s\n' "$target_file"
printf '%s\n' 'UNCHANGED: config.toml'
