---
name: trellis-check
description: "Comprehensive quality verification: spec compliance, lint, type-check, tests, cross-layer data flow, code reuse, and consistency checks. Use when code is written and needs quality verification, before committing changes, or to catch context drift during long sessions."
---

# Code Quality Check

Comprehensive quality verification for recently written code. Combines spec compliance, cross-layer safety, and pre-commit checks.

Review the current task's authorized files and applicable acceptance criteria. In a dirty worktree, distinguish task changes from unrelated existing work; do not treat every diff as permission to edit it. Read-only review requests authorize findings, not fixes.

---

## Step 1: Identify What Changed

```bash
git diff --name-only HEAD
git status --short
git ls-files --others --exclude-standard
```

Establish the current task's scope from its artifacts and implementation record. Inspect staged and unstaged diffs, read task-owned untracked files, and include earlier task commits against the task's verified base when relevant. A clean working tree does not mean the task has no changes. Do not review or fix unrelated user changes. Report an unresolved boundary/base instead of choosing an arbitrary baseline.

## Step 2: Read Task Artifacts and Applicable Specs

Read the current task artifacts in order:

- `prd.md`
- `design.md` if present
- `implement.md` if present

```bash
python3 ./.trellis/scripts/get_context.py --mode packages
```

For each changed package/layer, read the spec index and follow its **Quality Check** section:

```bash
cat .trellis/spec/<package>/<layer>/index.md
```

Read the specific guideline files referenced — the index is a pointer, not the goal.

## Step 3: Run Project Checks

Run checks required by the current task and applicable specs. Fix failures introduced by this task within its authorized scope; report pre-existing failures separately. Documentation-only changes can use file/reference checks when those cover the risk. Do not expand to full-repository tests unless the task or unresolved evidence requires them.

## Step 4: Review Against Checklist

### Spec: Requirements and behavior

- Map PRD acceptance criteria to implementation or verification evidence; identify missing, partial, or incorrect behavior.
- Check relevant contracts, design, and failure/edge cases, not only file/test presence.
- Identify unauthorized scope expansion and unresolved assumptions presented as decisions.

### Standards: Project conventions and maintainability

- Cite the applicable project rule for hard violations; distinguish them from design heuristics or optional improvements.
- Project conventions override generic preferences. Consider naming, duplication, scattered changes, unnecessary abstraction, and module boundaries only where relevant to this diff.
- Avoid repeating findings already enforced by selected tooling.

Report both dimensions separately, even when one has no findings. Passing Standards does not establish requirements compliance. Use the existing native check; two dimensions do not require two new agents.

The installed `code-review` capability supplies this analysis inside the same native gate. Do not launch a second review or repeat still-valid checks simply because another skill name is used.

### Code Quality

- [ ] Linter passes?
- [ ] Type checker passes (if applicable)?
- [ ] Tests pass?
- [ ] No debug logging left in?
- [ ] No suppressed warnings or type-safety bypasses?

### Test Coverage

- [ ] New function → unit test added?
- [ ] Bug fix → regression test added?
- [ ] Changed behavior → existing tests updated?

### Spec Sync

- [ ] Does `.trellis/spec/` need updates? (new patterns, conventions, lessons learned)

> "If I fixed a bug or discovered something non-obvious, should I document it so future me won't hit the same issue?" → If YES, update the relevant spec doc.

## Step 5: Cross-Layer Dimensions (if applicable)

Skip this step if your change is confined to a single layer.

### A. Data Flow (changes touch 3+ layers)

- [ ] Read flow traces correctly: Storage → Service → API → UI
- [ ] Write flow traces correctly: UI → API → Service → Storage
- [ ] Types/schemas correctly passed between layers?
- [ ] Errors properly propagated to caller?

### B. Code Reuse (modifying constants, creating utilities)

- [ ] Searched for existing similar code before creating new?
  ```bash
  grep -r "pattern" src/
  ```
- [ ] If 2+ places define same value → extracted to shared constant?
- [ ] After batch modification, all occurrences updated?

### C. Import/Dependency (creating new files)

- [ ] Correct import paths (relative vs absolute)?
- [ ] No circular dependencies?

### D. Same-Layer Consistency

- [ ] Other places using the same concept are consistent?

---

## Step 6: Report and Fix

Record Spec and Standards findings separately, with criterion/rule evidence and severity. Include the reviewed scope (including task-owned new files), actual commands/results, and uncovered boundaries in the current task. Unrun checks are not passes. Check completion does not grant task-state or Git authorization.

Report findings with their scope and evidence. When implementation is authorized, fix task-caused violations and rerun affected checks. Report unrelated failures or unresolved business decisions without silently changing their files or relaxing checks.
