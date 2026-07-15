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
  backup_dir="$codex_home/.trellis-template-backups"
fi

templates="$root_dir/trellis/codex"
config_toml="$codex_home/config.toml"
mkdir -p "$codex_home"

if [[ -f "$config_toml" ]] && ((dry_run == 0)); then
  install_lib_backup_file "$config_toml" "$backup_dir" "config.toml"
fi

mcp_args=(
  python3 "$script_dir/lib/merge_host_mcp.py"
  --host codex
  --target "$config_toml"
  --fragments "$templates/mcp"
  --policy "$mcp_policy"
)
[[ -n "$mem0_url" ]] && mcp_args+=(--mem0-url "$mem0_url")
((dry_run)) && mcp_args+=(--dry-run)

"${mcp_args[@]}"
mcp_status=$?
if ((mcp_status != 0)); then
  exit "$mcp_status"
fi

INSTALL_PROJECT_ROOT=""
install_lib_resolve_project_root "$project_root" "$skip_project" "$interactive" || exit 1

if [[ -z "${INSTALL_PROJECT_ROOT:-}" ]]; then
  exit 0
fi

proj="$INSTALL_PROJECT_ROOT"
dest_hooks_json="$proj/.codex/hooks.json"
dest_hooks_dir="$proj/.codex/hooks"

if [[ -e "$dest_hooks_json" || -e "$dest_hooks_dir" ]] && ((replace == 0)); then
  if ((interactive)) && [[ -t 0 ]]; then
    if ! install_lib_prompt_yn "Replace existing .codex hooks in $proj?" n; then
      printf '%s\n' 'SKIP: existing project Codex hooks preserved'
      exit 0
    fi
    replace=1
  else
    printf 'CONFLICT: existing project Codex hooks at %s (use --replace)\n' "$proj/.codex" >&2
    exit 1
  fi
fi

if ((dry_run)); then
  printf 'DRY-RUN: would install project Codex hooks under %s/.codex\n' "$proj"
  exit 0
fi

if ((replace)) && [[ -e "$proj/.codex" ]]; then
  install_lib_backup_file "$proj/.codex" "$backup_dir" "project-codex"
  rm -rf "$proj/.codex"
fi

mkdir -p "$dest_hooks_dir"
cp "$templates/hooks.json" "$dest_hooks_json"
cp -R "$templates/hooks/." "$dest_hooks_dir/"
chmod +x "$dest_hooks_dir"/*.sh 2>/dev/null || true
printf 'INSTALLED: %s\n' "$dest_hooks_json"
printf 'INSTALLED: %s\n' "$dest_hooks_dir"
