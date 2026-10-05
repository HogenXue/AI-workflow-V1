# Design

Extend the manifest from 7 to 18 skills. New skills have self-contained instructions and Codex metadata, upstream MIT license, and pinned provenance (`mattpocock/skills` commit `24fe0ef7737efae15c87225755e9f6f5965e4888`). Keep existing adapted skills intact.

`grill-me` stays explicit/stateless. `grill-with-docs` interviews unresolved task choices and records conclusions, replacing rather than duplicating native brainstorm. `to-spec` synthesizes the PRD; `to-tickets` creates native planning children with blockers; `wayfinder` maps prerequisite decisions in existing artifacts. `implement` follows authorized reviewed artifacts and native execution policy with selective TDD. `code-review` adds Spec/Standards review inside native check, with read-only behavior when only review is authorized. Support skills use research/task/journal locations. None grants Git authorization or creates a second lifecycle.

For non-Trellis projects, retain existing document/tracker conventions. Remove mandatory platform-specific Skill-tool/background-agent calls; work inline unless dispatch is configured/authorized.

Generic installers already enumerate the manifest and copy folders. Remove restored names from both legacy arrays; preserve dry-run, replacement, timestamped backups and rollback. Improve both one-click plan texts without adding components/prompts. Templates distribute through existing profile paths; other projects' native files are not silently overwritten.

GitNexus index is stale. Historical `_manifest_skills`/`validate_skill` impact reports LOW (one direct caller). Source confirms current manifest enumeration and host dispatch; PowerShell coverage is incomplete, supplemented by source tracing and real isolated tests. No graph rebuild, installer signature, task schema, MCP/hook scope change is needed. Snapshot unrelated dirty edits; rollback only task-owned hunks.
