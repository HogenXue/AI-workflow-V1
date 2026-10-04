# Installer Contracts

> Executable contracts for interactive multi-agent install and host-specific merge.
> Source of truth verified by `tests/test_install_interactive.py`, `tests/test_install_*_ps.py`,
> and related install tests.

---

## Design Decision: Dual bash / PowerShell implementation

**Context**: macOS/Linux users run bash installers; Windows users need a native peer without
requiring Git Bash.

**Decision**: Maintain **behaviorally equivalent** ports:

| Surface | Entry | Runtime |
|---------|-------|---------|
| Unix | `scripts/install.sh` + `install-*.sh` | Bash |
| Windows | `scripts/install.ps1` + `install-*.ps1`; launcher `scripts/install.cmd` | **PowerShell 7+ only** (`pwsh`) |

- `install.cmd` forwards to `pwsh -File scripts\install.ps1` (not Windows PowerShell 5.1).
- Shared MCP merge logic stays in `scripts/lib/merge_host_mcp.py` for both hosts.
- CLI component names, flags, exit codes, and stable diagnostic prefixes
  (`ERROR:` / `SKIP:` / `BACKUP:` / `INSTALLED:` / `CONFLICT:` / `DRY-RUN:`) must stay aligned.
- **Drift rule**: when an installer contract changes, update bash **and** PowerShell in the same
  change set, or document an explicit exemption in the PR / task notes.
- CI: ubuntu/macos run Skill validation and the unittest suite directly; `windows-latest` runs
  `tests/test_install_*_ps.py` with `pwsh` verified on the runner.

**Symlinks / `--link`**: creating or preserving dangling reparse points on Windows requires
Developer Mode or `SeCreateSymbolicLinkPrivilege`. PS tests that need file symlinks probe privilege
first and **skip with an explicit reason** when unavailable (last resort; CI attempts to enable
Developer Mode). `--link` failure must still rollback and exit non-zero (never silent copy).

---

## Design Decision: Duty mapping, never directory copy

**Context**: Codex, Cursor, and Claude Code use similarly named concepts (skills, rules, hooks, MCP) with different roots and formats.

**Decision**: Install by **profile duty mapping**. Never copy one host’s tree into another host’s tree. Never delete the other host’s directory as part of install.

**Why**: Same names ≠ same runtime contracts. Silent path guesswork installs into the wrong project or breaks Trellis-managed root `AGENTS.md`.

---

## Scenario: Explicit project root

### 1. Scope / Trigger

- Trigger: Any write under a **project** `.codex/` or `.cursor/` (hooks, Cursor rules).
- Infra contract: new/changed flags `--project-root`, `--skip-project`, and shared resolver in `scripts/install-lib.sh` / `scripts/install-lib.ps1`.

### 2. Signatures

```text
install_lib_resolve_project_root <provided_path> <skip_flag:0|1> <interactive:0|1>
  → sets INSTALL_PROJECT_ROOT to absolute path, or "" if skipped
  → exit 1 on invalid path / invalid menu choice

Install-LibResolveProjectRoot -Provided <path> -SkipFlag 0|1 -Interactive 0|1
  → sets $script:InstallProjectRoot (PowerShell peer)

install.sh <codex-merge|cursor-merge|claude-merge> --project-root PATH ...
install.sh <codex-merge|cursor-merge|claude-merge> --skip-project ...
install.sh   # TTY only: menu includes project-root pick (git root = candidate only; Cursor only)

install.ps1 / install.cmd  # same flags and TTY / non-TTY rules
```

### 3. Contracts

| Input | Behavior |
|-------|----------|
| `--project-root PATH` | Use absolute path; must be an existing directory |
| `--skip-project` | Skip project-scoped steps; print `SKIP: ...` |
| TTY interactive, no path | Menu: select git root **as option**, custom path, or skip (**only when Cursor is selected**) |
| Non-interactive, no path, no skip | Skip project-scoped steps; print clear `SKIP` + hint to pass `--project-root` |
| Global-only steps (skills, paired config, host MCP, Codex `~/.codex` AGENTS/hooks feature, Claude `~/.claude/CLAUDE.md`) | Do **not** require a project root |
| `claude-merge` | Accepts `--project-root` / `--skip-project` for wizard compatibility but ignores them (user-level MCP only) |

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
- PowerShell: covered by `tests/test_install_lib_ps.py` and merge/entry `*_ps.py` modules

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

