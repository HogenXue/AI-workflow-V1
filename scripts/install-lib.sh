#!/usr/bin/env bash
# Shared helpers for interactive / merge installers.
# shellcheck shell=bash

install_lib_prompt_yn() {
  # usage: install_lib_prompt_yn "question" default_y_or_n
  local question="$1"
  local default="${2:-n}"
  local reply
  if [[ ! -t 0 ]]; then
    [[ "$default" == [Yy] ]]
    return
  fi
  if [[ "$default" == [Yy] ]]; then
    printf '%s [Y/n]: ' "$question" >&2
  else
    printf '%s [y/N]: ' "$question" >&2
  fi
  read -r reply || reply=""
  if [[ -z "$reply" ]]; then
    reply="$default"
  fi
  [[ "$reply" == [Yy]* ]]
}

install_lib_candidate_git_root() {
  git -C "${1:-$PWD}" rev-parse --show-toplevel 2>/dev/null || true
}

# Sets INSTALL_PROJECT_ROOT to absolute path, or empty if skipped.
# Never silently applies git toplevel — PRD requires an explicit choice.
# Order: --project-root → --skip-project → TTY menu (git root as candidate) → skip.
install_lib_resolve_project_root() {
  local provided="${1:-}"
  local skip_flag="${2:-0}"
  local interactive="${3:-0}"

  INSTALL_PROJECT_ROOT=""

  if ((skip_flag)); then
    printf '%s\n' 'SKIP: skipping project-scoped steps (--skip-project)'
    return 0
  fi

  if [[ -n "$provided" ]]; then
    if [[ ! -d "$provided" ]]; then
      printf 'ERROR: --project-root is not a directory: %s\n' "$provided" >&2
      return 1
    fi
    INSTALL_PROJECT_ROOT="$(cd "$provided" && pwd)"
    return 0
  fi

  local git_root=""
  git_root="$(install_lib_candidate_git_root "$PWD")"

  if ((interactive)) && [[ -t 0 ]]; then
    printf '%s\n' 'Project-scoped hooks/rules require an explicit project root.' >&2
    printf '%s\n' 'Git toplevel is a candidate only — it is never applied automatically.' >&2
    local choice=""
    if [[ -n "$git_root" ]]; then
      printf '%s\n' "  1) $git_root  (detected git root)" >&2
      printf '%s\n' '  2) Enter a custom path' >&2
      printf '%s\n' '  3) Skip project-scoped steps' >&2
      printf 'Choice [1-3]: ' >&2
      read -r choice || choice=""
      case "$choice" in
        1)
          INSTALL_PROJECT_ROOT="$git_root"
          printf 'PROJECT-ROOT: %s (user-selected git root)\n' "$INSTALL_PROJECT_ROOT"
          return 0
          ;;
        2)
          printf 'Project path: ' >&2
          local typed
          read -r typed || typed=""
          if [[ -z "$typed" ]]; then
            printf '%s\n' 'SKIP: skipping project-scoped steps (empty path)'
            return 0
          fi
          if [[ ! -d "$typed" ]]; then
            printf 'ERROR: invalid project path\n' >&2
            return 1
          fi
          INSTALL_PROJECT_ROOT="$(cd "$typed" && pwd)"
          return 0
          ;;
        3|"")
          printf '%s\n' 'SKIP: skipping project-scoped steps (user declined)'
          return 0
          ;;
        *)
          printf 'ERROR: invalid project-root choice\n' >&2
          return 1
          ;;
      esac
    fi

    printf '%s\n' '  1) Enter a custom path' >&2
    printf '%s\n' '  2) Skip project-scoped steps' >&2
    printf 'Choice [1-2]: ' >&2
    read -r choice || choice=""
    case "$choice" in
      1)
        printf 'Project path: ' >&2
        local typed
        read -r typed || typed=""
        if [[ -z "$typed" ]]; then
          printf '%s\n' 'SKIP: skipping project-scoped steps (empty path)'
          return 0
        fi
        if [[ ! -d "$typed" ]]; then
          printf 'ERROR: invalid project path\n' >&2
          return 1
        fi
        INSTALL_PROJECT_ROOT="$(cd "$typed" && pwd)"
        return 0
        ;;
      2|"")
        printf '%s\n' 'SKIP: skipping project-scoped steps (user declined)'
        return 0
        ;;
      *)
        printf 'ERROR: invalid project-root choice\n' >&2
        return 1
        ;;
    esac
  fi

  printf '%s\n' 'SKIP: skipping project-scoped steps (no --project-root; pass --project-root PATH to install hooks/rules)'
  return 0
}

