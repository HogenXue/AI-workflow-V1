#!/usr/bin/env bash

set -euo pipefail

usage() {
  printf '%s\n' 'Usage: install-skills.sh [--dry-run] [--link | --copy] [--replace] [--prune-legacy] [--prune-other-root] [--target PATH] [--backup-dir PATH]' >&2
}

fail_usage() {
  printf 'ERROR: %s\n' "$1" >&2
  usage
  exit 2
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root_dir="$(cd "$script_dir/.." && pwd)"
manifest="$root_dir/manifest.yaml"
target="$HOME/.agents/skills"
backup_dir=""
mode="copy"
mode_selected=""
explicit_dry_run=0
execute_requested=0
replace=0
prune_legacy=0
prune_other_root=0

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
    --prune-legacy)
      prune_legacy=1
      ;;
    --prune-other-root)
      prune_other_root=1
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

normalized_target="${target%/}"
codex_skills="${CODEX_HOME:-"$HOME/.codex"}/skills"
codex_skills="${codex_skills%/}"
shared_skills="$HOME/.agents/skills"
other_codex_root=""

if [[ "$normalized_target" == "$codex_skills" ]]; then
  other_codex_root="$shared_skills"
elif [[ "$normalized_target" == "$shared_skills" ]]; then
  other_codex_root="$codex_skills"
fi

if ((prune_other_root)) && [[ -z "$other_codex_root" ]]; then
  fail_usage '--prune-other-root requires --target ~/.agents/skills or the active CODEX_HOME/skills'
fi

duplicate_skill_names=()
if [[ -n "$other_codex_root" ]]; then
  for skill in "${skills[@]}"; do
    if [[ -e "$other_codex_root/$skill" || -L "$other_codex_root/$skill" ]]; then
      duplicate_skill_names+=("$skill")
    fi
  done
fi

