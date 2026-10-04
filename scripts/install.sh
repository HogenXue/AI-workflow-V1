#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: install.sh <deps|skills|graphify|agents|config|codex-merge|cursor-merge|claude-merge|minimax-merge|workbuddy-merge> [component options]
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
    deps) bash "$script_dir/install-deps.sh" "$@" ;;
    skills) bash "$script_dir/install-skills.sh" "$@" ;;
    graphify) bash "$script_dir/install-graphify.sh" "$@" ;;
    agents) bash "$script_dir/install-agents.sh" "$@" ;;
    config) bash "$script_dir/install-config.sh" "$@" ;;
    codex-merge) bash "$script_dir/install-codex-merge.sh" "$@" ;;
    cursor-merge) bash "$script_dir/install-cursor-merge.sh" "$@" ;;
    claude-merge) bash "$script_dir/install-claude-merge.sh" "$@" ;;
    minimax-merge) bash "$script_dir/install-minimax-merge.sh" "$@" ;;
    workbuddy-merge) bash "$script_dir/install-workbuddy-merge.sh" "$@" ;;
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

install_full_dependencies() {
  local path_file directory status
  path_file="$(mktemp)"
  if run_component deps --apply --path-file "$path_file"; then
    while IFS= read -r directory; do
      [[ -n "$directory" ]] || continue
      # Also support Windows Python invoked from Git Bash during verification.
      if command -v cygpath >/dev/null 2>&1; then
        directory="$(cygpath -u "$directory")"
      fi
      # Do not let Graphify's private Python shadow the user's interpreter.
      PATH="$PATH:$directory"
    done < "$path_file"
    export PATH
    rm -f "$path_file"
  else
    status=$?
    rm -f "$path_file"
    exit "$status"
  fi
}

# Parse multi-select agent tokens (spaces or commas). Sets each want_* flag.
# Returns 1 on empty or invalid selection.
parse_agent_selection() {
  local raw="${1:-}"
  raw="${raw//,/ }"
  want_codex=0
  want_cursor=0
  want_claude=0
  want_minimax=0
  want_workbuddy=0
  local token found=0
  # shellcheck disable=SC2086
  for token in $raw; do
    case "$token" in
      1) want_codex=1; found=1 ;;
      2) want_cursor=1; found=1 ;;
      3) want_claude=1; found=1 ;;
      4) want_minimax=1; found=1 ;;
      5) want_workbuddy=1; found=1 ;;
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
  if [[ -e "$skills_target" || -L "$skills_target" ]]; then
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
  if [[ -e "$config_target" || -L "$config_target" ]]; then
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
  if [[ -e "$skills_target" || -L "$skills_target" ]]; then
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
  if [[ -e "$config_target" || -L "$config_target" ]]; then
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

