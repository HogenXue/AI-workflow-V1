import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class InteractiveInstallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.project = self.root / "project"
        self.project.mkdir()
        (self.project / "AGENTS.md").write_text("project-owned\n", encoding="utf-8")

    def env(self) -> dict[str, str]:
        return {
            **os.environ,
            "HOME": str(self.home),
            "CODEX_HOME": str(self.home / ".codex"),
        }

    def run_install(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(ROOT / "scripts" / "install.sh"), *args],
            cwd=str(cwd or ROOT),
            text=True,
            capture_output=True,
            check=False,
            env=self.env(),
        )

    def test_no_args_non_tty_exits_2(self) -> None:
        result = subprocess.run(
            ["bash", str(ROOT / "scripts" / "install.sh")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            stdin=subprocess.DEVNULL,
            env=self.env(),
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("interactive", result.stderr.lower() + result.stdout.lower())

    def test_codex_merge_skips_project_with_skip_flag(self) -> None:
        # Avoid cwd=ROOT without skip/project-root: that would write real .codex/.
        codex_home = self.home / ".codex"
        codex_home.mkdir(parents=True)
        (codex_home / "config.toml").write_text("[features]\nmemories = true\n", encoding="utf-8")

        result = self.run_install(
            "codex-merge",
            "--mcp-overwrite",
            "--mem0-url",
            "http://example.test/mem0",
            "--skip-project",
            "--codex-home",
            str(codex_home),
            "--backup-dir",
            str(self.root / "backup"),
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        text = (codex_home / "config.toml").read_text(encoding="utf-8")
        self.assertIn("[mcp_servers.recallium]", text)
        self.assertIn("[mcp_servers.mem0]", text)
        self.assertFalse((self.project / ".codex").exists())
        self.assertIn("skipping project-scoped", result.stdout + result.stderr)

    def test_codex_merge_skips_when_not_in_git_repo(self) -> None:
        orphan = self.root / "orphan"
        orphan.mkdir()
        codex_home = self.home / ".codex"
        codex_home.mkdir(parents=True)
        (codex_home / "config.toml").write_text("", encoding="utf-8")

        result = self.run_install(
            "codex-merge",
            "--mcp-overwrite",
            "--mem0-url",
            "http://example.test/mem0",
            "--codex-home",
            str(codex_home),
            "--backup-dir",
            str(self.root / "backup"),
            cwd=orphan,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("skipping project-scoped", result.stdout + result.stderr)
        self.assertFalse((orphan / ".codex").exists())

    def test_codex_merge_cwd_git_repo_is_not_auto_project_root(self) -> None:
        """Cwd git toplevel alone must not install project hooks (PRD: explicit root)."""
        repo = self.root / "git-repo"
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
        (repo / "AGENTS.md").write_text("owned\n", encoding="utf-8")
        codex_home = self.home / ".codex"
        codex_home.mkdir(parents=True)
        (codex_home / "config.toml").write_text("", encoding="utf-8")

        result = self.run_install(
            "codex-merge",
            "--mcp-overwrite",
            "--mem0-url",
            "http://example.test/mem0",
            "--codex-home",
            str(codex_home),
            "--backup-dir",
            str(self.root / "backup"),
            cwd=repo,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        out = result.stdout + result.stderr
        self.assertIn("SKIP: skipping project-scoped steps", out)
        self.assertIn("no --project-root", out)
        self.assertFalse((repo / ".codex").exists())
        self.assertEqual((repo / "AGENTS.md").read_text(encoding="utf-8"), "owned\n")

    def test_codex_merge_writes_project_hooks_with_explicit_root(self) -> None:
        codex_home = self.home / ".codex"
        codex_home.mkdir(parents=True)
        (codex_home / "config.toml").write_text("", encoding="utf-8")

        result = self.run_install(
            "codex-merge",
            "--mcp-keep",
            "--mem0-url",
            "http://example.test/mem0",
            "--project-root",
            str(self.project),
            "--codex-home",
            str(codex_home),
            "--backup-dir",
            str(self.root / "backup"),
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertTrue((self.project / ".codex" / "hooks.json").is_file())
        self.assertEqual((self.project / "AGENTS.md").read_text(encoding="utf-8"), "project-owned\n")

    def test_cursor_merge_mcp_and_project_rules(self) -> None:
        mcp_file = self.home / ".cursor" / "mcp.json"
        mcp_file.parent.mkdir(parents=True)
        mcp_file.write_text(
            json.dumps({"mcpServers": {"recallium": {"url": "http://old", "transport": "http"}}}),
            encoding="utf-8",
        )

        keep = self.run_install(
            "cursor-merge",
            "--mcp-keep",
            "--mem0-url",
            "http://example.test/mem0",
            "--mcp-file",
            str(mcp_file),
            "--project-root",
            str(self.project),
            "--backup-dir",
            str(self.root / "backup"),
        )
        self.assertEqual(keep.returncode, 0, keep.stderr + keep.stdout)
        data = json.loads(mcp_file.read_text(encoding="utf-8"))
        self.assertEqual(data["mcpServers"]["recallium"]["url"], "http://old")
        self.assertIn("gitnexus", data["mcpServers"])
        self.assertIn("mem0", data["mcpServers"])
        rules = self.project / ".cursor" / "rules" / "ai-workflow-global.mdc"
        self.assertTrue(rules.is_file())
        rules_text = rules.read_text(encoding="utf-8")
        agents_body = (ROOT / "trellis" / "AGENTS.global.md").read_text(encoding="utf-8")
        self.assertTrue(rules_text.startswith("---\n"))
        self.assertIn("alwaysApply: true", rules_text)
        # Body after frontmatter must match AGENTS.global.md (dynamic generation).
        _, _, body = rules_text.split("---", 2)
        self.assertEqual(
            body.lstrip("\n").rstrip("\n"),
            agents_body.rstrip("\n"),
        )
        self.assertTrue((self.project / ".cursor" / "hooks.json").is_file())
        self.assertEqual((self.project / "AGENTS.md").read_text(encoding="utf-8"), "project-owned\n")

    def test_cursor_merge_conflict_without_replace(self) -> None:
        mcp_file = self.home / ".cursor" / "mcp.json"
        mcp_file.parent.mkdir(parents=True)
        mcp_file.write_text('{"mcpServers":{}}', encoding="utf-8")
        cursor_dir = self.project / ".cursor"
        cursor_dir.mkdir()
        (cursor_dir / "hooks.json").write_text("{}", encoding="utf-8")

        result = self.run_install(
            "cursor-merge",
            "--mcp-keep",
            "--mem0-url",
            "http://example.test/mem0",
            "--mcp-file",
            str(mcp_file),
            "--project-root",
            str(self.project),
            "--backup-dir",
            str(self.root / "backup"),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CONFLICT", result.stderr)

    def test_existing_skills_cli_still_works(self) -> None:
        target = self.root / "skills"
        result = self.run_install("skills", "--dry-run", "--target", str(target))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("DRY-RUN", result.stdout)

    def test_codex_merge_mcp_overwrite_and_no_global_hooks(self) -> None:
        codex_home = self.home / ".codex"
        codex_home.mkdir(parents=True)
        (codex_home / "config.toml").write_text(
            '[mcp_servers.recallium]\ntype = "http"\nurl = "http://old.example/mcp"\n\n'
            '[mcp_servers.other]\ncommand = "keep-me"\n',
            encoding="utf-8",
        )

        result = self.run_install(
            "codex-merge",
            "--apply",
            "--mcp-overwrite",
            "--mem0-url",
            "http://example.test/mem0",
            "--project-root",
            str(self.project),
            "--codex-home",
            str(codex_home),
            "--backup-dir",
            str(self.root / "backup"),
            "--replace",
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        text = (codex_home / "config.toml").read_text(encoding="utf-8")
        self.assertIn("http://www.59005046.xyz:8102/mcp", text)
        self.assertNotIn("http://old.example/mcp", text)
        self.assertIn("[mcp_servers.other]", text)
        self.assertFalse((codex_home / "hooks.json").exists())

    def test_cursor_profile_does_not_write_codex_home(self) -> None:
        sentinel = self.home / ".codex" / "sentinel"
        sentinel.parent.mkdir(parents=True)
        sentinel.write_text("keep", encoding="utf-8")
        mcp_file = self.home / ".cursor" / "mcp.json"
        mcp_file.parent.mkdir(parents=True)
        mcp_file.write_text('{"mcpServers":{}}', encoding="utf-8")

        result = self.run_install(
            "cursor-merge",
            "--apply",
            "--mcp-overwrite",
            "--mem0-url",
            "http://example.test/mem0",
            "--mcp-file",
            str(mcp_file),
            "--project-root",
            str(self.project),
            "--backup-dir",
            str(self.root / "backup"),
            "--replace",
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")
        self.assertFalse((self.project / ".codex").exists())
        self.assertEqual((self.project / "AGENTS.md").read_text(encoding="utf-8"), "project-owned\n")

    def test_repo_root_agents_md_untouched_by_cursor_merge(self) -> None:
        agents = ROOT / "AGENTS.md"
        before = agents.read_text(encoding="utf-8") if agents.is_file() else None
        mcp_file = self.home / ".cursor" / "mcp.json"
        mcp_file.parent.mkdir(parents=True)
        mcp_file.write_text('{"mcpServers":{}}', encoding="utf-8")

        result = self.run_install(
            "cursor-merge",
            "--mcp-overwrite",
            "--mem0-url",
            "http://example.test/mem0",
            "--mcp-file",
            str(mcp_file),
            "--project-root",
            str(self.project),
            "--backup-dir",
            str(self.root / "backup"),
            "--replace",
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        if before is not None:
            self.assertEqual(agents.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
