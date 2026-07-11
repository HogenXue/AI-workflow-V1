#!/usr/bin/env bash

set -euo pipefail

usage() {
  printf '%s\n' 'Usage: install.sh [--dry-run] [--link | --copy] [--replace] [--target PATH] [--backup-dir PATH]' >&2
}

fail_usage() {
  printf 'ERROR: %s\n' "$1" >&2
  usage
  exit 2
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root_dir="$(cd "$script_dir/.." && pwd)"
manifest="$root_dir/manifest.yaml"
target="${CODEX_HOME:-"$HOME/.codex"}/skills"
backup_dir=""
mode="link"
mode_selected=""
explicit_dry_run=0
execute_requested=0
replace=0
config_source="$root_dir/config"
config_dest=""

set_config_dest() {
  local parent
  parent="$(dirname "$target")"
  if [[ -d "$parent" ]]; then
    config_dest="$(cd "$parent" && pwd)/config"
  else
    config_dest="$parent/config"
  fi
}

set_config_dest

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
      execute_requested=1
      ;;
    --target|--backup-dir)
      option="$1"
      if (($# < 2)) || [[ -z "$2" || "$2" == --* ]]; then
        fail_usage "$option requires a path"
      fi
      if [[ "$option" == '--target' ]]; then
        target="$2"
        set_config_dest
      else
        backup_dir="$2"
      fi
      shift
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
  backup_dir="$target/.codex-ultimate-v3-backups"
fi

if [[ ! -f "$manifest" ]]; then
  printf 'ERROR: manifest not found: %s\n' "$manifest" >&2
  exit 1
fi

if [[ ! -d "$config_source" ]]; then
  printf 'ERROR: config directory not found: %s\n' "$config_source" >&2
  exit 1
fi

skills=()
while IFS= read -r skill; do
  skills+=("$skill")
done < <(
  awk '
    /^skills:[[:space:]]*$/ { in_skills = 1; next }
    in_skills && /^  - [A-Za-z0-9_-]+[[:space:]]*$/ {
      name = $0
      sub(/^  - /, "", name)
      sub(/[[:space:]]+$/, "", name)
      print name
      next
    }
    in_skills { exit }
  ' "$manifest"
)

if ((${#skills[@]} == 0)); then
  printf 'ERROR: manifest must list at least one skill\n' >&2
  exit 1
fi

for skill in "${skills[@]}"; do
  if [[ ! -d "$root_dir/skills/$skill" ]]; then
    printf 'ERROR: source skill not found: %s\n' "$root_dir/skills/$skill" >&2
    exit 1
  fi
done

conflicts=()
for skill in "${skills[@]}"; do
  destination="$target/$skill"
  if [[ -e "$destination" || -L "$destination" ]]; then
    conflicts+=("$skill")
  fi
done

config_conflict=0
if [[ -e "$config_dest" || -L "$config_dest" ]]; then
  config_conflict=1
fi

if ((dry_run)); then
  if ((${#conflicts[@]} || config_conflict)); then
    if ((${#conflicts[@]})); then
      printf 'CONFLICT: existing skills: %s\n' "${conflicts[*]}" >&2
    fi
    if ((config_conflict)); then
      printf 'CONFLICT: existing config: %s\n' "$config_dest" >&2
    fi
    printf '%s\n' 'Use --replace to back up and replace them.' >&2
  fi
  printf 'DRY-RUN: %s config -> %s\n' "$mode" "$config_dest"
  for skill in "${skills[@]}"; do
    printf 'DRY-RUN: %s %s -> %s\n' "$mode" "$skill" "$target/$skill"
  done
  exit 0
fi

if (( (${#conflicts[@]} > 0 || config_conflict) && replace == 0 )); then
  if ((${#conflicts[@]})); then
    printf 'CONFLICT: existing skills: %s\n' "${conflicts[*]}" >&2
  fi
  if ((config_conflict)); then
    printf 'CONFLICT: existing config: %s\n' "$config_dest" >&2
  fi
  printf '%s\n' 'Use --replace to back up and replace them.' >&2
  exit 1
fi

moved_skills=()
created_skills=()
config_moved=0
config_created=0
backup_root=""

rollback() {
  local status="$1"
  local skill

  printf '%s\n' 'ERROR: installation failed; rolling back.' >&2
  if ((config_created)); then
    rm -rf "$config_dest" || true
  fi
  for skill in "${created_skills[@]}"; do
    rm -rf "$target/$skill" || true
  done
  if ((config_moved)); then
    rm -rf "$config_dest" || true
    if [[ -e "$backup_root/config" || -L "$backup_root/config" ]]; then
      if ! mv "$backup_root/config" "$config_dest"; then
        printf 'ERROR: could not restore config backup\n' >&2
      fi
    fi
  fi
  for skill in "${moved_skills[@]}"; do
    rm -rf "$target/$skill" || true
    if [[ -e "$backup_root/$skill" || -L "$backup_root/$skill" ]]; then
      if ! mv "$backup_root/$skill" "$target/$skill"; then
        printf 'ERROR: could not restore backup for %s\n' "$skill" >&2
      fi
    fi
  done
  exit "$status"
}

if ((${#conflicts[@]} || config_conflict)); then
  backup_root="$backup_dir/$(date -u +%Y%m%dT%H%M%SZ)"
  if [[ -e "$backup_root" || -L "$backup_root" ]]; then
    printf 'ERROR: backup destination already exists: %s\n' "$backup_root" >&2
    exit 1
  fi
  if ! mkdir -p "$backup_root"; then
    printf 'ERROR: could not create backup directory: %s\n' "$backup_root" >&2
    exit 1
  fi
  if ((config_conflict)); then
    if ! mv "$config_dest" "$backup_root/config"; then
      rollback 1
    fi
    config_moved=1
  fi
  for skill in "${conflicts[@]}"; do
    if ! mv "$target/$skill" "$backup_root/$skill"; then
      rollback 1
    fi
    moved_skills+=("$skill")
  done
fi

if ! mkdir -p "$target"; then
  rollback 1
fi

if ! mkdir -p "$(dirname "$config_dest")"; then
  rollback 1
fi

if [[ "$mode" == 'link' ]]; then
  if ! ln -s "$config_source" "$config_dest"; then
    rm -rf "$config_dest" || true
    rollback 1
  fi
elif ! cp -R "$config_source" "$config_dest"; then
  rm -rf "$config_dest" || true
  rollback 1
fi
config_created=1
printf 'INSTALLED: config -> %s\n' "$config_dest"

for skill in "${skills[@]}"; do
  destination="$target/$skill"
  source="$root_dir/skills/$skill"
  if [[ "$mode" == 'link' ]]; then
    if ! ln -s "$source" "$destination"; then
      rm -rf "$destination" || true
      rollback 1
    fi
  elif ! cp -R "$source" "$destination"; then
    rm -rf "$destination" || true
    rollback 1
  fi
  created_skills+=("$skill")
  printf 'INSTALLED: %s\n' "$skill"
done

if [[ -n "$backup_root" ]]; then
  printf 'BACKUP: %s\n' "$backup_root"
fi