## Scenario: Host profile pairing

### 1. Scope / Trigger

- Trigger: Full-profile or component install for one or more agents.
- Cross-host contract: skills root ↔ config root pairing; MCP format; rules vs AGENTS/CLAUDE placement.

### 2. Signatures

```text
install.sh                          # TTY: multi-select agents → full or single component
install.sh skills|agents|config|codex-merge|cursor-merge|claude-merge|minimax-merge|workbuddy-merge [options]

install.ps1 / install.cmd           # same interactive + component dispatch (pwsh 7+)

# Profile entrypoints (interactive full install)
install_profile_codex  <project_root_or_empty> <mem0_url_or_empty>
install_profile_cursor <project_root_or_empty> <mem0_url_or_empty>
install_profile_claude <mem0_url_or_empty>
```

### 3. Contracts — profile map

| Profile | Skills | Config (skill defaults) | Host / rules | MCP | Project-scoped |
|---------|--------|-------------------------|--------------|-----|----------------|
| **Codex** | `~/.agents/skills` | `~/.agents/config` (parent of skills root) | `~/.codex` (`AGENTS.md` + hooks feature); **not** root repo `AGENTS.md` for Cursor rules | `~/.codex/config.toml` `[mcp_servers.*]` | User-level hooks under `~/.codex` via `codex-merge` (not silent git-root project install) |
| **Cursor** | `~/.cursor/skills` | `~/.cursor/config` | Project `.cursor/rules/*.mdc` **generated from** `agents/AGENTS.global.md` at install | `~/.cursor/mcp.json` `mcpServers` | `<project>/.cursor/hooks.json` + `hooks/` (requires `--project-root`) |
| **Claude** | `~/.claude/skills` | `~/.claude/config` | User `~/.claude/CLAUDE.md` from `agents/AGENTS.global.md` (`agents --document-name CLAUDE.md --no-hooks-feature`) | `~/.claude.json` `mcpServers` | **None** — installer never writes project `.claude/` or `.mcp.json` |
| **MiniMax Code** | `<dataDir>/skills` | `<dataDir>/config` | `<dataDir>/AGENTS.md` with `--no-hooks-feature` | Native JSON `mcpServers`; `type: stdio/http` | None |
| **WorkBuddy** | `<codebuddyHome>/skills` | `<codebuddyHome>/config` | `<codebuddyHome>/CODEBUDDY.md` with `--no-hooks-feature` | Native JSON `mcpServers`; `type: stdio/http` | None |

**Hard rules**:

- Skills and config share a paired root (`~/.agents` / `~/.cursor` / `~/.claude`) because skills resolve `../../config`.
- Codex MCP = TOML fragments under `trellis/codex/mcp/`; Cursor/Claude MCP = JSON under `trellis/cursor/mcp/` and `trellis/claude/mcp/` respectively (duty mapping: no directory-copy between hosts).
- Cursor “AGENTS-like” content → `.cursor/rules/*.mdc` only, **dynamically** from `agents/AGENTS.global.md`.
- Claude global rules → `~/.claude/CLAUDE.md` only; never rewrite project-root `CLAUDE.md` / `AGENTS.md`.
- Installer **never** rewrites Trellis / project root `AGENTS.md`.
- Do not install global `~/.codex/hooks.json` as a mistaken project path; Codex hooks install at user scope under `~/.codex` per `codex-merge`.
- Claude recommended full install does **not** install Graphify (same as Cursor).
- Claude MCP default backup-dir is `~/.claude/.ai-workflow-backups` even when the MCP file is `~/.claude.json`.
- Multi-select runs selected profiles sequentially; never delete the other host’s files.

### MiniMax Code / WorkBuddy native user configuration

- MiniMax data root: `MINIMAX_DATA_DIR`, then `MAVIS_DATA_DIR`, then `~/.minimax`.
  Component override: `--minimax-home PATH`. Use existing `mcp.json`, otherwise
  existing `mcp/mcp.json`; create `mcp.json` only when neither exists.
