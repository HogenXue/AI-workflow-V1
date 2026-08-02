#!/usr/bin/env bash

set -euo pipefail

usage() {
  printf '%s\n' 'Usage: install-claude-merge.sh [--dry-run|--apply] [--mcp-keep|--mcp-overwrite] [--mem0-url URL] [--mcp-file PATH] [--replace] [--backup-dir PATH] [--interactive]' >&2
  printf '%s\n' '       --project-root and --skip-project are accepted for wizard compatibility but ignored; Claude merge is user-level MCP only.' >&2
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

mcp_file="${CLAUDE_MCP_FILE:-$HOME/.claude.json}"
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

# Surface flags kept for wizard parity; Claude has no project-scoped install steps.
if [[ -n "$project_root" ]]; then
  printf '%s\n' 'SKIP: Claude merge has no project-scoped steps (project .claude/ is Trellis-managed)'
fi
if ((skip_project)); then
  printf '%s\n' 'SKIP: --skip-project ignored (Claude merge is user-level MCP only)'
fi
# --replace has no project targets; accepted for surface parity with other merge components.
: "${replace}"

if [[ -z "$backup_dir" ]]; then
  # Prefer paired host backup root under ~/.claude even when MCP file is ~/.claude.json.
  backup_dir="$HOME/.claude/.ai-workflow-backups"
fi

templates="$root_dir/trellis/claude"
fragment_file="$templates/mcp/servers.json"
if [[ -e "$mcp_file" && "$mcp_file" -ef "$fragment_file" ]]; then
  printf 'ERROR: Claude MCP target must not be the package MCP fragment: %s\n' "$mcp_file" >&2
  exit 1
fi
mkdir -p "$(dirname "$mcp_file")"
mkdir -p "$(dirname "$backup_dir")"

mcp_original_existed=0
mcp_backup_path=""
mcp_mutated=0
if [[ -e "$mcp_file" || -L "$mcp_file" ]]; then
  mcp_original_existed=1
fi
if ((mcp_original_existed && dry_run == 0)); then
  install_lib_backup_file "$mcp_file" "$backup_dir" "claude.json" || exit 1
  mcp_backup_path="$INSTALL_BACKUP_PATH"
elif ((mcp_original_existed)); then
  printf 'DRY-RUN: backup would use %s/claude.json.<UTC timestamp>.bak\n' "$backup_dir"
fi

rollback_mcp() {
  if ((mcp_mutated == 0)); then
    return 0
  fi
  if ! install_lib_rollback_target "$mcp_original_existed" "$mcp_backup_path" "$mcp_file"; then
    printf 'ERROR: could not roll back Claude MCP configuration\n' >&2
    return 1
  fi
  mcp_mutated=0
}

mcp_args=(
  python3 "$script_dir/lib/merge_host_mcp.py"
  --host claude
  --target "$mcp_file"
  --fragments "$fragment_file"
  --policy "$mcp_policy"
)
[[ -n "$mem0_url" ]] && mcp_args+=(--mem0-url "$mem0_url")
if ((interactive)) && [[ -t 0 ]]; then
  mcp_args+=(--interactive)
fi
((dry_run)) && mcp_args+=(--dry-run)

if "${mcp_args[@]}"; then
  if ((dry_run == 0)); then
    mcp_mutated=1
  fi
else
  mcp_status=$?
  exit "$mcp_status"
fi
