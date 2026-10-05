---
name: trellis-brainstorm
description: "Resolve unsettled requirements in native Trellis planning using repository evidence, dependency-aware questions, and testable outcome slices. Use when user choices still block implementation; reuse agreed conclusions and skip interviewing clear requests."
---

# Trellis Brainstorm

## Interview Scope

The installed `grill-with-docs` capability is an alternative documented interview within the same Trellis phase. Select one; do not interview again after its conclusions are confirmed. `to-spec`, `to-tickets`, and `wayfinder` reuse these same artifacts rather than establishing another planning workflow.

Use this skill for unresolved requirements in Trellis Phase 1.1, not as an automatic interview for every complex task. Reuse approved conclusions and inspect the repository before asking. If the request is clear, record the required artifacts and proceed under existing authorization.

An explicitly invoked `grill-me` is a separate stateless conversation. After its conclusions are confirmed, Trellis persists them without launching this skill for another interview. Revisit only a newly changed requirement.

Treat unresolved choices as a dependency tree. Ask one high-value question at a time from the current frontier: decisions whose prerequisites are already settled. Give a recommended answer and its trade-off. Do not ask dependent questions until the prerequisite is resolved.

If a choice needs research or a bounded prototype, record the question, evidence needed, and completion condition in the current task. Pause that branch and continue independent planning; do not turn speculation into a user decision or begin unauthorized prototype work.

## Non-Negotiable Evidence Rule

If a question can be answered by exploring the codebase, explore the codebase instead.

This is mandatory. Before asking the user a question, first check whether the answer is already available in code, tests, configs, docs, existing specs, or task history.

Do not ask the user to confirm facts that the repository can answer. Ask only for product intent, preference, scope, risk tolerance, or decisions that remain ambiguous after inspection.

---

Use this skill during Phase 1 planning to turn the user's request into clear requirements and planning artifacts.

## Preconditions

Resolve task authorization under `.trellis/workflow.md` first. An explicit implementation request authorizes task recording within its settled scope; do not ask again solely to create a task. Consultation alone does not authorize task creation or implementation.

If no task exists yet, create one:

```bash
TASK_DIR=$(python3 ./.trellis/scripts/task.py create "<short task title>" --slug <slug>)
```

Use a concise title from the user's request. Use a slug without a date prefix. `task.py create` adds the `MM-DD-` directory prefix automatically.

`task.py create` creates the default `prd.md`. Update that file with the current understanding before asking follow-up questions.

## Planning Flow

1. Capture the user's request and initial known facts in `prd.md`.
2. Inspect available evidence before asking questions:
   - code, tests, fixtures, and configs
   - README files, docs, existing specs, and domain notes
   - related Trellis tasks, research files, and session history when present
3. Separate what you found into:
   - confirmed facts
   - product intent still needed from the user
   - scope or risk decisions still needed from the user
   - likely out-of-scope items
4. Ask the single highest-value remaining question whose prerequisites are settled; if none remains, do not manufacture an interview.
5. Include your recommended answer with the question.
6. After each user answer, update `prd.md` before continuing.
7. For complex tasks, create or update `design.md` and `implement.md` before implementation starts.
8. Before final review or `task.py start`, run the PRD convergence pass below.

Do not invent a project-specific product/spec hierarchy. If the repository already has product, domain, or spec docs, use them. If it does not, proceed with the evidence that exists.

## Question Rules

Ask only one question per message.

Each question must include:

- the decision needed
- why the answer matters
- your recommended answer
- the trade-off if the user chooses differently

Do not ask process questions such as whether to search, inspect files, or continue brainstorming. Do the evidence work directly. Ask the user only when the remaining issue is a product decision, preference, scope boundary, or risk tolerance choice.

## Thinking Framework: First Principles Analysis

When requirements are vague, solutions feel over-engineered, or you're about to add complexity "because everyone does" — decompose to fundamental truths before reasoning upward.

### Step 1: Restate the Problem

Strip away implementation details to one sentence.

> Bad: "We need to add Redis caching to the user profile endpoint"
> Good: "User profile data takes too long to load"

### Step 2: List Fundamental Truths

What is absolutely true (not opinion or convention)?

| Category | Examples |
|----------|----------|
| **Physical constraints** | Network latency ≥ 0, disk I/O has limits |
| **Business rules** | "Users must see their own data" |
| **Technical invariants** | "Data must be consistent" |
| **User needs** | "The user wants X within Y seconds" |

### Step 3: Challenge Assumptions

For each component of the current plan:

