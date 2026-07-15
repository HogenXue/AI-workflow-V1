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
# shellcheck source=install-lib.sh
source "$script_dir/install-lib.sh"
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

if install_lib_paths_overlap "$source_dir" "$target"; then
  printf 'ERROR: config target overlaps package source: %s\n' "$target" >&2
  exit 1
fi

if ((explicit_dry_run)); then
  dry_run=1
elif ((execute_requested)); then
  dry_run=0
else
  dry_run=1
fi

if [[ -z "$backup_dir" ]]; then
  backup_dir="$(dirname "$target")/.ai-workflow-backups"
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
    printf 'DRY-RUN: backup would use %s/%s.<UTC timestamp>.bak\n' "$backup_dir" "$(basename "$target")"
  fi
  printf 'DRY-RUN: %s config -> %s\n' "$mode" "$target"
  exit 0
fi

if ((conflict && replace == 0)); then
  printf 'CONFLICT: existing config: %s\n' "$target" >&2
  printf '%s\n' 'Use --replace to back up and replace it.' >&2
  exit 1
fi

backup_path=""
if ((conflict)); then
  install_lib_backup_file "$target" "$backup_dir" "$(basename "$target")" || exit 1
  backup_path="$INSTALL_BACKUP_PATH"
  if ! rm -rf "$target"; then
    install_lib_restore_backup "$backup_path" "$target" || true
    printf 'ERROR: could not replace existing config\n' >&2
    exit 1
  fi
fi

if ! mkdir -p "$(dirname "$target")"; then
  if [[ -n "$backup_path" ]]; then install_lib_restore_backup "$backup_path" "$target" || true; fi
  printf 'ERROR: could not create config parent directory\n' >&2
  exit 1
fi

copy_config_tree() {
  local source name

  mkdir -p "$target" || return 1
  for source in "$source_dir"/*; do
    name="${source##*/}"
    case "$name" in
      __pycache__|*.pyc|*.pyo) continue ;;
    esac
    cp -R "$source" "$target/" || return 1
  done
}

if [[ "$mode" == 'link' ]]; then
  if ! ln -s "$source_dir" "$target"; then
    if [[ -n "$backup_path" ]]; then install_lib_restore_backup "$backup_path" "$target" || true; fi
    printf 'ERROR: could not link config\n' >&2
    exit 1
  fi
else
  if ! copy_config_tree; then
    rm -rf "$target" || true
    if [[ -n "$backup_path" ]]; then install_lib_restore_backup "$backup_path" "$target" || true; fi
    printf 'ERROR: could not copy config\n' >&2
    exit 1
  fi
fi

printf 'INSTALLED: config -> %s\n' "$target"