if ((${#duplicate_skill_names[@]})); then
  printf 'WARNING: duplicate Skill names also exist in %s: %s\n' \
    "$other_codex_root" "${duplicate_skill_names[*]}" >&2
  printf '%s\n' 'Codex may discover both roots; keep one canonical copy per Skill name.' >&2
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

legacy_skills=("openspec" "review")
legacy_conflicts=()
for skill in "${legacy_skills[@]}"; do
  if [[ -e "$target/$skill" || -L "$target/$skill" ]]; then
    legacy_conflicts+=("$skill")
  fi
done

if ((${#legacy_conflicts[@]})); then
  printf 'WARNING: legacy workflow Skills are outside the current manifest: %s\n' \
    "${legacy_conflicts[*]}" >&2
  if ((prune_legacy == 0)); then
    printf '%s\n' 'They are preserved. Use --prune-legacy to back them up and remove them from this target.' >&2
  fi
fi

other_root_conflicts=()
if [[ -n "$other_codex_root" ]]; then
  for skill in "${skills[@]}" "${legacy_skills[@]}"; do
    if [[ -e "$other_codex_root/$skill" || -L "$other_codex_root/$skill" ]]; then
      other_root_conflicts+=("$skill")
    fi
  done
fi

if ((dry_run)); then
  if ((${#conflicts[@]})); then
    printf 'CONFLICT: existing skills: %s\n' "${conflicts[*]}" >&2
    printf '%s\n' 'Use --replace to back up and replace them.' >&2
  fi
  for skill in "${skills[@]}"; do
    printf 'DRY-RUN: %s %s -> %s\n' "$mode" "$skill" "$target/$skill"
  done
  if ((prune_legacy && ${#legacy_conflicts[@]})); then
    for skill in "${legacy_conflicts[@]}"; do
      printf 'DRY-RUN: would back up and remove legacy Skill: %s\n' "$skill"
    done
  fi
  if ((prune_other_root && ${#other_root_conflicts[@]})); then
    for skill in "${other_root_conflicts[@]}"; do
      printf 'DRY-RUN: would back up and remove other-root Skill: %s/%s\n' \
        "$other_codex_root" "$skill"
    done
  fi
  exit 0
fi

if ((${#conflicts[@]} > 0 && replace == 0)); then
  printf 'CONFLICT: existing skills: %s\n' "${conflicts[*]}" >&2
  printf '%s\n' 'Use --replace to back up and replace them.' >&2
  exit 1
fi

moved_skills=()
moved_legacy_skills=()
moved_other_root_skills=()
created_skills=()
backup_root=""

rollback() {
  local status="$1"
  local skill

  printf '%s\n' 'ERROR: Skills installation failed; rolling back.' >&2
  if ((${#created_skills[@]})); then
    for skill in "${created_skills[@]}"; do
      rm -rf "$target/$skill" || true
    done
  fi
  if ((${#moved_skills[@]})); then
    for skill in "${moved_skills[@]}"; do
      rm -rf "$target/$skill" || true
      if [[ -e "$backup_root/$skill" || -L "$backup_root/$skill" ]]; then
        if ! mv "$backup_root/$skill" "$target/$skill"; then
          printf 'ERROR: could not restore backup for %s\n' "$skill" >&2
        fi
      fi
    done
  fi
  if ((${#moved_legacy_skills[@]})); then
    for skill in "${moved_legacy_skills[@]}"; do
      if [[ -e "$backup_root/legacy/$skill" || -L "$backup_root/legacy/$skill" ]]; then
        if ! mv "$backup_root/legacy/$skill" "$target/$skill"; then
          printf 'ERROR: could not restore legacy Skill %s\n' "$skill" >&2
        fi
      fi
    done
  fi
  if ((${#moved_other_root_skills[@]})); then
    for skill in "${moved_other_root_skills[@]}"; do
      if [[ -e "$backup_root/other-root/$skill" || -L "$backup_root/other-root/$skill" ]]; then
        if ! mv "$backup_root/other-root/$skill" "$other_codex_root/$skill"; then
          printf 'ERROR: could not restore other-root Skill %s\n' "$skill" >&2
        fi
      fi
    done
  fi
  exit "$status"
}

needs_backup=0
if ((${#conflicts[@]})); then
  needs_backup=1
fi
if ((prune_legacy && ${#legacy_conflicts[@]})); then
  needs_backup=1
fi
if ((prune_other_root && ${#other_root_conflicts[@]})); then
  needs_backup=1
fi

if ((needs_backup)); then
  backup_root="$backup_dir/$(date -u +%Y%m%dT%H%M%SZ)"
  if [[ -e "$backup_root" || -L "$backup_root" ]]; then
    printf 'ERROR: backup destination already exists: %s\n' "$backup_root" >&2
    exit 1
  fi
  mkdir -p "$backup_root" || { printf 'ERROR: could not create backup directory: %s\n' "$backup_root" >&2; exit 1; }
  if ((${#conflicts[@]})); then
    for skill in "${conflicts[@]}"; do
      mv "$target/$skill" "$backup_root/$skill" || rollback 1
      moved_skills+=("$skill")
    done
  fi
  if ((prune_legacy)); then
    mkdir -p "$backup_root/legacy" || rollback 1
    for skill in "${legacy_conflicts[@]}"; do
      mv "$target/$skill" "$backup_root/legacy/$skill" || rollback 1
      moved_legacy_skills+=("$skill")
      printf 'PRUNED: legacy Skill %s\n' "$skill"
    done
  fi
  if ((prune_other_root && ${#other_root_conflicts[@]})); then
    mkdir -p "$backup_root/other-root" || rollback 1
    for skill in "${other_root_conflicts[@]}"; do
      mv "$other_codex_root/$skill" "$backup_root/other-root/$skill" || rollback 1
      moved_other_root_skills+=("$skill")
      printf 'PRUNED: other-root Skill %s/%s\n' "$other_codex_root" "$skill"
    done
  fi
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