install_lib_backup_file() {
  local source="$1"
  local backup_dir="$2"
  local name="${3:-$(basename "$source")}"
  INSTALL_BACKUP_PATH=""
  if [[ ! -e "$source" && ! -L "$source" ]]; then
    return 0
  fi
  if install_lib_path_is_within "$backup_dir" "$source"; then
    printf 'ERROR: backup directory must not be inside the target being backed up: %s\n' "$backup_dir" >&2
    return 1
  fi
  local stamp
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  if ! mkdir -p "$backup_dir"; then
    printf 'ERROR: could not create backup directory: %s\n' "$backup_dir" >&2
    return 1
  fi

  local candidate="$backup_dir/$name.$stamp.bak"
  local lock=""
  local sequence=1
  while true; do
    lock="$candidate.lock"
    if [[ -e "$candidate" || -L "$candidate" || -e "$lock" || -L "$lock" ]]; then
      candidate="$backup_dir/$name.$stamp-$sequence.bak"
      sequence=$((sequence + 1))
      continue
    fi
    if ! mkdir "$lock" 2>/dev/null; then
      if [[ ! -e "$candidate" && ! -L "$candidate" && ! -e "$lock" && ! -L "$lock" ]]; then
        printf 'ERROR: could not reserve backup path under: %s\n' "$backup_dir" >&2
        return 1
      fi
      candidate="$backup_dir/$name.$stamp-$sequence.bak"
      sequence=$((sequence + 1))
      continue
    fi
    if [[ ! -e "$candidate" && ! -L "$candidate" ]]; then
      break
    fi
    rmdir "$lock" 2>/dev/null || true
    candidate="$backup_dir/$name.$stamp-$sequence.bak"
    sequence=$((sequence + 1))
  done

  local staging="$lock/payload"
  if ! cp -pR "$source" "$staging"; then
    rm -rf "$lock" || true
    printf 'ERROR: could not back up existing target: %s\n' "$source" >&2
    return 1
  fi
  if ! mv "$staging" "$candidate"; then
    rm -rf "$lock" || true
    printf 'ERROR: could not finalize backup for: %s\n' "$source" >&2
    return 1
  fi
  rmdir "$lock" 2>/dev/null || rm -rf "$lock" || true
  INSTALL_BACKUP_PATH="$candidate"
  printf 'BACKUP: %s\n' "$candidate"
}

install_lib_restore_backup() {
  local backup="$1"
  local destination="$2"
  if [[ -z "$backup" || (! -e "$backup" && ! -L "$backup") ]]; then
    printf 'ERROR: backup is unavailable for restore: %s\n' "$backup" >&2
    return 1
  fi
  if [[ -f "$backup" && ! -L "$backup" && -f "$destination" && ! -L "$destination" ]]; then
    if ! cp -p "$backup" "$destination"; then
      printf 'ERROR: could not restore %s from %s\n' "$destination" "$backup" >&2
      return 1
    fi
    return 0
  fi
  if ! rm -rf "$destination"; then
    printf 'ERROR: could not clear failed target before restore: %s\n' "$destination" >&2
    return 1
  fi
  if ! cp -pR "$backup" "$destination"; then
    printf 'ERROR: could not restore %s from %s\n' "$destination" "$backup" >&2
    return 1
  fi
}

install_lib_rollback_target() {
  local original_existed="$1"
  local backup="$2"
  local destination="$3"
  if [[ "$original_existed" == "1" ]]; then
    install_lib_restore_backup "$backup" "$destination"
  else
    if ! rm -rf "$destination"; then
      printf 'ERROR: could not remove newly created target during rollback: %s\n' "$destination" >&2
      return 1
    fi
  fi
}

install_lib_paths_overlap() {
  local source="$1"
  local target="$2"
  local source_real target_real
  source_real="$(install_lib_normalize_path "$source")" || return 1
  target_real="$(install_lib_normalize_path "$target")" || return 1
  if [[ "$source_real" == "/" || "$target_real" == "/" \
    || "$source_real" == "$target_real" \
    || "$source_real" == "$target_real/"* \
    || "$target_real" == "$source_real/"* ]]; then
    return 0
  fi
  return 1
}

install_lib_path_is_within() {
  local candidate="$1"
  local parent="$2"
  local candidate_real parent_real
  candidate_real="$(install_lib_normalize_path "$candidate")" || return 1
  parent_real="$(install_lib_normalize_path "$parent")" || return 1
  [[ "$candidate_real" == "$parent_real" || "$candidate_real" == "$parent_real/"* ]]
}

install_lib_normalize_path() {
  local input_path="$1"
  if [[ "$input_path" != /* ]]; then
    input_path="$PWD/$input_path"
  fi

  local probe="$input_path"
  local parent component normalized
  local -a suffix=()
  while [[ ! -d "$probe" ]]; do
    parent="$(dirname "$probe")"
    if [[ "$parent" == "$probe" ]]; then
      return 1
    fi
    component="$(basename "$probe")"
    if ((${#suffix[@]})); then
      suffix=("$component" "${suffix[@]}")
    else
      suffix=("$component")
    fi
    probe="$parent"
  done

  normalized="$(cd "$probe" && pwd -P)" || return 1
  if ((${#suffix[@]})); then
    for component in "${suffix[@]}"; do
      case "$component" in
        .|'') ;;
        ..) normalized="$(dirname "$normalized")" ;;
        *) normalized="$normalized/$component" ;;
      esac
    done
  fi
  printf '%s\n' "$normalized"
}