- WorkBuddy reads CodeBuddy-compatible user configuration. Root:
  `CODEBUDDY_CONFIG_DIR`, otherwise `~/.codebuddy`; component override:
  `--workbuddy-home PATH`. Select first existing `.mcp.json`, then `mcp.json`,
  then `~/.codebuddy.json` for the default root. A custom root stays isolated;
  use `--mcp-file` to deliberately select a different legacy file.
- Current MCP file-priority documentation supersedes the older directory overview
  that lists `mcp.json` as the canonical CodeBuddy filename.
- `minimax-merge` / `workbuddy-merge` are equivalent Bash/PowerShell components
  using shared `install-json-mcp` drivers and host-native fragments.
- Preview creates no files/directories/backups. Reject non-regular targets,
  symlinks and package-fragment targets before any write. Backups are timestamped
  under the resolved host home's `.ai-workflow-backups` by default.
- Malformed JSON or a non-object `mcpServers` is an error; never silently replace
  it with an empty object. Existing unrelated JSON keys and servers are retained.
- Full profiles install the seven Skills and paired defaults, canonical global
  instructions and MCP. Preserve native `config.yaml` / `settings.json`. No
  guessed hooks, Graphify Skill, application install or project initialization.
- Wizard choices: `4=MiniMax Code`, `5=WorkBuddy`; duplicates ignored and profiles
  run sequentially with the existing failure-stop contract.
- Evidence: `tests/test_install_new_hosts.py` (native components and real full
  profiles in temporary homes), `tests/test_install_wizard.py` (routing/failures).

References: https://github.com/MiniMax-AI/minimax-code ;
https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Setting ;
https://www.codebuddy.cn/docs/cli/mcp ; https://www.codebuddy.cn/docs/cli/env-vars .

### 4. Validation & Error Matrix

| Condition | Result |
|-----------|--------|
| Unknown agent / component | Usage + exit `2` |
| MCP key conflict + policy `ask` | `CONFLICT: ...` stderr; exit `2` (need `--mcp-keep` / `--mcp-overwrite`) |
| Existing project hooks/rules without `--replace` (non-interactive) | `CONFLICT: ...`; exit `1` |
| Packaged `mem0` fragment without `--mem0-url` | Use `https://www.59005046.xyz:8102/mcp`; explicit `--mem0-url` overrides Mem0 only |

### 5. Good / Base / Bad Cases

- **Good**: Codex-only full install writes `~/.agents/*` + `~/.codex` MCP; leaves `~/.cursor` / `~/.claude` untouched
- **Good**: Claude-only writes `~/.claude/{skills,config,CLAUDE.md}` + `~/.claude.json`; no project `.claude/` / `.mcp.json`; no Graphify
- **Base**: multi-select writes each selected profile under its own tree
- **Bad**: Copying `.cursor/rules` into Claude/Codex, or overwriting repo-root `AGENTS.md` / `CLAUDE.md`

### 6. Tests Required

- Single-profile install: assert opposite host trees unchanged
- Multi-select: assert selected profiles receive expected markers
- Cursor/Claude merge with existing project `AGENTS.md` / `CLAUDE.md`: assert file content unchanged
- MCP: Codex path contains `[mcp_servers.]`; Cursor/Claude path is JSON `mcpServers` (Claude preserves non-MCP keys in `~/.claude.json`)
- Assertion points: path presence/absence, document hash/content, conflict exit codes

### 7. Wrong vs Correct

#### Wrong

```text
# Directory copy anti-pattern
cp -R ~/.cursor/skills ~/.claude/skills
# Cursor rules dumped into Codex / root AGENTS
cp .cursor/rules/* ~/.codex/rules/
echo "..." >> "$PROJECT/AGENTS.md"   # installer must not do this
```

#### Correct

```text
Codex:  skills→~/.agents/skills  config→~/.agents/config  MCP→config.toml  docs→~/.codex/AGENTS.md
Cursor: skills→~/.cursor/skills  config→~/.cursor/config  MCP→mcp.json     project→.cursor/{rules/*.mdc,hooks*}
Claude: skills→~/.claude/skills  config→~/.claude/config  MCP→~/.claude.json  docs→~/.claude/CLAUDE.md
```

---

## Scenario: Interactive `install.sh` / `install.ps1` multi-select

### 1. Scope / Trigger

