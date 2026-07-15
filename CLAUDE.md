<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **AI-workflow-V1** (835 symbols, 1357 relationships, 26 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- Follow the project's risk-driven policy: run impact analysis before cross-module, public contract/data contract, deletion/migration, high-risk, or unfamiliar call-chain changes. Local low-risk edits may use ordinary source reading and targeted tests.
- Run `gitnexus_detect_changes()` before committing only when project rules require it, graph impact analysis was used, or the change is cross-module/high-risk. Otherwise use standard Git scope checks and relevant tests.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/AI-workflow-V1/context` | Codebase overview, check index freshness |
| `gitnexus://repo/AI-workflow-V1/clusters` | All functional areas |
| `gitnexus://repo/AI-workflow-V1/processes` | All execution flows |
| `gitnexus://repo/AI-workflow-V1/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
