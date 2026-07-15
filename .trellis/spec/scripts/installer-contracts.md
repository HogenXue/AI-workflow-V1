# Installer Contracts

> Executable contracts for interactive multi-agent install and host-specific merge.
> Source of truth verified by `tests/test_install_interactive.py` and related install tests.

---

## Design Decision: Duty mapping, never directory copy

**Context**: Codex and Cursor use similarly named concepts (skills, rules, hooks, MCP) with different roots and formats.

**Decision**: Install by **profile duty mapping**. Never copy a Cursor tree into a Codex tree (or the reverse). Never delete the other host’s directory as part of install.

**Why**: Same names ≠ same runtime contracts. Silent path guesswork installs into the wrong project or breaks Trellis-managed root `AGENTS.md`.

---

## Scenario: Explicit project root

### 1. Scope / Trigger

- Trigger: Any write under a **project** `.codex/` or `.cursor/` (hooks, Cursor rules).
- Infra contract: new/changed flags `--project-root`, `--skip-project`, and shared resolver in `scripts/install-lib.sh`.

### 2. Signatures

```text
install_lib_resolve_project_root <provided_path> <skip_flag:0|1> <interactive:0|1>
  → sets INSTALL_PROJECT_ROOT to absolute path, or "" if skipped
  → exit 1 on invalid path / invalid menu choice

install.sh <codex-merge|cursor-merge> --project-root PATH ...
install.sh <codex-merge|cursor-merge> --skip-project ...
install.sh   # TTY only: menu includes project-root pick (git root = candidate only)
```

### 3. Contracts

| Input | Behavior |
|-------|----------|
| `--project-root PATH` | Use absolute path; must be an existing directory |
| `--skip-project` | Skip project-scoped steps; print `SKIP: ...` |
| TTY interactive, no path | Menu: select git root **as option**, custom path, or skip |
| Non-interactive, no path, no skip | Skip project-scoped steps; print clear `SKIP` + hint to pass `--project-root` |
| Global-only steps (skills, paired config, host MCP, Codex `~/.codex` AGENTS/hooks feature) | Do **not** require a project root |

**Forbidden**: applying `git rev-parse --show-toplevel` (or cwd) without an **explicit** user choice / `--project-root`.

### 4. Validation & Error Matrix

| Condition | Result |
|-----------|--------|
| `--project-root` not a directory | stderr `ERROR: ...`; exit `1` |
| TTY invalid menu choice | stderr `ERROR: invalid project-root choice`; exit `1` |
| Skip / no root | `INSTALL_PROJECT_ROOT=""`; continue global installs |
| Empty custom path on TTY | Skip (not error) |

### 5. Good / Base / Bad Cases

- **Good**: `--project-root /abs/repo` → hooks/rules written only under that repo
- **Base**: non-interactive merge without `--project-root` → MCP/global OK; project steps skipped with message
- **Bad**: silently defaulting to git toplevel when the user did not select it

### 6. Tests Required

- Assert non-interactive without `--project-root` does **not** create project `.codex/` / `.cursor/` hooks/rules
- Assert `--project-root` installs under the given path only
- Assert resolver never treats detected git root as applied unless choice/`--project-root` selects it
- Assertion points: no project files under wrong root; stdout contains `SKIP` / `PROJECT-ROOT` as expected

### 7. Wrong vs Correct

#### Wrong

```bash
# Silent default — forbidden
project_root="$(git rev-parse --show-toplevel)"
install_hooks "$project_root"
```

#### Correct

```bash
install_lib_resolve_project_root "${provided:-}" "${skip:-0}" "${interactive:-0}" || exit 1
if [[ -z "${INSTALL_PROJECT_ROOT:-}" ]]; then
  # skip project-scoped; continue global
  exit 0   # or return, depending on caller
fi
# write only under "$INSTALL_PROJECT_ROOT"
```

---

## Scenario: Codex vs Cursor profile pairing

### 1. Scope / Trigger

- Trigger: Full-profile or component install for one or both agents.
- Cross-host contract: skills root ↔ config root pairing; MCP format; rules vs AGENTS placement.

### 2. Signatures

```text
install.sh                          # TTY: multi-select agents → full or single component
install.sh skills|agents|config|codex-merge|cursor-merge [options]

# Profile entrypoints (interactive full install)
install_profile_codex  <project_root_or_empty> <mem0_url_or_empty>
install_profile_cursor <project_root_or_empty> <mem0_url_or_empty>
```

### 3. Contracts — profile map

| Profile | Skills | Config (skill defaults) | Host / rules | MCP | Project-scoped |
|---------|--------|-------------------------|--------------|-----|----------------|
| **Codex** | `~/.agents/skills` | `~/.agents/config` (parent of skills root) | `~/.codex` (`AGENTS.md` + hooks feature); **not** root repo `AGENTS.md` for Cursor rules | `~/.codex/config.toml` `[mcp_servers.*]` | `<project>/.codex/hooks.json` + `hooks/` |
| **Cursor** | `~/.cursor/skills` | `~/.cursor/config` | Project `.cursor/rules/*.mdc` | `~/.cursor/mcp.json` `mcpServers` | `<project>/.cursor/hooks.json` + `hooks/` |

**Hard rules**:

