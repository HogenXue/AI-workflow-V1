# Local Skill cleanup — 2026-10-10

## Decisions and actual actions

The user authorized auditing/deleting redundant or obsolete local Skills. Deleted
entries were moved to durable recovery storage outside every Skill discovery root.
No runtime file was irreversibly erased.

| Removed active entry | Reason / retained capability |
| --- | --- |
| `~/.codex/skills/anysearch` | Same-source alias; shared `.agents` alias and CC Switch source retained |
| `~/.codex/skills/figma-implement-design` | Alias to retained `.agents` tree |
| `~/.codex/skills/playwright` | Alias to retained `.agents` tree |
| `~/.codex/skills/open-spec` | Old no-frontmatter workflow forcing OpenSpec; adapted `openspec` retained |
| `~/.codex/skills/debugging` | Generic predecessor; native `diagnosing-bugs` retained |
| `~/.agents/skills/write-a-prd` | Unadapted duplicate interview/PRD with automatic GitHub issue publication |
| `~/.agents/skills/karpathy-guidelines-zh` | Redundant all-task policy routing; global principles retained |
| `~/.agents/skills/superpowers` | Removed the discovery symlink for 14 overlapping workflow Skills; underlying package retained |

Graphify's two variants were reviewed rather than merged by name. The existing
personally constrained Codex variant and all its resources were preserved exactly
under `~/.agents/skills/graphify`; the broader variant and original Codex location
are recoverable backups. One direct Graphify identity now remains.

Three `.codex-ultimate-v3-backups` containers (20 nested historical Skill copies)
were moved from `.agents/skills`, `.codex/skills` and `.cursor/skills` into the
recovery area. This includes the obsolete July Grill Me interviewer that wrote
task documents. The four active Grill Me copies match the current source and
remain explicit/stateless; they are retained under the conservative interpretation
of the user's request to remove expired copies. No full retirement was selected.

Distinct `openspec`, release, search/discovery, Figma, browser, iOS/WeChat and
host-specific capabilities were retained. System/plugin-managed assets were not
deleted. No manifest or repository Skill source was changed.

## Permission handling

The first batch hit a root-owned `write-a-prd` directory; all completed moves were
rolled back. `sudo -n true` confirmed administrator credentials were unavailable.
No credentials were requested and no original ownership/permissions were changed.

The user-owned shared root was then rebuilt from a fingerprint-verified keep set,
with the entire original root archived. This removed the root-owned entry from
discovery without editing it or escalating privileges. Original directory metadata
was retained; symlink cleanup moved links only, not their targets.

## Actual verification

- All 12 original removable/replaced entries match their recovery fingerprints;
  the selected Graphify tree matches its original chosen content and backup.
- All 37 protected-path checks passed, including native MCP/config/hooks, system
  assets, independent host Skill roots, CC Switch/Superpowers source packages and
  the existing repository source work.
- No duplicate direct Skill names remain across the two Codex user roots; 28
  valid direct identities remain. Four current Grill Me copies match the source;
  no obsolete Grill Me copy remains in the audited discovery roots.
- `task.py validate` and `git diff --check` passed. Native `trellis-check` was
  applied manually to the operation's scope, backup/preservation and chosen-source
  checks. No full repository or runtime test suite was needed.
- Metadata refresh/application discovery after cleanup: **not_run**. Codex detects
  local Skill changes; reopen the session/app if old entries remain visible.

Receipt: `cleanup-receipt.json`. Decision/restore map: `cleanup-plan.json`.
Recovery root:
`/Users/hogenxue/.local/state/codextamplate/skill-cleanups/2026-10-10-wp2vo_sw`.

## Restore boundary

Each removed entry's original and backup paths are listed in the receipt. Restore
only into absent destinations; do not overwrite newer work. The entire original
shared root and selected Graphify original are also retained. Restoring the shared
root would reintroduce the retired entries, so use the per-entry map for selective
restoration. No restore was executed as a final operation.

At cleanup verification time, no MCP address change, plugin uninstall,
source-package deletion, global config edit, commit/push or automatic Task archive
had occurred. The receipt's `git_actions` records that verification phase.

The user subsequently authorized committing and pushing the cleanup records.
Publication is limited to this Task and the session's Journal/index updates;
the existing `AGENTS.md` deletion and old LAN task remain outside that scope.

Reference: https://learn.chatgpt.com/docs/build-skills (local discovery, symlink
support and non-merging same-name entries). Filesystem evidence remains the basis
for the actual deletion choices.
