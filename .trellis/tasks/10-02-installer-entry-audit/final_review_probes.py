"""Read-only source audit with isolated destructive-failure fixtures, never real profiles."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[3]
PWSH = shutil.which("pwsh")
BASH = r"D:\Program Files\Git\bin\bash.exe" if os.name == "nt" else shutil.which("bash")


def run(argv, env=None):
    result = subprocess.run(argv, capture_output=True, timeout=30, env=env, check=False)
    return {"exit": result.returncode, "stdout": result.stdout.decode("utf-8", errors="replace"),
            "stderr": result.stderr.decode("utf-8", errors="replace")}


results = {}
with tempfile.TemporaryDirectory(prefix="installer-final-review-") as directory:
    fixture = Path(directory)
    for host in ("ps1", "sh"):
        package = fixture / ("package-" + host)
        scripts = package / "scripts"
        scripts.mkdir(parents=True)
        source = package / "config"
        source.mkdir()
        marker = source / "must-preserve.txt"
        marker.write_text("original package data\n", encoding="utf-8")
        for name in ("install-config", "install-lib"):
            destination = scripts / (name + "." + host)
            destination.write_text((ROOT / "scripts" / destination.name).read_text(encoding="utf-8"),
                                   encoding="utf-8", newline="\n")
        alias = fixture / ("alias-" + host)
        alias.symlink_to(package, target_is_directory=True)
        target = alias / "config"
        executable = [PWSH, "-NoProfile", "-File"] if host == "ps1" else [BASH]
        result = run(executable + [str(scripts / ("install-config." + host)), "--copy", "--replace",
                                  "--target", target.as_posix(), "--backup-dir", (fixture / ("backup-" + host)).as_posix()])
        result["source_marker_survives"] = marker.is_file()
        result["source_children_after"] = sorted(p.name for p in source.iterdir()) if source.is_dir() else None
        results["source_alias_overlap_" + host] = result

    for host in ("ps1", "sh"):
        home = fixture / ("home-" + host)
        home.mkdir()
        bin_dir = fixture / ("bin-" + host)
        bin_dir.mkdir()
        if host == "ps1":
            command = bin_dir / "graphify.cmd"
            command.write_text('@echo off\nmkdir "%HOME%\\.agents\\skills\\graphify" 2>nul\n'
                               'echo partial>"%HOME%\\.agents\\skills\\graphify\\partial.tmp"\nexit /b 23\n',
                               encoding="utf-8", newline="\r\n")
            executable = [PWSH, "-NoProfile", "-File"]
        else:
            command = bin_dir / "graphify"
            command.write_text('#!/usr/bin/env bash\nmkdir -p "$HOME/.agents/skills/graphify"\n'
                               'printf partial > "$HOME/.agents/skills/graphify/partial.tmp"\nexit 23\n',
                               encoding="utf-8", newline="\n")
            command.chmod(0o755)
            executable = [BASH]
        env = {**os.environ, "HOME": str(home),
               "PATH": str(bin_dir) + os.pathsep + str(Path(BASH).parent) + os.pathsep + os.environ["PATH"]}
        argv = executable + [str(ROOT / "scripts" / ("install-graphify." + host)), "--apply"]
        first = run(argv, env)
        target = home / ".agents/skills/graphify"
        first["partial_target_remains"] = (target / "partial.tmp").is_file()
        first["skill_exists"] = (target / "SKILL.md").is_file()
        retry = run(argv, env)
        results["graphify_fresh_failure_" + host] = {"first": first, "retry": retry}

print(json.dumps(results, ensure_ascii=False, indent=2))
