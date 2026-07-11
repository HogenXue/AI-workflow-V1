#!/usr/bin/env bash

set -euo pipefail

usage() {
  printf '%s\n' 'Usage: install-skills.sh [--dry-run] [--link | --copy] [--replace] [--target PATH] [--backup-dir PATH]' >&2
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

if [[ -z "$mode_selected" ]]; then
  manifest_mode="$(awk -F': ' '/^default_install_mode:/ { gsub(/[[:space:]]+$/, "", $2); print $2; exit }' "$manifest")"
  if [[ -n "$manifest_mode" ]]; then
    mode="$manifest_mode"
  fi
fi

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

conflicts=()
for skill in "${skills[@]}"; do
  if [[ ! -d "$root_dir/skills/$skill" ]]; then
    printf 'ERROR: source skill not found: %s\n' "$root_dir/skills/$skill" >&2
    exit 1
  fi
  if [[ -e "$target/$skill" || -L "$target/$skill" ]]; then
    conflicts+=("$skill")
  fi
done

if ((dry_run)); then
  if ((${#conflicts[@]})); then
    printf 'CONFLICT: existing skills: %s\n' "${conflicts[*]}" >&2
    printf '%s\n' 'Use --replace to back up and replace them.' >&2
  fi
  for skill in "${skills[@]}"; do
    printf 'DRY-RUN: %s %s -> %s\n' "$mode" "$skill" "$target/$skill"
  done
  exit 0
fi

if ((${#conflicts[@]} > 0 && replace == 0)); then
  printf 'CONFLICT: existing skills: %s\n' "${conflicts[*]}" >&2
  printf '%s\n' 'Use --replace to back up and replace them.' >&2
  exit 1
fi

moved_skills=()
created_skills=()
backup_root=""

rollback() {
  local status="$1"
  local skill

  printf '%s\n' 'ERROR: Skills installation failed; rolling back.' >&2
  for skill in "${created_skills[@]}"; do
    rm -rf "$target/$skill" || true
  done
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

if ((${#conflicts[@]})); then
  backup_root="$backup_dir/$(date -u +%Y%m%dT%H%M%SZ)"
  if [[ -e "$backup_root" || -L "$backup_root" ]]; then
    printf 'ERROR: backup destination already exists: %s\n' "$backup_root" >&2
    exit 1
  fi
  mkdir -p "$backup_root" || { printf 'ERROR: could not create backup directory: %s\n' "$backup_root" >&2; exit 1; }
  for skill in "${conflicts[@]}"; do
    mv "$target/$skill" "$backup_root/$skill" || rollback 1
    moved_skills+=("$skill")
  done
fi

mkdir -p "$target" || rollback 1
for skill in "${skills[@]}"; do
  destination="$target/$skill"
  source="$root_dir/skills/$skill"
  if [[ "$mode" == 'link' ]]; then
    ln -s "$source" "$destination" || rollback 1
  else
    cp -R "$source" "$destination" || rollback 1
  fi
  created_skills+=("$skill")
  printf 'INSTALLED: %s\n' "$skill"
done

if [[ -n "$backup_root" ]]; then
  printf 'BACKUP: %s\n' "$backup_root"
fi
