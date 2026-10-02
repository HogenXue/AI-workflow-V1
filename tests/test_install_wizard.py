"""Exercise real wizard control flow using harmless component subprocess fixtures."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ("deps", "skills", "graphify", "config", "agents", "codex-merge", "cursor-merge", "claude-merge")


class WizardHarness:
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.publish_path = False
        self.env = {**os.environ, "HOME": str(self.home), "CODEX_HOME": str(self.home / ".codex")}

    def prepare(self, failure: str = "", status: int = 37) -> Path:
        entry = ROOT / "scripts" / f"install.{self.ext}"
        source = entry.read_text(encoding="utf-8")
        if self.ext == "ps1":
            source = source.split("# --- entry ---", 1)[0]
            source += "\nfunction Test-InstallLibStdinTty { return $true }\nInvoke-InteractiveMain\n"
        else:
            source = source.split("if (($# == 0)); then", 1)[0]
            # Keep real reads; only replace TTY-sensitive yes/no prompts.
            source += '\ninstall_lib_prompt_yn() { [[ "$1" != Existing* ]]; }\ninteractive_main\n'
        harness = self.root / f"wizard.{self.ext}"
        harness.write_text(source, encoding="utf-8")
        shutil.copyfile(ROOT / "scripts" / f"install-lib.{self.ext}", self.root / f"install-lib.{self.ext}")
        for component in COMPONENTS:
            code = status if component == failure else 0
            if self.ext == "ps1":
                body = f"[Console]::Out.WriteLine('CALLED:{component}');\n"
                if self.publish_path and component == "deps":
                    directory = str(self.root / "tools bin").replace("'", "''")
                    body += ("$idx = [Array]::IndexOf($args, '--path-file'); "
                             f"Set-Content -LiteralPath $args[$idx + 1] -Value '{directory}' -Encoding utf8;\n")
                if self.publish_path and component == "skills":
                    body += ("Get-Command path-marker -ErrorAction Stop | Out-Null; "
                             "if ((Get-Command python).Source -like '*tools bin*') { exit 14 }; "
                             "[Console]::Out.WriteLine('PATH-REACHED');\n")
            else:
                body = f"printf '%s\\n' 'CALLED:{component}'\n"
                if self.publish_path and component == "deps":
                    directory = (self.root / "tools bin").as_posix().replace("'", "'\"'\"'")
                    body += f"while (($#)); do if [[ \"$1\" == --path-file ]]; then printf '%s\\n' '{directory}' > \"$2\"; break; fi; shift; done\n"
                if self.publish_path and component == "skills":
                    body += ("command -v path-marker >/dev/null || exit 12\n"
                             "[[ \"$(command -v python)\" != *'tools bin'* ]] || exit 14\n"
                             "printf '%s\\n' 'PATH-REACHED'\n")
            body += f"exit {code}\n"
            (self.root / f"install-{component}.{self.ext}").write_text(body, encoding="utf-8")
        return harness

    def run_wizard(self, answers: str, *, failure: str = "") -> subprocess.CompletedProcess[str]:
        harness = self.prepare(failure)
        if self.ext == "ps1":
            # Console input injection bypasses the real TTY gate only in the harness.
            quoted = str(harness).replace("'", "''")
            command = ("$global:LASTEXITCODE = 0; "
                       "[Console]::SetIn([IO.StringReader]::new([Console]::In.ReadToEnd())); "
                       f"& '{quoted}'; exit $LASTEXITCODE")
            argv = [shutil.which("pwsh"), "-NoProfile", "-Command", command]
        else:
            argv = [shutil.which("bash"), str(harness)]
        result = subprocess.run(argv, input=answers.encode("utf-8"), capture_output=True,
                                env=self.env, cwd=self.root, timeout=30, check=False)
        return subprocess.CompletedProcess(result.args, result.returncode,
                                           result.stdout.decode("utf-8"), result.stderr.decode("utf-8"))

    def test_failed_component_stops_remaining_profiles(self) -> None:
        result = self.run_wizard("1 3\n1\ny\n", failure="skills")
        self.assertEqual(result.returncode, 37, result.stderr + result.stdout)
        self.assertIn("CALLED:skills", result.stdout)
        for component in COMPONENTS[2:]:
            self.assertNotIn(f"CALLED:{component}", result.stdout)
        self.assertNotIn("Installing Claude profile", result.stdout)
        self.assertNotIn("Done.", result.stdout)

    def test_dependencies_run_before_profile_writes(self) -> None:
        result = self.run_wizard("3\n1\ny\n")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertLess(result.stdout.index("CALLED:deps"), result.stdout.index("CALLED:skills"))

    def test_dependency_failure_stops_before_profile_writes(self) -> None:
        result = self.run_wizard("1 3\n1\ny\n", failure="deps")
        self.assertEqual(result.returncode, 37, result.stderr + result.stdout)
        for component in COMPONENTS[1:]:
            self.assertNotIn(f"CALLED:{component}", result.stdout)
        self.assertNotIn("Done.", result.stdout)

    def test_dependency_paths_reach_profile_components(self) -> None:
        self.publish_path = True
        directory = self.root / "tools bin"
        directory.mkdir()
        marker = directory / ("path-marker.cmd" if self.ext == "ps1" else "path-marker")
        marker.write_text("echo marker\n", encoding="utf-8", newline="\n")
        marker.chmod(0o755)
        shadow = directory / ("python.cmd" if self.ext == "ps1" else "python")
        shadow.write_text("echo unexpected-python\n", encoding="utf-8", newline="\n")
        shadow.chmod(0o755)
        result = self.run_wizard("3\n1\ny\n")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("PATH-REACHED", result.stdout)

    def test_invalid_modes_and_eof_do_not_run_components(self) -> None:
        for mode in ("9\n", "typo\n", ""):
            with self.subTest(mode=mode):
                result = self.run_wizard("3\n" + mode)
                self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
                self.assertIn("ERROR: invalid install mode", result.stderr)
                self.assertNotIn("CALLED:", result.stdout)
                self.assertNotIn("Done.", result.stdout)

    def test_default_mode_and_successful_profile(self) -> None:
        result = self.run_wizard("3\n\ny\n")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        for component in ("skills", "config", "agents", "claude-merge"):
            self.assertIn(f"CALLED:{component}", result.stdout)
        self.assertIn("Done.", result.stdout)

    def test_single_component_failure_propagates(self) -> None:
        result = self.run_wizard("3\n2\nconfig\n", failure="config")
        self.assertEqual(result.returncode, 37, result.stderr + result.stdout)
        self.assertNotIn("Done.", result.stdout)

    def test_declined_dangling_roots_skip_skills_and_config(self) -> None:
        parent = self.home / ".claude"
        parent.mkdir()
        for name in ("skills", "config"):
            try:
                (parent / name).symlink_to(self.home / f"missing-{name}", target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"Directory symlinks unavailable: {exc}")
        result = self.run_wizard("3\n1\ny\nn\nn\nn\n")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("SKIP: Claude skills", result.stdout)
        self.assertIn("SKIP: Claude config", result.stdout)
        self.assertNotIn("CALLED:skills", result.stdout)
        self.assertNotIn("CALLED:config", result.stdout)


@unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7+ required")
class PowerShellWizardTests(WizardHarness, unittest.TestCase):
    ext = "ps1"


@unittest.skipUnless(shutil.which("bash"), "Bash required")
class BashWizardTests(WizardHarness, unittest.TestCase):
    ext = "sh"

    def test_real_dependency_preview_does_not_create_tools(self) -> None:
        result = subprocess.run(
            [shutil.which("bash"), str(ROOT / "scripts" / "install.sh"), "deps", "--dry-run"],
            capture_output=True, env=self.env, cwd=ROOT, timeout=30, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8"))
        self.assertIn(b"DEPENDENCIES:", result.stdout)
        self.assertFalse((self.home / ".agents").exists())

    def test_real_agents_installer_reads_canonical_template(self) -> None:
        target = self.root / "claude"
        result = subprocess.run(
            [shutil.which("bash"), str(ROOT / "scripts" / "install.sh"), "agents", "--apply",
             "--agents-home", target.as_posix(), "--document-name", "CLAUDE.md", "--no-hooks-feature"],
            capture_output=True, env=self.env, cwd=ROOT, timeout=30, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8"))
        self.assertEqual((target / "CLAUDE.md").read_bytes(),
                         (ROOT / "agents" / "AGENTS.global.md").read_bytes())
        self.assertFalse((target / "config.toml").exists())

    def test_real_cursor_installer_generates_canonical_rule_body(self) -> None:
        project = self.root / "project"
        project.mkdir()
        (project / "AGENTS.md").write_text("project-owned\n", encoding="utf-8")
        result = subprocess.run(
            [shutil.which("bash"), str(ROOT / "scripts" / "install.sh"), "cursor-merge",
             "--mcp-keep", "--project-root", project.as_posix(),
             "--mcp-file", (self.root / "mcp.json").as_posix(),
             "--backup-dir", (self.root / "backup").as_posix()],
            capture_output=True, env=self.env, cwd=ROOT, timeout=30, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8"))
        rule = (project / ".cursor" / "rules" / "ai-workflow-global.mdc").read_text(encoding="utf-8")
        expected = (ROOT / "agents" / "AGENTS.global.md").read_text(encoding="utf-8")
        self.assertEqual(rule.split("---", 2)[2].lstrip("\n"), expected + "\n")
        self.assertEqual((project / "AGENTS.md").read_text(encoding="utf-8"), "project-owned\n")


if __name__ == "__main__":
    unittest.main()
