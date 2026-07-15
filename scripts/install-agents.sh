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
# shellcheck source=install-lib.sh
source "$script_dir/install-lib.sh"
source_file="$root_dir/trellis/AGENTS.global.md"
agents_home="${CODEX_HOME:-$HOME/.codex}"
backup_dir=""
mode="dry-run"
mode_selected=""
agents_backup_path=""

validate_config_file() {
  local config_file="$agents_home/config.toml"

  if [[ -L "$config_file" || (-e "$config_file" && ! -f "$config_file") ]]; then
    printf 'ERROR: config.toml is not a regular file: %s\n' "$config_file" >&2
    return 1
  fi
}

enable_hooks_feature() {
  local config_file="$agents_home/config.toml"
  local config_tmp
  local hook_setting='hooks = true   # Codex 0.129+。旧版用 `codex_hooks = true`。'

  validate_config_file || return 1

  config_tmp="$(mktemp "$agents_home/.config.toml.trellis.XXXXXX")" || {
    printf 'ERROR: could not create a temporary config file\n' >&2
    return 1
  }

  if [[ -f "$config_file" ]]; then
    awk -v hook_setting="$hook_setting" '
      function is_features_header(line, value) {
        value = line
        sub(/^[[:space:]]*/, "", value)
        return value ~ /^\[features\][[:space:]]*(#.*)?$/
      }
      function is_table_header(line, value) {
        value = line
        sub(/^[[:space:]]*/, "", value)
        return value ~ /^\[[^]]+\][[:space:]]*(#.*)?$/
      }
      BEGIN {
        in_features = 0
        features_found = 0
        hooks_found = 0
      }
      {
        if (is_table_header($0)) {
          if (in_features && !hooks_found) {
            print hook_setting
            hooks_found = 1
          }
          in_features = is_features_header($0)
          if (in_features) {
            features_found = 1
          }
          print
          next
        }
        if (in_features && $0 ~ /^[[:space:]]*hooks[[:space:]]*=/) {
          print hook_setting
          hooks_found = 1
          next
        }
        print
      }
      END {
        if (in_features && !hooks_found) {
          print hook_setting
        }
        if (!features_found) {
          if (NR > 0) {
            print ""
          }
          print "[features]"
          print hook_setting
        }
      }
    ' "$config_file" > "$config_tmp" || {
      rm -f "$config_tmp"
      printf 'ERROR: could not update config.toml\n' >&2
      return 1
    }

    if cmp -s "$config_file" "$config_tmp"; then
      rm -f "$config_tmp"
      printf '%s\n' 'UNCHANGED: config.toml already enables hooks'
      return
    fi

    if ! install_lib_backup_file "$config_file" "$backup_dir" 'config.toml'; then
      rm -f "$config_tmp"
      return 1
    fi
  else
    printf '[features]\n%s\n' "$hook_setting" > "$config_tmp"
  fi

  mv "$config_tmp" "$config_file" || {
    rm -f "$config_tmp"
    printf 'ERROR: could not install config.toml update\n' >&2
    return 1
  }
  printf 'UPDATED: config.toml hooks feature enabled\n'
}

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
  backup_dir="$agents_home/.ai-workflow-backups"
fi

if [[ "$mode" == 'dry-run' ]]; then
  printf 'DRY-RUN: would copy %s -> %s\n' "$source_file" "$target_file"
  if [[ -e "$target_file" || -L "$target_file" ]]; then
    printf 'DRY-RUN: would back up %s as %s/AGENTS.md.<UTC timestamp>.bak\n' "$target_file" "$backup_dir"
  fi
  printf '%s\n' 'DRY-RUN: would ensure [features].hooks = true in config.toml'
  exit 0
fi

mkdir -p "$agents_home" || { printf 'ERROR: could not create agents home: %s\n' "$agents_home" >&2; exit 1; }

validate_config_file || exit 1

agents_backup_available=0
if [[ -e "$target_file" || -L "$target_file" ]]; then
  install_lib_backup_file "$target_file" "$backup_dir" 'AGENTS.md' || exit 1
  agents_backup_path="$INSTALL_BACKUP_PATH"
  agents_backup_available=1
  if [[ -L "$target_file" ]]; then
    rm -f "$target_file" || { printf 'ERROR: could not replace existing AGENTS.md\n' >&2; exit 1; }
  fi
fi

if ! cp "$source_file" "$target_file"; then
  if ((agents_backup_available)); then
    install_lib_restore_backup "$agents_backup_path" "$target_file" || true
  else
    rm -f "$target_file" || true
  fi
  printf 'ERROR: could not install AGENTS template\n' >&2
  exit 1
fi
printf 'INSTALLED: %s\n' "$target_file"
if ! enable_hooks_feature; then
  printf '%s\n' 'ERROR: config.toml update failed; restoring AGENTS.md.' >&2
  if ((agents_backup_available)); then
    install_lib_restore_backup "$agents_backup_path" "$target_file" || {
      printf 'ERROR: could not restore AGENTS.md from backup\n' >&2
      exit 1
    }
  else
    rm -f "$target_file" || {
      printf 'ERROR: could not remove newly installed AGENTS.md\n' >&2
      exit 1
    }
  fi
  exit 1
fi