- Trigger: `bash scripts/install.sh` or `pwsh -File scripts/install.ps1` with **no args**.
- UX contract: TTY wizard vs non-TTY hard fail.

### 2. Signatures

```text
install.sh / install.ps1 / install.cmd   # no args
  TTY:     interactive_main → exit 0 (or 2 on invalid choice)
  non-TTY: usage on stderr → exit 2

Interactive choices:
  agents: multi-select numbers — 1=Codex | 2=Cursor | 3=Claude | 4=MiniMax Code | 5=WorkBuddy
          (e.g. `1`, `1 3`, `1,2,3`; whitespace or comma separated; duplicates ignored)
  mode:   1=recommended full | 2=single component
  then:   explicit project-root menu only when Cursor is selected
```

### 3. Contracts

| Mode | Behavior |
|------|----------|
| Full install | Confirmation summary → dependency bootstrap → `install_profile_*` for each selected agent |
| Single component | One of `deps\|skills\|graphify\|agents\|config\|codex-merge\|cursor-merge\|claude-merge`; merge components get `--project-root` or `--skip-project` + `--interactive` |
| Component CLI (args present) | Unchanged dispatch; still compatible with existing flags |

### 4. Validation & Error Matrix

| Condition | Result |
|-----------|--------|
| No args + stdin not a TTY | Usage; exit `2` |
| Invalid agent choice | `ERROR: invalid agent choice`; exit `2` |
| Unknown single-component name | `ERROR: unknown component`; exit `2` |
| User declines “Proceed?” | `Aborted.`; exit `0` |

### 5. Good / Base / Bad Cases

- **Good**: TTY choice `1 3` runs Codex then Claude profiles; project-root asked only if Cursor is selected
- **Base**: piped/non-TTY install with no args → exit `2` (CI-safe)
- **Bad**: Treating non-TTY empty args as “default full install” or auto-picking git root
- **Bad**: Old fixed menu `3 = Codex+Cursor` without multi-select / Claude

### 6. Tests Required

- `install.sh` / `install.ps1` with stdin not a TTY and no args → exit code `2` and usage text
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

**Fix / Prevention**: Always go through `install_lib_resolve_project_root` / `Install-LibResolveProjectRoot` or require `--project-root` / explicit skip.

---

## Convention: Conflict handling

**What**: TTY prompts for replace/overwrite; non-interactive uses flags (`--mcp-keep` / `--mcp-overwrite`, `--replace`).

**Why**: Host MCP and project hooks must not be silently destroyed.

**Related**: Backup before overwrite via `install_lib_backup_file` / `Install-LibBackupFile`; MCP writes are atomic (`merge_host_mcp.py`).

## Convention: Wizard input and component failure boundaries

- The mode menu accepts `1`, `2`, or an empty line (default `1`). Invalid input and EOF
  exit `2` before project-root selection or component execution.
- Bash and PowerShell run components in separate processes. PowerShell launches its current
  `pwsh` executable under `$PSHOME` with `-NoProfile -File`, then checks the exit code immediately.
  Avoid .NET 6-only APIs such as `Environment.ProcessPath` or `FileSystemInfo.ResolveLinkTarget`
  while the declared minimum remains PowerShell 7.0. A nonzero component
  status stops all subsequent components/profiles, suppresses `Done.`, and propagates unchanged
  through the entrypoint and CMD launcher. Completed earlier components keep their existing backups;
  the wizard does not promise rollback of an entire multi-component installation.
- Skills/config replacement checks include dangling links, using `-e || -L` in Bash and
  `Test-InstallLibExistsOrLink` in PowerShell. Declining replacement skips that component.
