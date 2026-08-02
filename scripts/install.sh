#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: install.sh <skills|graphify|agents|config|codex-merge|cursor-merge|claude-merge> [component options]
       install.sh   # interactive (TTY only)

Run "install.sh <component> --help" for component-specific options.
Non-TTY with no args prints usage and exits 2.
EOF
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=install-lib.sh
source "$script_dir/install-lib.sh"

run_component() {
  local component="$1"
  shift
  case "$component" in
    skills) bash "$script_dir/install-skills.sh" "$@" ;;
    graphify) bash "$script_dir/install-graphify.sh" "$@" ;;
    agents) bash "$script_dir/install-agents.sh" "$@" ;;
    config) bash "$script_dir/install-config.sh" "$@" ;;
    codex-merge) bash "$script_dir/install-codex-merge.sh" "$@" ;;
    cursor-merge) bash "$script_dir/install-cursor-merge.sh" "$@" ;;
    claude-merge) bash "$script_dir/install-claude-merge.sh" "$@" ;;
    *)
      printf 'ERROR: unknown installer component: %s\n' "$component" >&2
      usage
      return 2
      ;;
  esac
}

prompt_replace_if_needed() {
  local kind="$1"
  local target="$2"
  if [[ ! -e "$target" && ! -L "$target" ]]; then
    return 0
  fi
  if install_lib_prompt_yn "Existing $kind at $target — backup and replace?" n; then
    return 0
  fi
  return 1
}

# Parse multi-select agent tokens (spaces or commas). Sets want_codex/cursor/claude.
# Returns 1 on empty or invalid selection.
parse_agent_selection() {
  local raw="${1:-}"
  raw="${raw//,/ }"
  want_codex=0
  want_cursor=0
  want_claude=0
  local token found=0
  # shellcheck disable=SC2086
  for token in $raw; do
    case "$token" in
      1) want_codex=1; found=1 ;;
      2) want_cursor=1; found=1 ;;
      3) want_claude=1; found=1 ;;
      *) return 1 ;;
    esac
  done
  ((found)) || return 1
  return 0
}

