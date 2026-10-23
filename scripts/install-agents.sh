#!/usr/bin/env bash

set -euo pipefail

usage() {
  printf '%s\n' 'Usage: install-agents.sh [--dry-run|--apply] [--agents-home PATH] [--document-name NAME] [--no-hooks-feature] [--backup-dir PATH]' >&2
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
source_file="$root_dir/agents/AGENTS.global.md"
agents_home="${CODEX_HOME:-$HOME/.codex}"
document_name="AGENTS.md"
no_hooks_feature=0
backup_dir=""
mode="dry-run"
mode_selected=""
agents_backup_path=""

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
    --document-name)
      if (($# < 2)) || [[ -z "$2" || "$2" == --* ]]; then
        fail_usage '--document-name requires a name'
      fi
      document_name="$2"
      shift
      ;;
    --no-hooks-feature) no_hooks_feature=1 ;;
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

# Reject path separators so document stays under agents-home.
if [[ "$document_name" == *"/"* || "$document_name" == *"\\"* ]]; then
  printf 'ERROR: --document-name must be a bare filename, got: %s\n' "$document_name" >&2
  exit 2
fi

target_file="$agents_home/$document_name"
if [[ -z "$backup_dir" ]]; then
  backup_dir="$agents_home/.ai-workflow-backups"
fi

if ((no_hooks_feature == 0)) && [[ "$document_name" == AGENTS.md && -s "$agents_home/AGENTS.override.md" ]]; then
  printf 'NOTE: %s is the effective global instruction file; installed AGENTS.md remains shadowed\n' "$agents_home/AGENTS.override.md"
fi

if [[ "$mode" == 'dry-run' ]]; then
  printf 'DRY-RUN: would copy %s -> %s\n' "$source_file" "$target_file"
  if [[ -e "$target_file" || -L "$target_file" ]]; then
    printf 'DRY-RUN: would back up %s as %s/%s.<UTC timestamp>.bak\n' "$target_file" "$backup_dir" "$document_name"
  fi
  if ((no_hooks_feature == 0)); then
    printf '%s\n' 'DRY-RUN: preserving config.toml and native hook settings'
  else
    printf '%s\n' 'DRY-RUN: skipping config.toml hooks feature (--no-hooks-feature)'
  fi
  exit 0
fi

mkdir -p "$agents_home" || { printf 'ERROR: could not create agents home: %s\n' "$agents_home" >&2; exit 1; }

agents_backup_available=0
if [[ -e "$target_file" || -L "$target_file" ]]; then
  install_lib_backup_file "$target_file" "$backup_dir" "$document_name" || exit 1
  agents_backup_path="$INSTALL_BACKUP_PATH"
  agents_backup_available=1
  if [[ -L "$target_file" ]]; then
    rm -f "$target_file" || { printf 'ERROR: could not replace existing %s\n' "$document_name" >&2; exit 1; }
  fi
fi

if ! cp "$source_file" "$target_file"; then
  if ((agents_backup_available)); then
    install_lib_restore_backup "$agents_backup_path" "$target_file" || true
  else
    rm -f "$target_file" || true
  fi
  printf 'ERROR: could not install agents document template\n' >&2
  exit 1
fi
printf 'INSTALLED: %s\n' "$target_file"
if ((no_hooks_feature == 0)); then
  printf '%s\n' 'UNCHANGED: config.toml and native hook settings preserved; use Codex /hooks to review hook trust'
fi
