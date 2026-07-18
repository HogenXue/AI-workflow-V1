#!/usr/bin/env bash

set -euo pipefail

usage() {
  printf '%s\n' 'Usage: install-cursor-merge.sh [--dry-run|--apply] [--mcp-keep|--mcp-overwrite] [--mem0-url URL] [--mcp-file PATH] [--project-root PATH] [--skip-project] [--replace] [--backup-dir PATH] [--interactive]' >&2
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

mcp_file="${CURSOR_MCP_FILE:-$HOME/.cursor/mcp.json}"
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
    --mcp-file)
      (($# >= 2)) || fail_usage '--mcp-file requires a path'
      mcp_file="$2"
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
  backup_dir="$(dirname "$mcp_file")/.ai-workflow-backups"
fi

templates="$root_dir/trellis/cursor"
fragment_file="$templates/mcp/servers.json"
if [[ -e "$mcp_file" && "$mcp_file" -ef "$fragment_file" ]]; then
  printf 'ERROR: Cursor MCP target must not be the package MCP fragment: %s\n' "$mcp_file" >&2
  exit 1
fi
mkdir -p "$(dirname "$mcp_file")"

mcp_original_existed=0
mcp_backup_path=""
mcp_mutated=0
if [[ -e "$mcp_file" || -L "$mcp_file" ]]; then
  mcp_original_existed=1
fi
if ((mcp_original_existed && dry_run == 0)); then
  install_lib_backup_file "$mcp_file" "$backup_dir" "mcp.json" || exit 1
  mcp_backup_path="$INSTALL_BACKUP_PATH"
elif ((mcp_original_existed)); then
  printf 'DRY-RUN: backup would use %s/mcp.json.<UTC timestamp>.bak\n' "$backup_dir"
fi

rollback_mcp() {
  if ((mcp_mutated == 0)); then
    return 0
  fi
  if ! install_lib_rollback_target "$mcp_original_existed" "$mcp_backup_path" "$mcp_file"; then
    printf 'ERROR: could not roll back Cursor MCP configuration\n' >&2
    return 1
  fi
  mcp_mutated=0
}

mcp_args=(
  python3 "$script_dir/lib/merge_host_mcp.py"
  --host cursor
  --target "$mcp_file"
  --fragments "$fragment_file"
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
agents_src="$root_dir/AGENTS.global.md"
if [[ ! -f "$agents_src" || ! -f "$templates/hooks.json" || ! -d "$templates/hooks" ]]; then
  printf 'ERROR: incomplete Cursor rules/hooks templates under %s\n' "$root_dir/trellis" >&2
  rollback_mcp || true
  exit 1
fi
# Never modify Trellis-managed root AGENTS.md
if [[ -f "$proj/AGENTS.md" ]]; then
  printf '%s\n' 'NOTE: leaving project root AGENTS.md untouched (Trellis / project owned)'
fi

rules_dest="$proj/.cursor/rules/ai-workflow-global.mdc"
hooks_json_dest="$proj/.cursor/hooks.json"
hooks_dir_dest="$proj/.cursor/hooks"

conflict=0
[[ -e "$rules_dest" || -L "$rules_dest" || -e "$hooks_json_dest" || -L "$hooks_json_dest" || -e "$hooks_dir_dest" || -L "$hooks_dir_dest" ]] && conflict=1

if ((conflict && replace == 0)); then
  if ((interactive)) && [[ -t 0 ]]; then
    if ! install_lib_prompt_yn "Replace/update existing Cursor project hooks/rules in $proj?" n; then
      printf '%s\n' 'SKIP: existing project Cursor hooks/rules preserved'
      exit 0
    fi
    replace=1
  else
    printf 'CONFLICT: existing Cursor project files under %s/.cursor (use --replace)\n' "$proj" >&2
    rollback_mcp || true
    exit 1
  fi
fi

write_rules_mdc_from_agents_global() {
  local dest="$1"
  {
    cat <<'EOF'
---
description: AI-workflow global guidance (from AGENTS.global.md)
alwaysApply: true
---

EOF
    cat "$agents_src"
    printf '\n'
  } > "$dest"
}

if ((dry_run)); then
  if ((conflict)); then
    printf 'DRY-RUN: hooks/rules backups would use %s/<name>.<UTC timestamp>.bak\n' "$backup_dir"
  fi
  printf 'DRY-RUN: would generate %s from %s and install Cursor hooks under %s/.cursor\n' \
    "$rules_dest" "$agents_src" "$proj"
  exit 0
fi

rules_backup=""
hooks_json_backup=""
hooks_dir_backup=""
if ((replace)); then
  if [[ -e "$rules_dest" || -L "$rules_dest" ]]; then
    install_lib_backup_file "$rules_dest" "$backup_dir" "ai-workflow-global.mdc" || { rollback_mcp || true; exit 1; }
    rules_backup="$INSTALL_BACKUP_PATH"
  fi
  if [[ -e "$hooks_json_dest" || -L "$hooks_json_dest" ]]; then
    install_lib_backup_file "$hooks_json_dest" "$backup_dir" "hooks.json" || { rollback_mcp || true; exit 1; }
    hooks_json_backup="$INSTALL_BACKUP_PATH"
  fi
  if [[ -e "$hooks_dir_dest" || -L "$hooks_dir_dest" ]]; then
    install_lib_backup_file "$hooks_dir_dest" "$backup_dir" "hooks" || { rollback_mcp || true; exit 1; }
    hooks_dir_backup="$INSTALL_BACKUP_PATH"
  fi
  if ! rm -rf "$rules_dest" "$hooks_json_dest" "$hooks_dir_dest"; then
    if [[ -n "$rules_backup" ]]; then
      install_lib_restore_backup "$rules_backup" "$rules_dest" || true
    fi
    if [[ -n "$hooks_json_backup" ]]; then
      install_lib_restore_backup "$hooks_json_backup" "$hooks_json_dest" || true
    fi
    if [[ -n "$hooks_dir_backup" ]]; then
      install_lib_restore_backup "$hooks_dir_backup" "$hooks_dir_dest" || true
    fi
    printf 'ERROR: could not replace existing Cursor project hooks/rules\n' >&2
    rollback_mcp || true
    exit 1
  fi
fi

if ! mkdir -p "$proj/.cursor/rules" "$hooks_dir_dest" \
  || ! write_rules_mdc_from_agents_global "$rules_dest" \
  || ! cp "$templates/hooks.json" "$hooks_json_dest" \
  || ! cp -R "$templates/hooks/." "$hooks_dir_dest/"; then
  rm -rf "$rules_dest" "$hooks_json_dest" "$hooks_dir_dest" || true
  if [[ -n "$rules_backup" ]]; then
    install_lib_restore_backup "$rules_backup" "$rules_dest" || true
  fi
  if [[ -n "$hooks_json_backup" ]]; then
    install_lib_restore_backup "$hooks_json_backup" "$hooks_json_dest" || true
  fi
  if [[ -n "$hooks_dir_backup" ]]; then
    install_lib_restore_backup "$hooks_dir_backup" "$hooks_dir_dest" || true
  fi
  printf 'ERROR: could not install Cursor project hooks/rules\n' >&2
  rollback_mcp || true
  exit 1
fi
printf 'INSTALLED: %s (generated from %s)\n' "$rules_dest" "$agents_src"
printf 'INSTALLED: %s\n' "$hooks_json_dest"
printf 'INSTALLED: %s\n' "$hooks_dir_dest"
