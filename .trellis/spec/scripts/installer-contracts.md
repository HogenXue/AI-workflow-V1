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
| **Cursor** | `~/.cursor/skills` | `~/.cursor/config` | Project `.cursor/rules/*.mdc` **generated from** `trellis/AGENTS.global.md` at install | `~/.cursor/mcp.json` `mcpServers` | `<project>/.cursor/hooks.json` + `hooks/` |

**Hard rules**:

- Skills and config share a paired root (`~/.agents` vs `~/.cursor`) because skills resolve `../../config`.
- Codex MCP = TOML fragments under `trellis/codex/mcp/`; Cursor MCP = JSON under `trellis/cursor/mcp/`.
- Cursor “AGENTS-like” content → `.cursor/rules/*.mdc` only, **dynamically** from `trellis/AGENTS.global.md` (static `trellis/cursor/rules/*.mdc` is not the install source body).
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

## Convention: Timestamped backup names

**What**: Every existing file, directory, or symlink that an installer will overwrite, delete, or migrate is copied first to `<backup-dir>/<name>.<UTC timestamp>.bak`. A same-second collision appends a numeric suffix before `.bak`; an existing backup is never overwritten. Default roots use `.ai-workflow-backups` under the paired host home; legacy backup directories are preserved but receive no new backups.

**Integrity contract**: The helper reserves each backup name with a lock directory, copies into a staging payload, and publishes with a same-filesystem rename. Parallel invocations cannot select the same backup path, and a partial copy is never exposed as a completed `.bak`.

**Failure contract**: Backup or lock-reservation failure aborts the component before the original target is mutated. Rollback restores from the exact backup path returned by the shared helper without consuming the `.bak` artifact. A host merge that updates MCP and then fails during project-scoped work must restore the original MCP target (including a dangling symlink) or remove a newly created target.

**Transaction boundary**: Each component is transactional within its own write scope, but a multi-component install is not a global transaction. A later component failure does not undo earlier successful components. Multiple installers must not run concurrently; backup-name publication is concurrency-safe, but target mutation is intentionally not serialized. Historical backups are retained until the user removes them.

**Host scope**:

- Codex project replacement backs up and replaces only `.codex/hooks.json` and `.codex/hooks/`; unrelated `.codex` content is preserved.
- Cursor project replacement backs up rules and hooks, removes the old managed hooks directory, then installs the template so deleted hooks cannot remain active; unrelated `.cursor` content is preserved.
- Installer targets must not overlap packaged source directories, and Cursor's MCP target must not be the packaged MCP fragment.
- A backup directory must not be the target itself or a descendant of the target being backed up.

**Tests required**: Assert the filename pattern, preserved backup contents, sequential and parallel collision uniqueness, backup-failure behavior, dangling-symlink handling, MCP rollback after project failure, source/target separation, nested-backup rejection, and unrelated host-directory sentinels.

---

## Convention: MCP URL transport safety

**What**: URL-bearing MCP entries are validated in `scripts/lib/merge_host_mcp.py`
before the merged host configuration is written. HTTPS is allowed for remote
servers. Plain HTTP is allowed only for `localhost`, `127.0.0.1`, and `::1`.

**Why**: Project memory and other MCP payloads must not be sent to a remote
server over a plaintext default. Keeping the policy in the shared merge helper
prevents Codex TOML and Cursor JSON behavior from drifting.

**Failure contract**: An invalid, unsupported, or remote HTTP URL prints a
stable `ERROR:` diagnostic and returns non-zero before target mutation. The
calling shell installer retains its existing timestamped backup and rollback
contract. Entries preserved by an explicit `keep` policy are not rewritten.

**Tests required**: Cover Codex and Cursor rejection without target mutation,
the three loopback hosts, the packaged Recallium HTTPS default, and valid remote
HTTPS input.

---

## Convention: Shared configuration and workflow checks

**What**: `config/effective_config.py` owns defaults/project merge and schema
validation. `config/workflow_check.py` provides platform-neutral `readiness`,
`quality`, and `completion` commands. The config installer copies these runtime
files together with `defaults.yaml`.

**State boundary**: Workflow checks never replace or mutate the Trellis task
state machine. Readiness and completion are read-only. Quality writes
`verification.json` only when a task is explicitly supplied; CI omits the task
and writes no evidence.

**Freshness contract**: Task quality evidence records Git HEAD as audit metadata
and uses a deterministic worktree content fingerprint for freshness. Committing
the same verified content does not invalidate evidence merely because HEAD
changes. Completion still fails after tracked or unignored untracked content
changes. Run targeted checks during implementation and one final quality check
per task, not once per commit; rerun only after covered content changes.

**Tests required**: Validate configuration consumer coverage, missing runtime
dependencies, placeholder planning artifacts, complex-task requirements,
curated context, unchecked acceptance criteria, fresh/stale evidence, evidence
reuse across a commit boundary, unchanged task status, and a temporary
planning-to-completion lifecycle.

---

## Convention: Skill renames and optional resources

**Manifest contract**: `manifest.yaml` lists only currently distributed Skill names. A renamed or removed
workflow Skill is not silently deleted during an ordinary install. Add it to the installer's legacy list;
`--prune-legacy` must preview the removal and, on execution, create a unique timestamped `.bak` before
removing the old directory or symlink. The `grill-me` → `grill-with-docs` migration follows this path.

**Structure contract**: Every Skill requires `SKILL.md` and `agents/openai.yaml`. `references/`,
`templates/`, `examples/`, `scripts/`, and `assets/` are optional and should exist only when the Skill uses
them. The validator checks relative links and placeholder examples when those resources exist; it must not
require empty directories or placeholder files.

**Tests required**: Assert manifest installation includes every current Skill, legacy rename pruning is
explicit and backed up, a minimal Skill without optional resource directories validates, and existing
optional resources still receive link/placeholder checks.