install_profile_document_host() {
  local host_label="$1" agents_home="$2" document_name="$3" merge_component="$4"
  local mem0_url="${5:-}"
  local skills_target="$agents_home/skills"
  local config_target="$agents_home/config"

  local skill_args=(--copy --target "$skills_target")
  if [[ -e "$skills_target" || -L "$skills_target" ]]; then
    if prompt_replace_if_needed "skills" "$skills_target"; then
      skill_args+=(--replace)
    else
      printf 'SKIP: %s skills\n' "$host_label"
      skill_args=()
    fi
  fi
  if ((${#skill_args[@]})); then
    run_component skills "${skill_args[@]}"
  fi

  local config_args=(--copy --target "$config_target")
  if [[ -e "$config_target" || -L "$config_target" ]]; then
    if prompt_replace_if_needed "config" "$config_target"; then
      config_args+=(--replace)
    else
      printf 'SKIP: %s config\n' "$host_label"
      config_args=()
    fi
  fi
  if ((${#config_args[@]})); then
    run_component config "${config_args[@]}"
  fi

  run_component agents --apply --agents-home "$agents_home" \
    --document-name "$document_name" --no-hooks-feature

  local merge_args=(--interactive)
  [[ -n "$mem0_url" ]] && merge_args+=(--mem0-url "$mem0_url")
  if [[ -t 0 ]]; then
    if install_lib_prompt_yn "Overwrite existing non-URL $host_label MCP entries that conflict?" n; then
      merge_args+=(--mcp-overwrite)
    else
      merge_args+=(--mcp-keep)
    fi
  else
    merge_args+=(--mcp-keep)
  fi
  run_component "$merge_component" "${merge_args[@]}"
}

install_profile_claude() {
  install_profile_document_host Claude "$HOME/.claude" CLAUDE.md claude-merge "${1:-}"
}

install_profile_minimax() {
  install_profile_document_host 'MiniMax Code' "${MINIMAX_DATA_DIR:-${MAVIS_DATA_DIR:-$HOME/.minimax}}" AGENTS.md minimax-merge "${1:-}"
}

install_profile_workbuddy() {
  install_profile_document_host WorkBuddy "${CODEBUDDY_CONFIG_DIR:-$HOME/.codebuddy}" CODEBUDDY.md workbuddy-merge "${1:-}"
}

interactive_main() {
  printf '%s\n' 'AI-workflow installer'
  printf '%s\n' 'Select target agent(s):'
  printf '%s\n' '  1) Codex'
  printf '%s\n' '  2) Cursor'
  printf '%s\n' '  3) Claude'
  printf '%s\n' '  4) MiniMax Code (mcode)'
  printf '%s\n' '  5) WorkBuddy'
  printf 'Select agents (e.g. 1, 1 3, 1,2,3): '
  local agent_choice
  read -r agent_choice || agent_choice=""
  local want_codex=0 want_cursor=0 want_claude=0 want_minimax=0 want_workbuddy=0
  if ! parse_agent_selection "$agent_choice"; then
    printf 'ERROR: invalid agent choice\n' >&2
    exit 2
  fi

  printf '%s\n' 'Install mode:'
  printf '%s\n' '  1) Recommended full install'
  printf '%s\n' '  2) Single component (advanced)'
  printf 'Choice [1-2]: '
  local mode_choice
  if ! read -r mode_choice; then
    printf 'ERROR: invalid install mode (expected 1 or 2)\n' >&2
    exit 2
  fi
  case "$mode_choice" in
    ''|1) mode_choice=1 ;;
    2) ;;
    *) printf 'ERROR: invalid install mode (expected 1 or 2)\n' >&2; exit 2 ;;
  esac

  local project_root=""
  if ((want_cursor)); then
    INSTALL_PROJECT_ROOT=""
    printf '%s\n' 'Select project root for Cursor hooks/rules (explicit choice required; git root is only a candidate)...'
    install_lib_resolve_project_root "" 0 1 || exit 1
    project_root="${INSTALL_PROJECT_ROOT:-}"
  fi

  local mem0_url=""

  if [[ "$mode_choice" == "2" ]]; then
    printf '%s\n' 'Component: deps | skills | graphify | agents | config | codex-merge | cursor-merge | claude-merge | minimax-merge | workbuddy-merge'
    printf 'Component: '
    local comp
    read -r comp || comp=""
    case "$comp" in
      deps|skills|graphify|agents|config|codex-merge|cursor-merge|claude-merge|minimax-merge|workbuddy-merge)
        local extra=()
        if [[ "$comp" == *-merge && -n "$project_root" ]]; then
          extra+=(--project-root "$project_root" --interactive)
        elif [[ "$comp" == *-merge ]]; then
          extra+=(--skip-project --interactive)
        fi
        [[ -n "$mem0_url" && "$comp" == *-merge ]] && extra+=(--mem0-url "$mem0_url")
        if ((${#extra[@]})); then
          run_component "$comp" "${extra[@]}"
        else
          run_component "$comp"
        fi
        ;;
      *)
        printf 'ERROR: unknown component\n' >&2
        exit 2
        ;;
    esac
    return 0
  fi

  printf '%s\n' '--- Recommended full install plan ---'
  printf '%s\n' '- Dependencies: keep usable GitNexus/Trellis/Graphify CLIs; install missing tools first'
  ((want_codex)) && printf '%s\n' '- Codex: ~/.agents/skills (including Graphify) + ~/.agents/config + ~/.codex AGENTS/user hooks + global MCP'
  ((want_cursor)) && printf '%s\n' '- Cursor: ~/.cursor/skills + ~/.cursor/config + mcp.json + project rules/hooks'
  ((want_claude)) && printf '%s\n' '- Claude: ~/.claude/skills + ~/.claude/config + CLAUDE.md + ~/.claude.json MCP (no Graphify, no project .claude/)'
  ((want_minimax)) && printf '%s\n' "- MiniMax Code: ${MINIMAX_DATA_DIR:-${MAVIS_DATA_DIR:-$HOME/.minimax}}/{skills,config,AGENTS.md} + native MCP"
  ((want_workbuddy)) && printf '%s\n' "- WorkBuddy: ${CODEBUDDY_CONFIG_DIR:-$HOME/.codebuddy}/{skills,config,CODEBUDDY.md} + native MCP"
  if [[ -n "$project_root" ]]; then
    printf '%s\n' "- Project root: $project_root"
  else
    printf '%s\n' '- Project-scoped steps: skipped'
  fi
  if ! install_lib_prompt_yn "Proceed?" y; then
    printf '%s\n' 'Aborted.'
    exit 0
  fi

  install_full_dependencies

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
  if ((want_minimax)); then
    printf '%s\n' '=== Installing MiniMax Code profile ==='
    install_profile_minimax "$mem0_url"
  fi
  if ((want_workbuddy)); then
    printf '%s\n' '=== Installing WorkBuddy profile ==='
    install_profile_workbuddy "$mem0_url"
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
  deps|skills|graphify|agents|config|codex-merge|cursor-merge|claude-merge|minimax-merge|workbuddy-merge)
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