- Windows backup tests compare link targets allowing the equivalent `\\?\` namespace prefix,
  while still requiring the backup to be a symlink pointing to the expected target.

**Verification**: `tests/test_install_wizard.py` executes actual wizard functions with isolated
component fixtures. Windows CI runs it alongside `test_install_*_ps.py`.

## Convention: Canonical agents template directory

`agents/` is the sole package source for `AGENTS.global.md`, `AGENTS.project.md`, and `AGENTS-egm.md`.
The identical old root templates are removed. Do not confuse them with the repository's active
root `AGENTS.md`, which remains project-owned.

Both `install-agents` implementations read `agents/AGENTS.global.md`; both Cursor merge implementations
generate rule bodies from that same file. Configuration consumers and documentation use these paths.
The project and EGM templates remain reference supplements for deliberate merging outside Trellis
managed blocks, and are never implicitly applied by a global install. Do not fall back to root copies.

## Convention: Missing CLI bootstrap

Full-profile installs run `deps --apply` after the existing confirmation, before profile writes.
The dual wrappers delegate to `scripts/lib/install_dependencies.py`; `deps` defaults to preview.
Preview performs no package-manager call, installation, path-report write, or environment creation.

- Detect and verify existing GitNexus/Trellis/Graphify commands before installing anything. Keep
  usable versions and fail explicitly on broken commands; do not silently upgrade or repair them.
- Missing npm tools use the official `gitnexus@latest` and `@mindfoldhq/trellis@latest` packages with
  `npm install --global --engine-strict`. Node/npm are prerequisites; no sudo or automatic OS/runtime
  installation. npm's current engine constraints remain authoritative.
- Missing Graphify uses Python 3.10+ with `venv`/pip and the official `graphifyy` package inside
  `~/.agents/tools/graphify`. Reject an arbitrary existing managed directory; preserve partial
  environments for retry. Never install into or modify system Python with global pip.
- A temporary, newline-delimited path report lets the wizard pass npm/Graphify executable paths
  to later component subprocesses. Only the current process PATH changes. Standalone dependency
  execution prints directories for optional persistent PATH setup; shell profiles stay user-owned.
- Append discovered directories after existing PATH entries so Graphify's private Python cannot
  replace the interpreter used by the user's configuration and subsequent components.
- Graphify's separate skill installer also checks the managed environment when PATH lacks its CLI.
- Propagate dependency command failures; do not report success until each CLI probe passes. Global
  dependency installs are retained on failure, and no project init/setup/index command runs here.

**Verification**: Simulate subprocesses in `tests/test_install_dependencies.py`; execute actual
wizard functions and dual entry previews in `tests/test_install_wizard.py` / `test_install_entry_ps.py`.
Tests never download dependencies. Review source/bootstrap calls separately from real network install
acceptance, which remains unrun unless expressly executed.

## Convention: Physical path and Graphify rollback protection

PowerShell backup reservations use a `FileMode.CreateNew` lock file, not `New-Item` directory
creation: a raced directory creator can return an already-created directory to two contenders.
Copy into a unique staging payload, publish only after the copy completes, and remove the lock
and any uncommitted payload in `finally`. Keep timestamp/sequence backup naming and never overwrite
another process's backup. A controlled concurrent regression checks two distinct source contents
produce two distinct backups. Bash retains its atomic `mkdir` reservation.

PowerShell resolves each existing path component with `LinkType`/`Target` metadata before comparing
source/target overlap or backup containment. This includes parent symlinks, relative link targets,
and Windows junctions; missing suffixes are appended after the physical ancestor is resolved.
Follow links with a bounded depth. Cycles, inaccessible metadata, and unsupported extended device
namespaces are refused before mutation, rather than being treated as disjoint paths. DOS and UNC
extended prefixes are normalized consistently. Bash's native Unix normalizer already uses `pwd -P`;
the PowerShell-only path fix aligns with that contract without changing Bash path handling.

For Graphify, record whether the Skill target existed before install. On CLI failure or missing
`SKILL.md`, restore a pre-existing backup or clear a newly created target, including dangling links.
Use the shared rollback helper in both ports so an unsuccessful fresh install can be retried without
`--replace`. Replacement failure must preserve the original Skill body.

**Regression evidence**: `tests/test_install_review_ps.py` verifies source aliases/junctions,
relative targets, nonexistent suffixes, backup containment, cycles/device paths, positive copies
through unrelated aliases, and both Graphify failure modes with retry/original restoration.

## Scenario: Per-server URL conflict prompts

### 1. Scope / Trigger

- Trigger: the no-argument TTY wizard merges managed MCP entries into an existing Codex or Cursor host configuration.
- Safety goal: an existing URL is user-owned and must not be replaced by a package default or newly entered Mem0 URL without per-server confirmation.

### 2. Signatures

```text
install.sh / install.ps1           # TTY wizard
  -> install-<host>-merge.sh|.ps1 --interactive
  -> merge_host_mcp.py --interactive --host <codex|cursor|claude|minimax|workbuddy> ...

