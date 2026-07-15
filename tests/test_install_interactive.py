import json
import os
import subprocess
import sys
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

    def test_codex_merge_rejects_remote_http_before_mutating_target(self) -> None:
        codex_home = self.home / ".codex"
        codex_home.mkdir(parents=True)
        config = codex_home / "config.toml"
        original = "[features]\nmemories = true\n"
        config.write_text(original, encoding="utf-8")

        result = self.run_install(
            "codex-merge",
            "--mcp-overwrite",
            "--mem0-url",
            "http://memory.example.test/mcp",
            "--skip-project",
            "--codex-home",
            str(codex_home),
            "--backup-dir",
            str(self.root / "backup"),
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("insecure remote HTTP", result.stderr)
        self.assertEqual(config.read_text(encoding="utf-8"), original)

    def test_cursor_merge_rejects_remote_http_before_mutating_target(self) -> None:
        mcp_file = self.home / ".cursor" / "mcp.json"
        mcp_file.parent.mkdir(parents=True)
        original = '{"mcpServers":{"existing":{"command":"keep"}}}\n'
        mcp_file.write_text(original, encoding="utf-8")

        result = self.run_install(
            "cursor-merge",
            "--mcp-overwrite",
            "--mem0-url",
            "http://memory.example.test/mcp",
            "--mcp-file",
            str(mcp_file),
            "--skip-project",
            "--backup-dir",
            str(self.root / "backup"),
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("insecure remote HTTP", result.stderr)
        self.assertEqual(mcp_file.read_text(encoding="utf-8"), original)

    def test_mcp_merge_allows_loopback_http_for_local_development(self) -> None:
        codex_home = self.home / ".codex"
        codex_home.mkdir(parents=True)
        (codex_home / "config.toml").write_text("", encoding="utf-8")

        for url in (
            "http://localhost:8102/mcp",
            "http://127.0.0.1:8102/mcp",
            "http://[::1]:8102/mcp",
        ):
            with self.subTest(url=url):
                result = self.run_install(
                    "codex-merge",
                    "--mcp-overwrite",
                    "--mem0-url",
                    url,
                    "--skip-project",
                    "--codex-home",
                    str(codex_home),
                    "--backup-dir",
                    str(self.root / "backup"),
                )
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_codex_merge_validates_single_quoted_toml_url(self) -> None:
        fragments = self.root / "fragments"
        fragments.mkdir()
        (fragments / "recallium.toml").write_text(
            "[mcp_servers.recallium]\nurl = 'http://memory.example.test/mcp'\n",
            encoding="utf-8",
        )
        target = self.root / "config.toml"
        original = "[features]\nmemories = true\n"
        target.write_text(original, encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "lib" / "merge_host_mcp.py"),
                "--host",
                "codex",
                "--target",
                str(target),
                "--fragments",
                str(fragments),
                "--policy",
                "overwrite",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("insecure remote HTTP", result.stderr)
        self.assertEqual(target.read_text(encoding="utf-8"), original)

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
            "https://example.test/mem0",
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

    def test_codex_merge_backs_up_dangling_config_symlink(self) -> None:
        codex_home = self.home / ".codex"
        codex_home.mkdir(parents=True)
        config = codex_home / "config.toml"
        missing_target = self.root / "missing-config.toml"
        config.symlink_to(missing_target)
        backup_dir = self.root / "backup"

        result = self.run_install(
            "codex-merge",
            "--mcp-overwrite",
            "--skip-project",
            "--codex-home",
            str(codex_home),
            "--backup-dir",
            str(backup_dir),
        )

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertTrue(config.is_file())
        self.assertFalse(config.is_symlink())
        backups = list(backup_dir.glob("config.toml.*.bak"))
        self.assertEqual(len(backups), 1)
        self.assertTrue(backups[0].is_symlink())
        self.assertEqual(os.readlink(backups[0]), str(missing_target))

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
            "https://example.test/mem0",
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
            "https://example.test/mem0",
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
            "https://example.test/mem0",
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
            "https://example.test/mem0",
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
        original_mcp = '{"mcpServers":{}}'
        mcp_file.write_text(original_mcp, encoding="utf-8")
        cursor_dir = self.project / ".cursor"
        cursor_dir.mkdir()
        (cursor_dir / "hooks.json").write_text("{}", encoding="utf-8")

        result = self.run_install(
            "cursor-merge",
            "--mcp-keep",
            "--mem0-url",
            "https://example.test/mem0",
            "--mcp-file",
            str(mcp_file),
            "--project-root",
            str(self.project),
            "--backup-dir",
            str(self.root / "backup"),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CONFLICT", result.stderr)
        self.assertEqual(mcp_file.read_text(encoding="utf-8"), original_mcp)

    def test_codex_merge_project_conflict_restores_mcp(self) -> None:
        codex_home = self.home / ".codex"
        codex_home.mkdir(parents=True)
        config = codex_home / "config.toml"
        original_config = '[mcp_servers.other]\ncommand = "keep"\n'
        config.write_text(original_config, encoding="utf-8")
        project_codex = self.project / ".codex"
        project_codex.mkdir()
        (project_codex / "hooks.json").write_text("existing\n", encoding="utf-8")

        result = self.run_install(
            "codex-merge",
            "--mcp-overwrite",
            "--codex-home",
            str(codex_home),
            "--project-root",
            str(self.project),
            "--backup-dir",
            str(self.root / "backup"),
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CONFLICT", result.stderr)
        self.assertEqual(config.read_text(encoding="utf-8"), original_config)

    def test_cursor_merge_backs_up_dangling_mcp_symlink(self) -> None:
        cursor_home = self.home / ".cursor"
        cursor_home.mkdir(parents=True)
        mcp_file = cursor_home / "mcp.json"
        missing_target = self.root / "missing-mcp.json"
        mcp_file.symlink_to(missing_target)
        backup_dir = self.root / "backup"

        result = self.run_install(
            "cursor-merge",
            "--mcp-overwrite",
            "--mcp-file",
            str(mcp_file),
            "--skip-project",
            "--backup-dir",
            str(backup_dir),
        )

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertTrue(mcp_file.is_file())
        self.assertFalse(mcp_file.is_symlink())
        backups = list(backup_dir.glob("mcp.json.*.bak"))
        self.assertEqual(len(backups), 1)
        self.assertTrue(backups[0].is_symlink())
        self.assertEqual(os.readlink(backups[0]), str(missing_target))

    def test_cursor_merge_rejects_packaged_mcp_fragment_as_target(self) -> None:
        fragment = ROOT / "trellis" / "cursor" / "mcp" / "servers.json"
        before = fragment.read_text(encoding="utf-8")

        result = self.run_install(
            "cursor-merge",
            "--dry-run",
            "--mcp-file",
            str(fragment),
            "--skip-project",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("package MCP fragment", result.stderr)
        self.assertEqual(fragment.read_text(encoding="utf-8"), before)

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
        project_codex = self.project / ".codex"
        old_hooks = project_codex / "hooks"
        old_hooks.mkdir(parents=True)
        (project_codex / "hooks.json").write_text("old hooks\n", encoding="utf-8")
        (old_hooks / "obsolete.sh").write_text("obsolete\n", encoding="utf-8")
        unrelated = project_codex / "project-owned.txt"
        unrelated.write_text("keep\n", encoding="utf-8")
        backup_dir = self.root / "backup"

        result = self.run_install(
            "codex-merge",
            "--apply",
            "--mcp-overwrite",
            "--mem0-url",
            "https://example.test/mem0",
            "--project-root",
            str(self.project),
            "--codex-home",
            str(codex_home),
            "--backup-dir",
            str(backup_dir),
            "--replace",
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        text = (codex_home / "config.toml").read_text(encoding="utf-8")
        self.assertIn("https://www.59005046.xyz:8102/mcp", text)
        self.assertNotIn("http://old.example/mcp", text)
        self.assertIn("[mcp_servers.other]", text)
        self.assertFalse((codex_home / "hooks.json").exists())
        self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep\n")
        self.assertFalse((old_hooks / "obsolete.sh").exists())
        self.assertEqual(len(list(backup_dir.glob("config.toml.*.bak"))), 1)
        self.assertEqual(len(list(backup_dir.glob("hooks.json.*.bak"))), 1)
        self.assertEqual(
            len([path for path in backup_dir.glob("hooks.*.bak") if path.is_dir()]),
            1,
        )

    def test_cursor_replace_removes_obsolete_hooks_and_preserves_unrelated_files(self) -> None:
        mcp_file = self.home / ".cursor" / "mcp.json"
        mcp_file.parent.mkdir(parents=True)
        mcp_file.write_text('{"mcpServers":{}}', encoding="utf-8")
        cursor_dir = self.project / ".cursor"
        hooks_dir = cursor_dir / "hooks"
        hooks_dir.mkdir(parents=True)
        (cursor_dir / "hooks.json").write_text("old hooks\n", encoding="utf-8")
        rules = cursor_dir / "rules" / "ai-workflow-global.mdc"
        rules.parent.mkdir(parents=True)
        rules.write_text("old rules\n", encoding="utf-8")
        (hooks_dir / "obsolete.py").write_text("obsolete\n", encoding="utf-8")
        unrelated = cursor_dir / "project-owned.txt"
        unrelated.write_text("keep\n", encoding="utf-8")
        backup_dir = self.root / "backup"

        result = self.run_install(
            "cursor-merge",
            "--apply",
            "--mcp-overwrite",
            "--mcp-file",
            str(mcp_file),
            "--project-root",
            str(self.project),
            "--backup-dir",
            str(backup_dir),
            "--replace",
        )

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertFalse((hooks_dir / "obsolete.py").exists())
        self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep\n")
        self.assertEqual(len(list(backup_dir.glob("mcp.json.*.bak"))), 1)
        self.assertEqual(len(list(backup_dir.glob("hooks.json.*.bak"))), 1)
        self.assertEqual(
            len([path for path in backup_dir.glob("hooks.*.bak") if path.is_dir()]),
            1,
        )
        self.assertEqual(
            len(list(backup_dir.glob("ai-workflow-global.mdc.*.bak"))),
            1,
        )

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
            "https://example.test/mem0",
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
            "https://example.test/mem0",
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
