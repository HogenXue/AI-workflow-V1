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
  local name="$3"
  if [[ ! -e "$source" && ! -L "$source" ]]; then
    return 0
  fi
  local stamp
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  local dest="$backup_dir/$stamp"
  mkdir -p "$dest"
  cp -pR "$source" "$dest/$name"
  printf 'BACKUP: %s\n' "$dest/$name"
}
