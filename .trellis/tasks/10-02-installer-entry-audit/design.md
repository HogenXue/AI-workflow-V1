# Installer dependency bootstrap

The Bash and PowerShell entries dispatch a `deps` component before full-profile writes, after the
wizard's existing confirmation. Standalone components retain explicit behavior. Shell wrappers
select a working Python interpreter and invoke one shared standard-library Python implementation
so command detection, installation, and verification cannot drift between hosts.

The helper keeps commands that already work. Missing npm CLIs are installed globally using
`gitnexus@latest` and `@mindfoldhq/trellis@latest` with engine checks. Missing Graphify is installed
with `python -m venv` and venv-local pip into `~/.agents/tools/graphify`, isolating it from system
Python. Runtimes are prerequisites; the installer never uses sudo or installs OS runtimes.

A temporary path report transfers npm/Graphify executable directories back to the wizard, which
updates only its process environment before launching children. Shell profiles are not rewritten.
The Graphify component also checks the managed environment when its CLI is absent from PATH.

Failures retain their nonzero status and stop profile writes. Earlier dependency installations
are retained for retry, rather than being uninstalled. Existing Graphify environments are reused
only when they are venvs; arbitrary files/directories in the managed location are rejected.

Official installation sources were checked on 2026-10-02:
- https://github.com/abhigyanpatwari/GitNexus
- https://github.com/Graphify-Labs/graphify
- https://github.com/mindfold-ai/Trellis

Graph traversal is unavailable (partial/error result). Use the previously approved source
reference review plus dual-shell regression strategy and state that limitation explicitly.

## Final-review repair

Resolve each existing path component with PowerShell's existing LinkType/Target metadata, following
relative and absolute link targets with a bounded recursion. This supports PowerShell 7.0 without
.NET 6 ResolveLinkTarget APIs, resolves parent links, and retains normalized nonexistent suffixes.
Source overlap and backup containment checks refuse paths that cannot be safely resolved.

Use the existing rollback-target helper for Graphify failure, passing whether the target existed
before install. Newly created targets are cleared; backed-up targets are restored. Both failure
branches and both ports follow the same contract.

Launch component children through the pwsh binary under PSHOME, preserving process isolation,
NoProfile, argument arrays and exit propagation without Environment.ProcessPath.
