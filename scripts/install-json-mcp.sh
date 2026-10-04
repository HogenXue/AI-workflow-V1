#!/usr/bin/env bash
# Shared user-level JSON MCP driver for MiniMax Code and WorkBuddy.
set -euo pipefail

host="${1:-}"
shift || exit 2
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root_dir="$(cd "$script_dir/.." && pwd)"
source "$script_dir/install-lib.sh"

case "$host" in
  minimax) host_home="${MINIMAX_DATA_DIR:-${MAVIS_DATA_DIR:-$HOME/.minimax}}" ;;
  workbuddy) host_home="${CODEBUDDY_CONFIG_DIR:-$HOME/.codebuddy}" ;;
  *) printf 'ERROR: unsupported JSON MCP host: %s\n' "$host" >&2; exit 2 ;;
esac

usage() {
  printf 'Usage: install-%s-merge.sh [--dry-run|--apply] [--%s-home PATH] [--mcp-file PATH] [--mcp-keep|--mcp-overwrite] [--mem0-url URL] [--backup-dir PATH] [--interactive]\n' "$host" "$host" >&2
}
fail_usage() { printf 'ERROR: %s\n' "$1" >&2; usage; exit 2; }

mcp_file=""
backup_dir=""
dry_run=0
mode_selected=""
policy="ask"
mem0_url=""
interactive=0
while (($#)); do
  case "$1" in
    --dry-run|--apply)
      mode="${1#--}"
      [[ -z "$mode_selected" || "$mode_selected" == "$mode" ]] || fail_usage '--dry-run and --apply cannot be used together'
      mode_selected="$mode"
      if [[ "$mode" == dry-run ]]; then dry_run=1; else dry_run=0; fi
      ;;
    --mcp-keep) policy="keep" ;;
    --mcp-overwrite) policy="overwrite" ;;
    --interactive) interactive=1 ;;
    --replace|--skip-project) : ;;
    --minimax-home|--workbuddy-home|--mcp-file|--backup-dir|--mem0-url|--project-root)
      option="$1"
      (($# >= 2)) && [[ -n "$2" && "$2" != --* ]] || fail_usage "$option requires a value"
      case "$option" in
        "--$host-home") host_home="$2" ;;
        --mcp-file) mcp_file="$2" ;;
        --backup-dir) backup_dir="$2" ;;
        --mem0-url) mem0_url="$2" ;;
        --project-root) printf 'SKIP: %s merge has no project-scoped steps\n' "$host" ;;
        *) fail_usage "unrecognized option: $option" ;;
      esac
      shift
      ;;
    --help|-h) usage; exit 0 ;;
    *) fail_usage "unrecognized option: $1" ;;
  esac
  shift
done

if [[ -z "$mcp_file" ]]; then
  if [[ "$host" == minimax ]]; then
    mcp_file="$host_home/mcp.json"
    if [[ ! -e "$mcp_file" && ! -L "$mcp_file" && (-e "$host_home/mcp/mcp.json" || -L "$host_home/mcp/mcp.json") ]]; then
      mcp_file="$host_home/mcp/mcp.json"
    fi
  else
    mcp_file="$host_home/.mcp.json"
    if [[ ! -e "$mcp_file" && ! -L "$mcp_file" ]]; then
      if [[ -e "$host_home/mcp.json" || -L "$host_home/mcp.json" ]]; then
        mcp_file="$host_home/mcp.json"
      elif [[ "$host_home" == "$HOME/.codebuddy" && (-e "$HOME/.codebuddy.json" || -L "$HOME/.codebuddy.json") ]]; then
        mcp_file="$HOME/.codebuddy.json"
      fi
    fi
  fi
fi
fragment_file="$root_dir/trellis/$host/mcp/servers.json"
if [[ -L "$mcp_file" || (-e "$mcp_file" && ! -f "$mcp_file") ]]; then
  printf 'ERROR: MCP target is not a regular file: %s\n' "$mcp_file" >&2
  exit 1
fi
if [[ -e "$mcp_file" && "$mcp_file" -ef "$fragment_file" ]]; then
  printf 'ERROR: MCP target must not be the package MCP fragment: %s\n' "$mcp_file" >&2
  exit 1
fi
[[ -n "$backup_dir" ]] || backup_dir="$host_home/.ai-workflow-backups"
if [[ -f "$mcp_file" ]]; then
  if ((dry_run)); then
    printf 'DRY-RUN: backup would use %s/%s.<UTC timestamp>.bak\n' "$backup_dir" "$(basename "$mcp_file")"
  else
    install_lib_backup_file "$mcp_file" "$backup_dir" "$(basename "$mcp_file")" || exit 1
  fi
fi

merge_args=(--host "$host" --target "$mcp_file" --fragments "$fragment_file" --policy "$policy")
[[ -n "$mem0_url" ]] && merge_args+=(--mem0-url "$mem0_url")
if ((interactive)) && [[ -t 0 ]]; then merge_args+=(--interactive); fi
((dry_run)) && merge_args+=(--dry-run)
python3 "$script_dir/lib/merge_host_mcp.py" "${merge_args[@]}"