install_profile_codex() {
  local project_root="${1:-}"
  local mem0_url="${2:-}"
  local skills_target="$HOME/.agents/skills"
  local config_target="$HOME/.agents/config"
  local agents_home="${CODEX_HOME:-$HOME/.codex}"

  local skill_args=(--copy --target "$skills_target")
  if [[ -e "$skills_target" ]]; then
    if prompt_replace_if_needed "skills" "$skills_target"; then
      skill_args+=(--replace)
    else
      printf '%s\n' 'SKIP: Codex skills'
      skill_args=()
    fi
  fi
  if ((${#skill_args[@]})); then
    run_component skills "${skill_args[@]}"
  fi

  local graphify_target="$skills_target/graphify"
  local graphify_args=(--apply)
  if [[ -e "$graphify_target" || -L "$graphify_target" ]]; then
    if prompt_replace_if_needed "Graphify Skill" "$graphify_target"; then
      graphify_args+=(--replace)
    else
      printf '%s\n' 'SKIP: Graphify global Skill'
      graphify_args=()
    fi
  fi
  if ((${#graphify_args[@]})); then
    run_component graphify "${graphify_args[@]}"
  fi

  local config_args=(--copy --target "$config_target")
  if [[ -e "$config_target" ]]; then
    if prompt_replace_if_needed "config" "$config_target"; then
      config_args+=(--replace)
    else
      printf '%s\n' 'SKIP: Codex config'
      config_args=()
    fi
  fi
  if ((${#config_args[@]})); then
    run_component config "${config_args[@]}"
  fi

  run_component agents --apply --agents-home "$agents_home"

  local merge_args=(--interactive)
  [[ -n "$mem0_url" ]] && merge_args+=(--mem0-url "$mem0_url")
  [[ -n "$project_root" ]] && merge_args+=(--project-root "$project_root")
  if [[ -t 0 ]]; then
    if install_lib_prompt_yn "Overwrite existing non-URL Codex MCP entries that conflict?" n; then
      merge_args+=(--mcp-overwrite)
    else
      merge_args+=(--mcp-keep)
    fi
  else
    merge_args+=(--mcp-keep)
  fi
  run_component codex-merge "${merge_args[@]}"
}

install_profile_cursor() {
  local project_root="${1:-}"
  local mem0_url="${2:-}"
  local skills_target="$HOME/.cursor/skills"
  local config_target="$HOME/.cursor/config"

  local skill_args=(--copy --target "$skills_target")
  if [[ -e "$skills_target" ]]; then
    if prompt_replace_if_needed "skills" "$skills_target"; then
      skill_args+=(--replace)
    else
      printf '%s\n' 'SKIP: Cursor skills'
      skill_args=()
    fi
  fi
  if ((${#skill_args[@]})); then
    run_component skills "${skill_args[@]}"
  fi

  local config_args=(--copy --target "$config_target")
  if [[ -e "$config_target" ]]; then
    if prompt_replace_if_needed "config" "$config_target"; then
      config_args+=(--replace)
    else
      printf '%s\n' 'SKIP: Cursor config'
      config_args=()
    fi
  fi
  if ((${#config_args[@]})); then
    run_component config "${config_args[@]}"
  fi

  local merge_args=(--interactive)
  [[ -n "$mem0_url" ]] && merge_args+=(--mem0-url "$mem0_url")
  if [[ -n "$project_root" ]]; then
    merge_args+=(--project-root "$project_root")
  else
    merge_args+=(--skip-project)
  fi
  if [[ -t 0 ]]; then
    if install_lib_prompt_yn "Overwrite existing non-URL Cursor MCP entries that conflict?" n; then
      merge_args+=(--mcp-overwrite)
    else
      merge_args+=(--mcp-keep)
    fi
  else
    merge_args+=(--mcp-keep)
  fi
  run_component cursor-merge "${merge_args[@]}"
}

install_profile_claude() {
  local mem0_url="${1:-}"
  local skills_target="$HOME/.claude/skills"
  local config_target="$HOME/.claude/config"
  local agents_home="$HOME/.claude"

  local skill_args=(--copy --target "$skills_target")
  if [[ -e "$skills_target" ]]; then
    if prompt_replace_if_needed "skills" "$skills_target"; then
      skill_args+=(--replace)
    else
      printf '%s\n' 'SKIP: Claude skills'
      skill_args=()
    fi
  fi
  if ((${#skill_args[@]})); then
    run_component skills "${skill_args[@]}"
  fi

  local config_args=(--copy --target "$config_target")
  if [[ -e "$config_target" ]]; then
    if prompt_replace_if_needed "config" "$config_target"; then
      config_args+=(--replace)
    else
      printf '%s\n' 'SKIP: Claude config'
      config_args=()
    fi
  fi
  if ((${#config_args[@]})); then
    run_component config "${config_args[@]}"
  fi

  run_component agents --apply --agents-home "$agents_home" \
    --document-name CLAUDE.md --no-hooks-feature

  local merge_args=(--interactive)
  [[ -n "$mem0_url" ]] && merge_args+=(--mem0-url "$mem0_url")
  if [[ -t 0 ]]; then
    if install_lib_prompt_yn "Overwrite existing non-URL Claude MCP entries that conflict?" n; then
      merge_args+=(--mcp-overwrite)
    else
      merge_args+=(--mcp-keep)
    fi
  else
    merge_args+=(--mcp-keep)
  fi
  run_component claude-merge "${merge_args[@]}"
}

interactive_main() {
  printf '%s\n' 'AI-workflow installer'
  printf '%s\n' 'Select target agent(s):'
  printf '%s\n' '  1) Codex'
  printf '%s\n' '  2) Cursor'
  printf '%s\n' '  3) Claude'
  printf 'Select agents (e.g. 1, 1 3, 1,2,3): '
  local agent_choice
  read -r agent_choice || agent_choice=""
  local want_codex=0 want_cursor=0 want_claude=0
  if ! parse_agent_selection "$agent_choice"; then
    printf 'ERROR: invalid agent choice\n' >&2
    exit 2
  fi

  printf '%s\n' 'Install mode:'
  printf '%s\n' '  1) Recommended full install'
  printf '%s\n' '  2) Single component (advanced)'
  printf 'Choice [1-2]: '
  local mode_choice
  read -r mode_choice || mode_choice="1"

  local project_root=""
  if ((want_cursor)); then
    INSTALL_PROJECT_ROOT=""
    printf '%s\n' 'Select project root for Cursor hooks/rules (explicit choice required; git root is only a candidate)...'
    install_lib_resolve_project_root "" 0 1 || exit 1
    project_root="${INSTALL_PROJECT_ROOT:-}"
  fi

  local mem0_url=""

  if [[ "$mode_choice" == "2" ]]; then
    printf '%s\n' 'Component: skills | graphify | agents | config | codex-merge | cursor-merge | claude-merge'
    printf 'Component: '
    local comp
    read -r comp || comp=""
    case "$comp" in
      skills|graphify|agents|config|codex-merge|cursor-merge|claude-merge)
        local extra=()
        if [[ "$comp" == *-merge && -n "$project_root" ]]; then
          extra+=(--project-root "$project_root" --interactive)
        elif [[ "$comp" == *-merge ]]; then
          extra+=(--skip-project --interactive)
        fi
        [[ -n "$mem0_url" && "$comp" == *-merge ]] && extra+=(--mem0-url "$mem0_url")
        run_component "$comp" "${extra[@]}"
        ;;
      *)
        printf 'ERROR: unknown component\n' >&2
        exit 2
        ;;
    esac
    return 0
  fi

  printf '%s\n' '--- Recommended full install plan ---'
  ((want_codex)) && printf '%s\n' '- Codex: ~/.agents/skills (including Graphify) + ~/.agents/config + ~/.codex AGENTS/user hooks + global MCP'
  ((want_cursor)) && printf '%s\n' '- Cursor: ~/.cursor/skills + ~/.cursor/config + mcp.json + project rules/hooks'
  ((want_claude)) && printf '%s\n' '- Claude: ~/.claude/skills + ~/.claude/config + CLAUDE.md + ~/.claude.json MCP (no Graphify, no project .claude/)'
  if [[ -n "$project_root" ]]; then
    printf '%s\n' "- Project root: $project_root"
  else
    printf '%s\n' '- Project-scoped steps: skipped'
  fi
  if ! install_lib_prompt_yn "Proceed?" y; then
    printf '%s\n' 'Aborted.'
    exit 0
  fi

  if ((want_codex)); then
    printf '%s\n' '=== Installing Codex profile ==='
    install_profile_codex "$project_root" "$mem0_url"
  fi
  if ((want_cursor)); then
    printf '%s\n' '=== Installing Cursor profile ==='
    install_profile_cursor "$project_root" "$mem0_url"
  fi
  if ((want_claude)); then
    printf '%s\n' '=== Installing Claude profile ==='
    install_profile_claude "$mem0_url"
  fi
  printf '%s\n' 'Done.'
}

if (($# == 0)); then
  if [[ ! -t 0 ]]; then
    usage
    exit 2
  fi
  interactive_main
  exit 0
fi

component="$1"
shift

case "$component" in
  skills|graphify|agents|config|codex-merge|cursor-merge|claude-merge)
    run_component "$component" "$@"
    ;;
  --help|-h|help)
    usage
    exit 0
    ;;
  *)
    printf 'ERROR: unknown installer component: %s\n' "$component" >&2
    usage
    exit 2
    ;;
esac
