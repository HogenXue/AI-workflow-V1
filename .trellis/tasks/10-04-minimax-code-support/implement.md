# Execution plan

1. Record confirmed scope and verified official contracts; validate task context
   references before starting.
2. Add focused regression tests for components, native fields, path overrides,
   precedence, preservation/preview/errors and wizard profiles. Run new cases
   and record feature-missing failures before production edits.
3. Extend JSON MCP routing; add shared Bash/PowerShell component drivers, thin
   wrappers, native fragments and independent menu/profile routes.
4. Run new and adjacent tests; repair relevant failures. Update README and specs.
5. Apply native `trellis-check` manually in configured Codex inline mode. Record
   commands, results, preservation and unsupported runtime checks. Do not commit,
   push, install real profiles or archive automatically.

## Selected final checks

- Follow-up default URL scope: `test_mcp_defaults.py`, `test_install_interactive.py`,
  `test_install_new_hosts.py` and `test_install_merge_ps.py`; reuse unrelated
  successful wizard/entry evidence because those production sources are unchanged.

- `python3 -m unittest discover -s tests -p test_install_new_hosts.py -v`
- `python3 -m unittest discover -s tests -p test_install_wizard.py -v`
- `python3 -m unittest discover -s tests -p test_install_interactive.py -v`
- `python3 -m unittest discover -s tests -p test_install_entry_ps.py -v`
- `python3 -m unittest discover -s tests -p test_install_merge_ps.py -v`
- Bash syntax: entry, new drivers and wrappers; native PowerShell parser/runtime
  checks only when a usable existing `pwsh` is available.
- `task.py validate`, `git diff --check`, scoped spec review and dirty-change
  preservation comparison.

No full repository suite, package installation or application/API runtime test.