merge_host_mcp.py --interactive
  # Internal flag. Bash and PowerShell entrypoints pass it only when stdin is a TTY.
```

### 3. Contracts

- Show each existing managed URL and default to keeping it.
- Replace only after explicit confirmation. Both Mem0 and Recallium packaged URL
  entries default to `https://www.59005046.xyz:8102/mcp`. Show that replacement URL;
  an explicit `--mem0-url` overrides Mem0 only. Custom placeholder-only fragments
  still prompt for a URL when none is supplied.
- Missing packaged Mem0 entries use the default without requesting another URL.
- Resolve all five host profiles independently when multiple profiles are selected.
- Existing command/args entries continue to use the host's ordinary `--mcp-keep` / `--mcp-overwrite` policy.
- Component and non-TTY calls never read stdin unless their shell entrypoint has confirmed an interactive TTY.

### 4. Validation & Error Matrix

| Condition | Result |
|-----------|--------|
| Existing URL + default/No | Print `KEEP`; preserve the complete existing entry |
| Existing packaged URL + Yes | Replace with the packaged URL after transport validation |
| Existing Mem0 URL + Yes | Use the displayed default/explicit override after validation |
| Missing packaged Mem0 | Add the default, or explicit `--mem0-url` override |
| Non-TTY component invocation | Do not prompt; use existing policy flags |
| Remote plaintext HTTP replacement | Print `ERROR:` and leave the target unmodified |

### 5. Good / Base / Bad Cases

- **Good**: keep an existing Recallium URL and replace only Mem0 in the same run.
- **Base**: press Enter for every existing URL; all existing URL entries remain unchanged.
- **Bad**: pass a single global overwrite answer through to every URL-bearing MCP without showing the current value.

### 6. Tests Required

- Codex TOML: independent keep/replace decisions; assert old Recallium remains and Mem0 changes.
- Cursor JSON / Claude JSON: inverse or independent decisions; assert packaged Recallium replaces old value and Mem0 remains when kept.
- Missing Mem0: assert the default is added without an extra URL prompt; test
  explicit overrides and both template defaults across all supported hosts.
- Claude: assert non-`mcpServers` keys in `~/.claude.json` are preserved.
- Regression suite: component CLI, non-TTY no-args, URL transport validation, backup, and rollback behavior remain green.
- TTY smoke test: verify the shell entrypoint propagates interactivity and the resulting host config matches the selected decisions.
- PowerShell: `install-*-merge.ps1` must forward `--interactive` to `merge_host_mcp.py` under TTY (wiring asserted in `tests/test_install_merge_ps.py`).

### 7. Wrong vs Correct

#### Wrong

```text
Overwrite existing MCP entries that conflict? Yes
-> silently replace recallium, mem0, and every other URL entry
```

#### Correct

```text
Existing Codex recallium URL: https://old.example/recallium
Replace ... with https://packaged.example/mcp? [y/N]: n
KEEP: mcp_servers.recallium

Existing Codex mem0 URL: https://old.example/mem0
Replace ... with https://www.59005046.xyz:8102/mcp? [y/N]: y
OVERWRITE: mcp_servers.mem0
```

## Convention: Timestamped backup names

**What**: Every existing file, directory, or symlink that an installer will overwrite, delete, or migrate is copied first to `<backup-dir>/<name>.<UTC timestamp>.bak`. A same-second collision appends a numeric suffix before `.bak`; an existing backup is never overwritten. Default roots use `.ai-workflow-backups` under the paired host home; legacy backup directories are preserved but receive no new backups.

**Integrity contract**: The helper reserves each backup name with a lock directory, copies into a staging payload, and publishes with a same-filesystem rename. Parallel invocations cannot select the same backup path, and a partial copy is never exposed as a completed `.bak`.

**Failure contract**: Backup or lock-reservation failure aborts the component before the original target is mutated. Rollback restores from the exact backup path returned by the shared helper without consuming the `.bak` artifact. A host merge that updates MCP and then fails during project-scoped work must restore the original MCP target (including a dangling symlink) or remove a newly created target.

