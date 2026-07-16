---
name: resolving-merge-conflicts
description: "Resolve an already in-progress Git merge or rebase conflict by tracing both sides to their primary intent and verifying the combined result. Use when the user explicitly asks to resolve current merge/rebase conflicts; do not start, abort, commit, continue, or push the Git operation without matching authorization."
---

1. **Confirm scope and authorization.** Verify that a merge or rebase is already in progress. A request to resolve files does not by itself authorize starting another Git operation, committing, continuing the rebase, or pushing.

2. **See the current state** of the merge/rebase. Check git history, status, and the conflicting files. Preserve unrelated user changes.

3. **Find the primary sources** for each conflict. Understand why each change was made and the original intent. Read commit messages and the relevant Trellis PRD/Design; inspect PRs or issues only when they are the actual source.

4. **Resolve each hunk.** Preserve both intents where possible. Where they are incompatible, stop for a user decision unless the authoritative requirement makes the choice unambiguous. Do not invent new behavior, run `--abort`, or discard either side silently.

5. **Verify.** Run `git diff --check`, confirm no conflict markers remain, then run the project's relevant automated checks. Fix only regressions caused by the resolution and report anything outside scope.

6. **Hand back control.** Report resolved files, intent choices, and checks. Stage, commit, run `git merge --continue`/`git rebase --continue`, or push only when the user explicitly authorized that exact Git action.
