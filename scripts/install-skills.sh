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
# shellcheck source=install-lib.sh
source "$script_dir/install-lib.sh"
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

if install_lib_paths_overlap "$root_dir/skills" "$target"; then
  printf 'ERROR: skills target overlaps package source: %s\n' "$target" >&2
  exit 1
fi

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
  backup_dir="$(dirname "$target")/.ai-workflow-backups"
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
  if ((${#conflicts[@]} || (prune_legacy && ${#legacy_conflicts[@]}) || (prune_other_root && ${#other_root_conflicts[@]}))); then
    printf 'DRY-RUN: backups would use %s/<Skill name>.<UTC timestamp>.bak\n' "$backup_dir"
  fi
  exit 0
fi

if ((${#conflicts[@]} > 0 && replace == 0)); then
  printf 'CONFLICT: existing skills: %s\n' "${conflicts[*]}" >&2
  printf '%s\n' 'Use --replace to back up and replace them.' >&2
  exit 1
fi

backed_up_skills=()
skill_backup_paths=()
backed_up_legacy_skills=()
legacy_backup_paths=()
backed_up_other_root_skills=()
other_root_backup_paths=()
created_skills=()

rollback() {
  local status="$1"
  local skill backup index

  printf '%s\n' 'ERROR: Skills installation failed; rolling back.' >&2
  if ((${#created_skills[@]})); then
    for skill in "${created_skills[@]}"; do
      rm -rf "$target/$skill" || true
    done
  fi
  if ((${#backed_up_skills[@]})); then
    for index in "${!backed_up_skills[@]}"; do
      skill="${backed_up_skills[$index]}"
      backup="${skill_backup_paths[$index]}"
      if ! install_lib_restore_backup "$backup" "$target/$skill"; then
        printf 'ERROR: could not restore backup for %s\n' "$skill" >&2
      fi
    done
  fi
  if ((${#backed_up_legacy_skills[@]})); then
    for index in "${!backed_up_legacy_skills[@]}"; do
      skill="${backed_up_legacy_skills[$index]}"
      backup="${legacy_backup_paths[$index]}"
      if ! install_lib_restore_backup "$backup" "$target/$skill"; then
        printf 'ERROR: could not restore legacy Skill %s\n' "$skill" >&2
      fi
    done
  fi
  if ((${#backed_up_other_root_skills[@]})); then
    for index in "${!backed_up_other_root_skills[@]}"; do
      skill="${backed_up_other_root_skills[$index]}"
      backup="${other_root_backup_paths[$index]}"
      if ! install_lib_restore_backup "$backup" "$other_codex_root/$skill"; then
        printf 'ERROR: could not restore other-root Skill %s\n' "$skill" >&2
      fi
    done
  fi
  exit "$status"
}

if ((${#conflicts[@]})); then
  for skill in "${conflicts[@]}"; do
    install_lib_backup_file "$target/$skill" "$backup_dir" "$skill" || rollback 1
    backed_up_skills+=("$skill")
    skill_backup_paths+=("$INSTALL_BACKUP_PATH")
    rm -rf "$target/$skill" || rollback 1
  done
fi
if ((prune_legacy)); then
  for skill in "${legacy_conflicts[@]}"; do
    install_lib_backup_file "$target/$skill" "$backup_dir" "$skill" || rollback 1
    backed_up_legacy_skills+=("$skill")
    legacy_backup_paths+=("$INSTALL_BACKUP_PATH")
    rm -rf "$target/$skill" || rollback 1
    printf 'PRUNED: legacy Skill %s\n' "$skill"
  done
fi
if ((prune_other_root && ${#other_root_conflicts[@]})); then
  for skill in "${other_root_conflicts[@]}"; do
    install_lib_backup_file "$other_codex_root/$skill" "$backup_dir" "$skill" || rollback 1
    backed_up_other_root_skills+=("$skill")
    other_root_backup_paths+=("$INSTALL_BACKUP_PATH")
    rm -rf "$other_codex_root/$skill" || rollback 1
    printf 'PRUNED: other-root Skill %s/%s\n' "$other_codex_root" "$skill"
  done
fi

mkdir -p "$target" || rollback 1
for skill in "${skills[@]}"; do
  destination="$target/$skill"
  source="$root_dir/skills/$skill"
  created_skills+=("$skill")
  if [[ "$mode" == 'link' ]]; then
    ln -s "$source" "$destination" || rollback 1
  else
    cp -R "$source" "$destination" || rollback 1
  fi
  printf 'INSTALLED: %s\n' "$skill"
done