- Skills and config share a paired root (`~/.agents` vs `~/.cursor`) because skills resolve `../../config`.
- Codex MCP = TOML fragments under `trellis/codex/mcp/`; Cursor MCP = JSON under `trellis/cursor/mcp/`.
- Cursor “AGENTS-like” content → `.cursor/rules/*.mdc` only.
- Installer **never** rewrites Trellis / project root `AGENTS.md`.
- Do not install global `~/.codex/hooks.json`; project hooks only under explicit project root.
- Multi-select runs selected profiles sequentially; never delete the other host’s files.

### 4. Validation & Error Matrix

| Condition | Result |
|-----------|--------|
| Unknown agent / component | Usage + exit `2` |
| MCP key conflict + policy `ask` | `CONFLICT: ...` stderr; exit `2` (need `--mcp-keep` / `--mcp-overwrite`) |
| Existing project hooks/rules without `--replace` (non-interactive) | `CONFLICT: ...`; exit `1` |
| `mem0` fragment without `--mem0-url` | Skip mem0 entry with message (other servers may still merge) |

### 5. Good / Base / Bad Cases

- **Good**: Codex-only full install writes `~/.agents/*` + `~/.codex` MCP; leaves `~/.cursor` untouched
- **Base**: Codex+Cursor multi-select writes both profiles under their own trees
- **Bad**: Copying `.cursor/rules` into Codex sandbox `rules`, or overwriting repo-root `AGENTS.md`

### 6. Tests Required

- Single-profile install: assert opposite host tree unchanged
- Multi-select: assert both profiles receive expected markers
- Cursor merge with existing `AGENTS.md`: assert file content unchanged
- MCP: Codex path contains `[mcp_servers.]`; Cursor path is JSON `mcpServers`
- Assertion points: path presence/absence, `AGENTS.md` hash/content, conflict exit codes

### 7. Wrong vs Correct

#### Wrong

```text
# Directory copy anti-pattern
cp -R ~/.cursor/skills ~/.agents/skills
# Cursor rules dumped into Codex / root AGENTS
cp .cursor/rules/* ~/.codex/rules/
echo "..." >> "$PROJECT/AGENTS.md"   # installer must not do this
```

#### Correct

```text
Codex:  skills→~/.agents/skills  config→~/.agents/config  MCP→config.toml  project→.codex/hooks*
Cursor: skills→~/.cursor/skills  config→~/.cursor/config  MCP→mcp.json     project→.cursor/{rules/*.mdc,hooks*}
```

---

## Scenario: Interactive `install.sh` multi-select

### 1. Scope / Trigger

- Trigger: `bash scripts/install.sh` with **no args**.
- UX contract: TTY wizard vs non-TTY hard fail.

### 2. Signatures

```text
install.sh                 # no args
  TTY:     interactive_main → exit 0 (or 2 on invalid choice)
  non-TTY: usage on stderr → exit 2

Interactive choices:
  agents: 1=Codex | 2=Cursor | 3=Codex+Cursor
  mode:   1=recommended full | 2=single component
  then:   explicit project-root menu (shared resolver)
```

### 3. Contracts

| Mode | Behavior |
|------|----------|
| Full install | Confirmation summary → `install_profile_*` for each selected agent |
| Single component | One of `skills\|agents\|config\|codex-merge\|cursor-merge`; merge components get `--project-root` or `--skip-project` + `--interactive` |
| Component CLI (args present) | Unchanged dispatch; still compatible with existing flags |

### 4. Validation & Error Matrix

| Condition | Result |
|-----------|--------|
| No args + stdin not a TTY | Usage; exit `2` |
| Invalid agent choice | `ERROR: invalid agent choice`; exit `2` |
| Unknown single-component name | `ERROR: unknown component`; exit `2` |
| User declines “Proceed?” | `Aborted.`; exit `0` |

### 5. Good / Base / Bad Cases

- **Good**: TTY choice `3` runs Codex then Cursor profiles once project root is resolved/skipped
- **Base**: piped/non-TTY `install.sh` with no args → exit `2` (CI-safe)
- **Bad**: Treating non-TTY empty args as “default full install” or auto-picking git root

### 6. Tests Required

- `install.sh` with stdin not a TTY and no args → exit code `2` and usage text
- Interactive paths covered via scripted input or component-level flags (`--project-root` / `--skip-project`)
- Assertion points: exit code, stderr usage, no unintended project writes

### 7. Wrong vs Correct

#### Wrong

```bash
# Non-TTY empty args silently installing everything
if (($# == 0)); then install_everything; fi
```

#### Correct

```bash
if (($# == 0)); then
  if [[ ! -t 0 ]]; then usage; exit 2; fi
  interactive_main
  exit 0
fi
```

---

## Common Mistake: Silent git toplevel

**Symptom**: Hooks/rules appear in an unexpected repository (or the wrong monorepo package root).

**Cause**: Using `git rev-parse --show-toplevel` as an implicit default.

**Fix / Prevention**: Always go through `install_lib_resolve_project_root` or require `--project-root` / explicit skip.

---

## Convention: Conflict handling

**What**: TTY prompts for replace/overwrite; non-interactive uses flags (`--mcp-keep` / `--mcp-overwrite`, `--replace`).

**Why**: Host MCP and project hooks must not be silently destroyed.

**Related**: Backup before overwrite via `install_lib_backup_file`; MCP writes are atomic (`merge_host_mcp.py`).
