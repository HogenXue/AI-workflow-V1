# Design

## Installation and ownership

Keep the existing Codex and Cursor profile destinations. After the user agrees to install
Skills, offer a separate default-no adoption choice when a third-party global lock exists.
Pass `--adopt-skill-lock` only after that consent. Declining leaves third-party metadata
untouched; skipping Skills does not offer or perform adoption.

A shared shell resolver selects the lock for both the wizard and component installer:
standard `~/.agents/skills`, active CODEX_HOME/skills, and `~/.cursor/skills` targets use
`$XDG_STATE_HOME/skills/.skill-lock.json` when configured, otherwise
`~/.agents/.skill-lock.json`. Custom destinations retain their documented adjacent lock,
using the caller-spelled parent even when the target Skills directory is a symlink.
This follows the locally inspected third-party CLI's actual global registration layout.
Adoption changes registration only; it does not delete or rewrite other host Skill trees.

Reuse the component's preflight validation, timestamped backup, atomic helper and rollback.
The profile prompt does not imply that replacement consent includes metadata ownership.

## Template review

Review the committed diff `git diff 3bc7af2...HEAD` at pinned HEAD `b32419b` with independent
Standards and Spec agents. Audit the three unchanged templates as additional user scope,
clearly distinguishing pre-existing issues. The global template's capability summary
must qualify Trellis-only interview/design destinations; the other two templates are
explicitly Trellis project supplements and need no speculative rewrite.

## Scope and compatibility

The prior task's adjacent-lock design is superseded only for known global host targets.
Custom-target behavior, existing non-TTY dispatch and host MCP/hook code remain intact.
No package version bump, release, Git mutation or real host installation is needed here.
