# Implement: ps-install-lib

1. Add `scripts/install-lib.ps1` porting all helpers from `install-lib.sh`.
2. Add focused tests or a small harness invoked by pytest subprocess (may land under ci-docs; minimum: parallel backup uniqueness runnable).
3. Manual: dot-source in pwsh and exercise backup once under a temp dir.
4. Check against child PRD AC; do not start components until lib usable.

Validation:

```text
pwsh -NoProfile -Command ". ./scripts/install-lib.ps1; ..."
# plus whatever lib tests exist
```
