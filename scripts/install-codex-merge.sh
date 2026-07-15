#!/usr/bin/env bash

set -euo pipefail

usage() {
  printf '%s\n' 'Usage: install-codex-merge.sh [--dry-run|--apply] [--mcp-keep|--mcp-overwrite] [--mem0-url URL] [--codex-home PATH] [--project-root PATH] [--skip-project] [--replace] [--backup-dir PATH] [--interactive]' >&2
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

codex_home="${CODEX_HOME:-$HOME/.codex}"
project_root=""
skip_project=0
dry_run=0
mcp_policy="ask"
mem0_url=""
replace=0
backup_dir=""
interactive=0

while (($#)); do
  case "$1" in
    --dry-run) dry_run=1 ;;
    --apply) dry_run=0 ;;
    --mcp-keep) mcp_policy="keep" ;;
    --mcp-overwrite) mcp_policy="overwrite" ;;
    --mem0-url)
      (($# >= 2)) || fail_usage '--mem0-url requires a value'
      mem0_url="$2"
      shift
      ;;
    --codex-home)
      (($# >= 2)) || fail_usage '--codex-home requires a path'
      codex_home="$2"
      shift
      ;;
    --project-root)
      (($# >= 2)) || fail_usage '--project-root requires a path'
      project_root="$2"
      shift
      ;;
    --skip-project) skip_project=1 ;;
    --replace) replace=1 ;;
    --interactive) interactive=1 ;;
    --backup-dir)
      (($# >= 2)) || fail_usage '--backup-dir requires a path'
      backup_dir="$2"
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

if [[ -z "$backup_dir" ]]; then
  backup_dir="$codex_home/.ai-workflow-backups"
fi

templates="$root_dir/trellis/codex"
config_toml="$codex_home/config.toml"
mkdir -p "$codex_home"

mcp_original_existed=0
mcp_backup_path=""
mcp_mutated=0
if [[ -e "$config_toml" || -L "$config_toml" ]]; then
  mcp_original_existed=1
fi
if ((mcp_original_existed && dry_run == 0)); then
  install_lib_backup_file "$config_toml" "$backup_dir" "config.toml" || exit 1
  mcp_backup_path="$INSTALL_BACKUP_PATH"
elif ((mcp_original_existed)); then
  printf 'DRY-RUN: backup would use %s/config.toml.<UTC timestamp>.bak\n' "$backup_dir"
fi

rollback_mcp() {
  if ((mcp_mutated == 0)); then
    return 0
  fi
  if ! install_lib_rollback_target "$mcp_original_existed" "$mcp_backup_path" "$config_toml"; then
    printf 'ERROR: could not roll back Codex MCP configuration\n' >&2
    return 1
  fi
  mcp_mutated=0
}

mcp_args=(
  python3 "$script_dir/lib/merge_host_mcp.py"
  --host codex
  --target "$config_toml"
  --fragments "$templates/mcp"
  --policy "$mcp_policy"
)
[[ -n "$mem0_url" ]] && mcp_args+=(--mem0-url "$mem0_url")
((dry_run)) && mcp_args+=(--dry-run)

if "${mcp_args[@]}"; then
  if ((dry_run == 0)); then
    mcp_mutated=1
  fi
else
  mcp_status=$?
  exit "$mcp_status"
fi

INSTALL_PROJECT_ROOT=""
if ! install_lib_resolve_project_root "$project_root" "$skip_project" "$interactive"; then
  rollback_mcp || true
  exit 1
fi

if [[ -z "${INSTALL_PROJECT_ROOT:-}" ]]; then
  exit 0
fi

proj="$INSTALL_PROJECT_ROOT"
dest_hooks_json="$proj/.codex/hooks.json"
dest_hooks_dir="$proj/.codex/hooks"

if [[ -e "$dest_hooks_json" || -L "$dest_hooks_json" || -e "$dest_hooks_dir" || -L "$dest_hooks_dir" ]] && ((replace == 0)); then
  if ((interactive)) && [[ -t 0 ]]; then
    if ! install_lib_prompt_yn "Replace existing .codex hooks in $proj?" n; then
      printf '%s\n' 'SKIP: existing project Codex hooks preserved'
      exit 0
    fi
    replace=1
  else
    printf 'CONFLICT: existing project Codex hooks at %s (use --replace)\n' "$proj/.codex" >&2
    rollback_mcp || true
    exit 1
  fi
fi

if ((dry_run)); then
  if [[ -e "$dest_hooks_json" || -L "$dest_hooks_json" || -e "$dest_hooks_dir" || -L "$dest_hooks_dir" ]]; then
    printf 'DRY-RUN: hook backups would use %s/<name>.<UTC timestamp>.bak\n' "$backup_dir"
  fi
  printf 'DRY-RUN: would install project Codex hooks under %s/.codex\n' "$proj"
  exit 0
fi

hooks_json_backup=""
hooks_dir_backup=""
if ((replace)); then
  if [[ -e "$dest_hooks_json" || -L "$dest_hooks_json" ]]; then
    install_lib_backup_file "$dest_hooks_json" "$backup_dir" "hooks.json" || { rollback_mcp || true; exit 1; }
    hooks_json_backup="$INSTALL_BACKUP_PATH"
  fi
  if [[ -e "$dest_hooks_dir" || -L "$dest_hooks_dir" ]]; then
    install_lib_backup_file "$dest_hooks_dir" "$backup_dir" "hooks" || { rollback_mcp || true; exit 1; }
    hooks_dir_backup="$INSTALL_BACKUP_PATH"
  fi
  if ! rm -rf "$dest_hooks_json" "$dest_hooks_dir"; then
    if [[ -n "$hooks_json_backup" ]]; then
      install_lib_restore_backup "$hooks_json_backup" "$dest_hooks_json" || true
    fi
    if [[ -n "$hooks_dir_backup" ]]; then
      install_lib_restore_backup "$hooks_dir_backup" "$dest_hooks_dir" || true
    fi
    printf 'ERROR: could not replace existing project Codex hooks\n' >&2
    rollback_mcp || true
    exit 1
  fi
fi

if ! mkdir -p "$dest_hooks_dir" \
  || ! cp "$templates/hooks.json" "$dest_hooks_json" \
  || ! cp -R "$templates/hooks/." "$dest_hooks_dir/"; then
  rm -rf "$dest_hooks_json" "$dest_hooks_dir" || true
  if [[ -n "$hooks_json_backup" ]]; then
    install_lib_restore_backup "$hooks_json_backup" "$dest_hooks_json" || true
  fi
  if [[ -n "$hooks_dir_backup" ]]; then
    install_lib_restore_backup "$hooks_dir_backup" "$dest_hooks_dir" || true
  fi
  printf 'ERROR: could not install project Codex hooks\n' >&2
  rollback_mcp || true
  exit 1
fi
chmod +x "$dest_hooks_dir"/*.sh 2>/dev/null || true
printf 'INSTALLED: %s\n' "$dest_hooks_json"
printf 'INSTALLED: %s\n' "$dest_hooks_dir"
