# Finish Work

Archive the completed task selected by the user's finish-work request and record the session. Reuse existing task and Git authorization; archive and journal operations do not grant commit or push permission.

## 1. Confirm scope and completion

```bash
python3 ./.trellis/scripts/get_context.py --mode record
python3 ./.trellis/scripts/task.py current --source
git status --short
```

Read the selected task's acceptance criteria, verification record and outstanding blockers. Archive only tasks the user selected or authorized through this finish-work request and whose required acceptance is satisfied. Leave unrelated active/completed tasks alone. A check result, missing active pointer or conversational claim alone does not prove completion.

Identify task-owned changes, including earlier commits, staged/unstaged files and new files. Preserve unrelated work, including files under `.trellis/tasks/` and `.trellis/workspace/`. If a required acceptance criterion is unresolved, record the blocker and keep that task active. Reuse valid evidence; archive bookkeeping alone does not require rerunning implementation checks.

## 2. Archive without implicit Git actions

```bash
python3 ./.trellis/scripts/task.py archive <task-name> --no-commit
```

Use the selected task's actual path/name. Verify that the archive exists, task status is `completed`, evidence files remain present and session pointers no longer target the moved path. No selected completed task means this step is skipped.

Uncommitted task changes are reported as pending Git work. If the project explicitly requires publication before archive, satisfy that gate under existing authorization or report it as blocked; do not infer Git permission from the archive request.

## 3. Record the session

```bash
python3 ./.trellis/scripts/add_session.py \
  --title "Session Title" \
  --summary "Verified outcome and remaining work" \
  --no-commit
```

Add `--commit "hash1,hash2"` only for verified commits that actually contain this task's work. Record acceptance coverage, uncovered boundaries, archive paths and pending Git work. Use a content file or stdin for longer records.

Check the installed scripts' `--help` before using version-specific options. If `--no-commit` is unavailable, use a documented equivalent that preserves the Git boundary or report that limitation before calling an auto-committing command.

## 4. Close out

Review the resulting diff and preservation of unrelated work. When the user has already authorized committing these records, use the project's scoped Git procedure with that authorization; otherwise leave the changes available for review. Report archive, journal, commit and push outcomes separately, based on actual results.
