#!/usr/bin/env bash

set -euo pipefail

usage() {
  printf '%s\n' 'Usage: install-config.sh [--dry-run] [--link | --copy] [--replace] [--target PATH] [--backup-dir PATH]' >&2
}

fail_usage() {
  printf 'ERROR: %s\n' "$1" >&2
  usage
  exit 2
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root_dir="$(cd "$script_dir/.." && pwd)"
source_dir="$root_dir/config"
target="$HOME/.agents/config"
backup_dir=""
mode="copy"
mode_selected=""
explicit_dry_run=0
execute_requested=0
replace=0

while (($#)); do
  case "$1" in
    --dry-run)
      explicit_dry_run=1
      ;;
    --link|--copy)
      requested_mode="${1#--}"
      if [[ -n "$mode_selected" && "$mode_selected" != "$requested_mode" ]]; then
        fail_usage '--link and --copy cannot be used together'
      fi
      mode="$requested_mode"
      mode_selected="$requested_mode"
      execute_requested=1
      ;;
    --replace)
      replace=1
      ;;
    --target|--backup-dir)
      option="$1"
      if (($# < 2)) || [[ -z "$2" || "$2" == --* ]]; then
        fail_usage "$option requires a path"
      fi
      if [[ "$option" == '--target' ]]; then
        target="$2"
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

if ((explicit_dry_run)); then
  dry_run=1
elif ((execute_requested)); then
  dry_run=0
else
  dry_run=1
fi

if [[ -z "$backup_dir" ]]; then
  backup_dir="$(dirname "$target")/.codex-ultimate-v3-backups"
fi

if [[ ! -d "$source_dir" ]]; then
  printf 'ERROR: config directory not found: %s\n' "$source_dir" >&2
  exit 1
fi

conflict=0
if [[ -e "$target" || -L "$target" ]]; then
  conflict=1
fi

if ((dry_run)); then
  if ((conflict)); then
    printf 'CONFLICT: existing config: %s\n' "$target" >&2
    printf '%s\n' 'Use --replace to back up and replace it.' >&2
  fi
  printf 'DRY-RUN: %s config -> %s\n' "$mode" "$target"
  exit 0
fi

if ((conflict && replace == 0)); then
  printf 'CONFLICT: existing config: %s\n' "$target" >&2
  printf '%s\n' 'Use --replace to back up and replace it.' >&2
  exit 1
fi

backup_root=""
if ((conflict)); then
  backup_root="$backup_dir/$(date -u +%Y%m%dT%H%M%SZ)"
  if [[ -e "$backup_root" || -L "$backup_root" ]]; then
    printf 'ERROR: backup destination already exists: %s\n' "$backup_root" >&2
    exit 1
  fi
  mkdir -p "$backup_root" || { printf 'ERROR: could not create backup directory: %s\n' "$backup_root" >&2; exit 1; }
  mv "$target" "$backup_root/config" || { printf 'ERROR: could not move existing config to backup\n' >&2; exit 1; }
fi

if ! mkdir -p "$(dirname "$target")"; then
  if [[ -n "$backup_root" ]]; then mv "$backup_root/config" "$target" || true; fi
  printf 'ERROR: could not create config parent directory\n' >&2
  exit 1
fi

if [[ "$mode" == 'link' ]]; then
  if ! ln -s "$source_dir" "$target"; then
    if [[ -n "$backup_root" ]]; then mv "$backup_root/config" "$target" || true; fi
    printf 'ERROR: could not link config\n' >&2
    exit 1
  fi
else
  if ! cp -R "$source_dir" "$target"; then
    rm -rf "$target" || true
    if [[ -n "$backup_root" ]]; then mv "$backup_root/config" "$target" || true; fi
    printf 'ERROR: could not copy config\n' >&2
    exit 1
  fi
fi

printf 'INSTALLED: config -> %s\n' "$target"
if [[ -n "$backup_root" ]]; then
  printf 'BACKUP: %s\n' "$backup_root"
fi
