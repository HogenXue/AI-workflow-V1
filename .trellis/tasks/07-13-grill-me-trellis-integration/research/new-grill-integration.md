# New Grill integration

Upstream source reviewed at `mattpocock/skills` commit `c55ee46073ed923f86ce59a5eb3b6d895095d1b7`.

The upstream architecture separates an explicit `grill-me` entrypoint from its interview primitive. The user chose a single visible Skill, so this package inlines the current interview method into `grill-me` and removes the older or split variants:

- `grill-me` is explicit-only and stateless;
- it works in dependency-aware rounds using the current frontier;
- facts are researched by the agent while decisions remain with the user;
- ungrillable questions stop and become bounded prototype or research needs;
- Trellis resumes after the session and remains authoritative for PRD, Design/Plan, domain, and decision documents;
- no `CONTEXT.md`, `docs/adr/`, second task, or second approval lifecycle is created in Trellis projects.

The installed copy uses `~/.agents/skills` as the canonical root. Old Grill variants and same-name copies under `~/.codex/skills` are backed up before pruning.