**Transaction boundary**: Each component is transactional within its own write scope, but a multi-component install is not a global transaction. A later component failure does not undo earlier successful components. Multiple installers must not run concurrently; backup-name publication is concurrency-safe, but target mutation is intentionally not serialized. Historical backups are retained until the user removes them.

**Host scope**:

- Codex project replacement backs up and replaces only `.codex/hooks.json` and `.codex/hooks/`; unrelated `.codex` content is preserved.
- Cursor project replacement backs up rules and hooks, removes the old managed hooks directory, then installs the template so deleted hooks cannot remain active; unrelated `.cursor` content is preserved.
- Claude merge backs up and updates only the MCP target file (default `~/.claude.json`); non-`mcpServers` keys are preserved; default backup-dir is `~/.claude/.ai-workflow-backups`.
- Installer targets must not overlap packaged source directories, and Cursor/Claude MCP targets must not be the packaged MCP fragment.
- A backup directory must not be the target itself or a descendant of the target being backed up.

**Tests required**: Assert the filename pattern, preserved backup contents, sequential and parallel collision uniqueness, backup-failure behavior, dangling-symlink handling, MCP rollback after project failure, source/target separation, nested-backup rejection, and unrelated host-directory sentinels.

**Windows note**: Dangling-symlink backup parity depends on symlink create privilege. When privilege is missing, PS tests skip with an explicit reason rather than asserting a false pass.

---

## Convention: MCP URL transport safety

**What**: URL-bearing MCP entries are validated in `scripts/lib/merge_host_mcp.py`
before the merged host configuration is written. HTTPS is allowed for remote
servers. Plain HTTP is allowed only for `localhost`, `127.0.0.1`, and `::1`.

**Why**: Project memory and other MCP payloads must not be sent to a remote
server over a plaintext default. Keeping the policy in the shared merge helper
prevents Codex TOML and Cursor/Claude JSON behavior from drifting.

**Failure contract**: An invalid, unsupported, or remote HTTP URL prints a
stable `ERROR:` diagnostic and returns non-zero before target mutation. The
calling shell installer retains its existing timestamped backup and rollback
contract. Entries preserved by an explicit `keep` policy are not rewritten.

**Tests required**: Cover Codex and Cursor rejection without target mutation,
the three loopback hosts, the packaged Recallium HTTPS default, and valid remote
HTTPS input. PowerShell peers assert the same reject-before-mutate behavior in
`tests/test_install_merge_ps.py`.

---

## Convention: Shared configuration and native task checks

**What**: `config/effective_config.py` owns defaults/project merge and schema
validation. The config installer copies this runtime file with `defaults.yaml`.
Trellis projects use their local `task.py` for task state and context validation,
then run project-specific checks and record their actual results in the task.

**CI contract**: Ubuntu and macOS run `scripts/validate-all-skills.py` and
`python -m unittest discover -s tests` directly. Windows keeps the dedicated
PowerShell installer suite.

**Tests required**: Validate configuration consumer coverage, config component
installation without the removed helper, native task context validation, and
the direct CI command references.

---

## Convention: Skill renames and optional resources

**Manifest contract**: `manifest.yaml` lists only currently distributed Skill names. A renamed or removed
workflow Skill is not silently deleted during an ordinary install. Add it to the installer's legacy list;
`--prune-legacy` must preview the removal and, on execution, create a unique timestamped `.bak` before
removing the old directory or symlink. The `grill-with-docs` → `grill-me` migration follows this path;
`grilling`, `domain-modeling`, `release`, and `karpathy-guidelines-zh` are also legacy entries, not current
manifest Skills. The current package contains five Trellis-adapted AI Hero capabilities plus Memory and
GitNexus; Graphify remains a separately installed analysis skill. General constraints remain in AGENTS,
and release operations follow the existing project workflow without a second lifecycle skill.

**Structure contract**: Every Skill requires `SKILL.md` and `agents/openai.yaml`. `references/`,
`templates/`, `examples/`, `scripts/`, and `assets/` are optional and should exist only when the Skill uses
them. The validator checks relative links and placeholder examples when those resources exist; it must not
require empty directories or placeholder files.

**Tests required**: Assert manifest installation includes every current Skill, legacy rename pruning is
explicit and backed up, a minimal Skill without optional resource directories validates, and existing
optional resources still receive link/placeholder checks.