- **Fact or convention?** "We always use REST" — why?
- **What if we removed this?** If nothing breaks, it's unnecessary.
- **Solving the actual problem or a symptom?** Trace the causal chain.
- **Who benefits from this complexity?** If "nobody", simplify.

### Step 4: Build Up from Truths

1. Start with the minimum viable mechanism satisfying all truths
2. Add complexity only when a specific truth demands it
3. Each addition must answer: "Which truth requires this?"

### Step 5: Validate

- Does the solution solve the original problem?
- What assumptions need verification?
- What's the simplest experiment to test this?

## Artifact Rules

### Outcome slicing and blockers

Split large scopes only when each child delivers an independently demonstrable or verifiable outcome. Prefer the smallest complete path through the necessary layers over separate schema/API/UI tasks. Keep related small work in one task; do not create children just to reproduce an upstream ticket workflow.

For each child, record its outcome, acceptance criteria, actual blockers, and what evidence clears them. Use native Trellis parent/child commands; tree position and numbering do not imply a dependency. Choose the next task whose blockers are satisfied. An unresolved decision belongs in planning, not in a supposedly implementation-ready child.

Capture the parent path explicitly. When drafting multiple children, use native `create --parent <parent> --no-start` where supported and verify the session remains on the parent with children in `planning`. Default `create` activates the new child; do not use `start` merely to restore context and accidentally advance a planning task to implementation.

Broad migrations can use expand, migrate, then contract, with compatibility and validation boundaries in `design.md` / `implement.md`. Do not force an unsafe migration into artificial vertical slices.

### Domain terms and durable decisions

Read existing domain/decision specs before introducing new language. Clarify overloaded terms with concrete examples and verify code agrees. Persist resolved terms in the existing domain location, not the PRD or a new root glossary.

Keep task-specific choices in `design.md`. Record a durable decision in the project's existing decision location only when it is costly to reverse, surprising without context, and reflects a real trade-off. Create entries lazily; empty glossary/ADR scaffolds are unnecessary. In this project, use `.trellis/spec/domain/` and `.trellis/spec/decisions/`.

`prd.md` records requirements and acceptance:

- goal and user value
- confirmed facts
- requirements
- acceptance criteria
- out of scope
- open questions that still block planning

`design.md` records technical design for complex tasks:

- architecture and boundaries
- data flow and contracts
- compatibility and migration notes
- important trade-offs
- operational or rollback considerations

`implement.md` records execution planning for complex tasks:

- ordered implementation checklist
- validation commands
- risky files or rollback points
- follow-up checks before `task.py start`

Lightweight tasks may have only `prd.md`. Complex tasks must have `prd.md`, `design.md`, and `implement.md` before `task.py start`.

`implement.md` is not a replacement for `implement.jsonl`. On sub-agent-dispatch workflows, `implement.jsonl` and `check.jsonl` must each contain at least one real spec/research entry before `task.py start`; the seed `_example` row does not count. Inline workflows skip this JSONL gate because Phase 2 loads context through `trellis-before-dev`.

## PRD Convergence Pass

Before declaring planning ready or running `task.py start`, rewrite `prd.md` once against the final structure described in the artifact rules above. This is not optional cleanup; it is the final planning gate.

The pass must be lossless:

- Collapse repeated facts into one authoritative section.
- Fold temporary brainstorm sections such as `What I already know`, `Assumptions`, and resolved `Open Questions` into Goal, Background, Requirements, Technical Notes, or Acceptance Criteria.
- Remove resolved open questions instead of leaving empty or already-answered sections.
- Merge parallel bug and requirement lists when they describe the same work; keep each defect's severity, evidence, and file:line anchors on the owning requirement.
- Preserve every file:line anchor, decision, constraint, requirement ID, and acceptance-criteria mapping.
- Keep only genuinely blocking open questions.

After the pass, read `prd.md` top to bottom and verify that no fact is repeated across sections unless the repetition adds new information.

## Quality Bar

Before declaring planning ready:

- `prd.md` contains testable acceptance criteria.
- `prd.md` has passed the PRD convergence pass: no unresolved temporary brainstorm sections, no duplicate facts across sections, and no lost anchors, decisions, or acceptance mappings.
- Repository-answerable questions have already been answered through inspection.
- Remaining open questions are genuinely about user intent or scope.
- Complex tasks have `design.md` and `implement.md`.
- Sub-agent-dispatch tasks have real curated entries in both `implement.jsonl` and `check.jsonl`; seed-only manifests are not ready.
- The user has reviewed the final planning artifacts or explicitly approved proceeding.

Do not start implementation until the user approves or asks for implementation.
