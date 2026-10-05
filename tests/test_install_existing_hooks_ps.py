"""Existing-target interactive merge paths, including strict-mode prompt expansion."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PWSH = shutil.which("pwsh")


@unittest.skipUnless(PWSH, "PowerShell 7+ required")
class ExistingHooksInteractiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / "package"
        scripts = self.package / "scripts"
        scripts.mkdir(parents=True)
        for name in ("install-lib.ps1", "install-codex-merge.ps1", "install-cursor-merge.ps1"):
            shutil.copyfile(ROOT / "scripts" / name, scripts / name)
        shutil.copytree(ROOT / "scripts/lib", scripts / "lib", ignore=shutil.ignore_patterns("__pycache__"))
        for host in ("codex", "cursor"):
            shutil.copytree(ROOT / "trellis" / host, self.package / "trellis" / host)
        (self.package / "agents").mkdir()
        shutil.copyfile(ROOT / "agents/AGENTS.global.md", self.package / "agents/AGENTS.global.md")
        # Confirm the interactive branch without requiring a GUI in CI. Python
        # still reads actual piped N answers; the hook prompt reads Console.In.
        with (scripts / "install-lib.ps1").open("a", encoding="utf-8") as stream:
            stream.write("\nfunction Test-InstallLibStdinTty { return $true }\n")
        self.home = self.root / "home"
        self.home.mkdir()
        self.project = self.root / "project with space"
        self.project.mkdir()
        (self.project / "AGENTS.md").write_text("project-owned\n", encoding="utf-8")

    def invoke(self, host, answer, *args):
        path = str(self.package / "scripts" / f"install-{host}-merge.ps1").replace("'", "''")
        quoted = " ".join("'" + arg.replace("'", "''") + "'" for arg in args)
        command = (f"[Console]::SetIn([IO.StringReader]::new('{answer}')); "
                   f"& '{path}' --interactive --mcp-overwrite {quoted}; exit $LASTEXITCODE")
        result = subprocess.run([PWSH, "-NoProfile", "-Command", command], input=b"n\nn\n",
                                capture_output=True, timeout=30, cwd=self.package,
                                env={**os.environ, "HOME": str(self.home),
                                     "CODEX_HOME": str(self.home / ".codex")}, check=False)
        return subprocess.CompletedProcess(result.args, result.returncode,
                                           result.stdout.decode("utf-8", errors="replace"),
                                           result.stderr.decode("utf-8", errors="replace"))

    def test_codex_existing_hooks_keep_and_replace_finish_without_unset_variable(self):
        for answer in ("n", "y"):
            with self.subTest(answer=answer):
                codex = self.home / f"codex-{answer}"
                hooks = codex / "hooks"
                hooks.mkdir(parents=True)
                (hooks / "old.txt").write_text("original", encoding="utf-8")
                (codex / "hooks.json").write_text('{"original": true}', encoding="utf-8")
                config = codex / "config.toml"
                config.write_text('[features]\nhooks = true\n'
                                  '[mcp_servers.recallium]\ntype = "http"\nurl = "http://www.59005046.xyz:8102/mcp"\n'
                                  '[mcp_servers.mem0]\ntype = "http"\nurl = "https://www.59005046.xyz:8102/mcp"\n', encoding="utf-8")
                result = self.invoke("codex", answer, "--codex-home", str(codex))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(f"Replace existing Codex user hooks in {codex}?", result.stderr)
                text = config.read_text(encoding="utf-8")
                self.assertIn('url = "http://www.59005046.xyz:8102/mcp"', text)
                self.assertIn('url = "https://www.59005046.xyz:8102/mcp"', text)
                self.assertIn("KEEP: mcp_servers.recallium", result.stdout)
                if answer == "n":
                    self.assertIn("SKIP: existing Codex user hooks preserved", result.stdout)
                    self.assertEqual((hooks / "old.txt").read_text(), "original")
                    self.assertEqual(json.loads((codex / "hooks.json").read_text()), {"original": True})
                else:
                    self.assertFalse((hooks / "old.txt").exists())
                    self.assertTrue((hooks / "session-start.sh").is_file())
                    self.assertIn("hooks", json.loads((codex / "hooks.json").read_text()))

    def test_cursor_existing_hooks_keep_and_replace_finish_without_unset_variable(self):
        for answer in ("n", "y"):
            with self.subTest(answer=answer):
                project = self.root / f"cursor-{answer}"
                hooks = project / ".cursor/hooks"
                hooks.mkdir(parents=True)
                (hooks / "old.txt").write_text("original", encoding="utf-8")
                (project / "AGENTS.md").write_text("project-owned", encoding="utf-8")
                mcp = self.home / f"cursor-{answer}.json"
                mcp.write_text('{"mcpServers": {}}', encoding="utf-8")
                result = self.invoke("cursor", answer, "--project-root", str(project), "--mcp-file", str(mcp))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(f"Replace/update existing Cursor project hooks/rules in {project}?", result.stderr)
                self.assertEqual((project / "AGENTS.md").read_text(), "project-owned")
                if answer == "n":
                    self.assertIn("SKIP: existing project Cursor hooks/rules preserved", result.stdout)
                    self.assertEqual((hooks / "old.txt").read_text(), "original")
                else:
                    self.assertFalse((hooks / "old.txt").exists())
                    self.assertTrue((project / ".cursor/hooks.json").is_file())
                    self.assertTrue((project / ".cursor/rules/ai-workflow-global.mdc").is_file())


if __name__ == "__main__":
    unittest.main()
