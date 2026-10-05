# Design

## Ownership

Trellis remains the sole owner of planning artifacts, task lifecycle, checks, and session records. AIHero contributes methods, not another router or state machine. No executable symbol or installer contract changes are planned.

## Integration surfaces

- `agents/AGENTS.global.md`: distributable, self-contained practice guidance for downstream Trellis projects; existing installers already use this source.
- `agents/AGENTS.project.md` and repository `AGENTS.md`: consistent ordinary planning and explicit-only Grill routing.
- `.trellis/workflow.md`: canonical phase guidance and matching breadcrumbs.
- `.claude/skills/trellis-brainstorm/SKILL.md`: evidence-first decision frontier, outcome slicing, and conditional domain/decision capture.
- `.claude/skills/trellis-check/SKILL.md`: task-scoped Spec and Standards review including dirty/new files.
- Native continue/check agent instructions: reuse canonical artifacts and cover both review dimensions in dispatch mode.
- `.trellis/spec/decisions/`: stable integration boundary with source links.

## Source-based impact assessment

Instruction/document changes only: no runtime symbols, API/data contracts, migrations, deletions, or installer implementation changes. GitNexus CLI is installed and its index matches HEAD, but query FTS is unavailable and the inspected PowerShell symbol is unindexed (risk UNKNOWN). This is not successful graph impact analysis. Source inspection of routing, manifests, installer template selection, and existing tests establishes the documentation scope. Ordinary source analysis is permitted for these low-risk instruction changes.

Existing unrelated edits include an in-flight move of root templates into `agents/`. Use current paths and narrow patches; do not revert that work or change installers for stale paths. Do not write user-level Codex files.

## Compatibility and rollback

Keep `grill-me`, its explicit invocation policy, the manifest, task schema, parser tags, and artifact roles. Installation propagates global guidance through the existing template path. Native skill/workflow changes apply in this repository; downstream native files are not silently overwritten. Revert only this task's documentation hunks if needed.
