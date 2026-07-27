# Implement: Windows PowerShell installers (parent)

Parent does **not** implement code. Execution order and gates:

## Order

1. Start **`07-27-ps-install-lib`** → implement + check → finish/archive when green.
2. Start **`07-27-ps-install-components`** and/or **`07-27-ps-install-merge`** (after lib exists; may sequentialize if one agent).
3. Start **`07-27-ps-install-entry`** (needs components + merge scripts present).
4. Start **`07-27-ps-install-ci-docs`** (may add failing/skeleton tests earlier; must go green after entry).
5. Parent integration review against `prd.md` AC-P1…P5 → archive parent.

## Per-child gate before moving on

- Child `prd.md` / `design.md` / `implement.md` complete and reviewed.
- `task.py start` on that child only.
- `trellis-check` (or equivalent) passes for that child’s scope.
- Do not start parent for implementation.

## Validation (integration)

```text
# Windows
pwsh -NoProfile -File scripts/install.ps1   # expect usage exit 2 when stdin not TTY
scripts\install.cmd skills --dry-run --target <temp>
# plus full PS test modules

# Non-Windows CI (unchanged expectation)
python -m pytest tests/test_install.py tests/test_install_interactive.py
```

## Risky points

- Backup lock semantics on NTFS vs mkdir-lock.
- Symlink privileges on Windows CI runners.
- Path normalization with drive letters vs bash `/`.
- `python` vs `python3` on CI images.

## Rollback

- Delete new `scripts/*.ps1` / `install.cmd` and PS tests; revert CI matrix; bash remains authoritative.
