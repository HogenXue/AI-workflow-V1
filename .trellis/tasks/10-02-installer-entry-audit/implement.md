# Execution and verification

1. Preserve completed entry hardening and canonical template migration.
2. Reproduce absent dependency dispatch/preflight with the existing isolated wizard fixtures.
3. Implement the shared bootstrap and dual shell wrappers; update the wizard and Graphify locator.
4. Test existing tools, missing tools, dry-run, missing runtimes, failed installs, and PATH recovery
   with fake package managers. Do not perform real network installations.
5. Run task-scoped installer, template/config, syntax, and consumer checks; apply native
   `trellis-check` to Spec and Standards dimensions and record platform limitations.
6. Update installer documentation/specs and preserve unrelated worktree changes. No commit/push.

7. Add failing regressions for physical source aliases, junctions/nonexistent suffixes, Graphify
   failure/retry and original-target restoration. Exercise minimum PowerShell compatibility.
8. Repair the shared path resolver, both Graphify failure branches/ports, and component executable
   selection. Run related regression, complete task scope, syntax and native quality checks.
