"""Install missing tool CLIs without changing host profiles or project state."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


TOOLS = ("gitnexus", "trellis", "graphify")
NPM_PACKAGES = {"gitnexus": "gitnexus@latest", "trellis": "@mindfoldhq/trellis@latest"}


class InstallError(Exception):
    def __init__(self, message: str, status: int = 1):
        super().__init__(message)
        self.status = status


def run_command(argv: list[str], *, capture: bool = False) -> str:
    try:
        result = subprocess.run(argv, check=False, text=True, encoding="utf-8",
                                errors="replace", capture_output=capture)
    except OSError as exc:
        raise InstallError(f"could not execute {argv[0]}: {exc}") from exc
    if result.returncode:
        raise InstallError(f"command failed (exit {result.returncode}): {' '.join(argv)}",
                           result.returncode if result.returncode > 0 else 1)
    return result.stdout.strip() if capture else ""


def bootstrap(home: Path, *, apply: bool, path_file: Path | None = None) -> None:
    print("DEPENDENCIES: GitNexus, Trellis, Graphify", flush=True)
    env_dir = home / ".agents" / "tools" / "graphify"
    env_bin = env_dir / ("Scripts" if os.name == "nt" else "bin")
    env_python = env_bin / ("python.exe" if os.name == "nt" else "python")
    managed_graphify = env_bin / ("graphify.exe" if os.name == "nt" else "graphify")
    resolved = {tool: shutil.which(tool) for tool in TOOLS}
    if not resolved["graphify"] and managed_graphify.is_file():
        resolved["graphify"] = str(managed_graphify)

    if not apply:
        for tool in TOOLS:
            if resolved[tool]:
                print(f"SKIP: {tool} found at {resolved[tool]} (preview)")
            elif tool in NPM_PACKAGES:
                print(f"DRY-RUN: npm install --global --engine-strict {NPM_PACKAGES[tool]}")
            else:
                print(f"DRY-RUN: {sys.executable} -m venv {env_dir}")
                print(f"DRY-RUN: {env_python} -m pip install graphifyy")
        return

    if sys.version_info < (3, 10):
        raise InstallError("Python 3.10+ is required; install Python and rerun deps --apply")
    if not resolved["graphify"] and env_dir.exists() and not (env_dir / "pyvenv.cfg").is_file():
        raise InstallError(f"managed Graphify location is not a virtual environment: {env_dir}")

    missing_npm = [tool for tool in NPM_PACKAGES if not resolved[tool]]
    npm = None
    if missing_npm:
        npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
        node = shutil.which("node")
        if not npm or not node:
            raise InstallError("Node.js/npm are required for missing GitNexus/Trellis; install a supported Node.js LTS and rerun deps --apply")
        version = run_command([node, "--version"], capture=True)
        match = re.match(r"v?(\d+)\.", version)
        if not match or int(match[1]) < 18:
            raise InstallError("Node.js 18+ is required; GitNexus latest may require a newer LTS (npm engine checks are enforced)")
        prefix = run_command([npm, "prefix", "--global"], capture=True)
        if not prefix or "\n" in prefix or "\r" in prefix:
            raise InstallError("npm returned an invalid global prefix")
        npm_bin = Path(prefix) if os.name == "nt" else Path(prefix) / "bin"
        os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + str(npm_bin)
        # An installed CLI may simply be absent from the original PATH.
        for tool in missing_npm:
            resolved[tool] = shutil.which(tool)

    # Verify every pre-existing command before installing anything else.
    for tool, executable in resolved.items():
        if executable:
            run_command([executable, "--help" if tool == "graphify" else "--version"], capture=True)
            print(f"SKIP: {tool} already usable at {executable}", flush=True)

    for tool in TOOLS:
        if resolved[tool]:
            continue
        if tool in NPM_PACKAGES:
            run_command([npm, "install", "--global", "--engine-strict", NPM_PACKAGES[tool]])
            resolved[tool] = shutil.which(tool)
        else:
            if not env_python.is_file():
                run_command([sys.executable, "-m", "venv", str(env_dir)])
            run_command([str(env_python), "-m", "pip", "install", "graphifyy"])
            resolved[tool] = str(managed_graphify) if managed_graphify.is_file() else None
        if not resolved[tool]:
            raise InstallError(f"{tool} installation returned success but its CLI is unavailable")
        run_command([resolved[tool], "--help" if tool == "graphify" else "--version"], capture=True)
        print(f"INSTALLED: {tool} -> {resolved[tool]}", flush=True)

    paths = list(dict.fromkeys(str(Path(resolved[tool]).parent) for tool in TOOLS))
    if path_file is not None:
        path_file.write_text("\n".join(paths) + "\n", encoding="utf-8", newline="\n")
    for directory in paths:
        print(f"PATH: {directory}")
    print("NOTE: CLI installation does not initialize projects or generate graphs. Add the reported directories to your shell PATH if needed.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    parser.add_argument("--path-file", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        bootstrap(Path(os.environ.get("HOME") or Path.home()), apply=args.apply, path_file=args.path_file)
        return 0
    except (InstallError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return exc.status if isinstance(exc, InstallError) else 1


if __name__ == "__main__":
    raise SystemExit(main())
