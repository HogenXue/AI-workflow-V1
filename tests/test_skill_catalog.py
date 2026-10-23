"""Exercise Skill identities and discovery collisions, not just folder names."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts/lib/skill_catalog.py"


class SkillCatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)

    def skill(self, path, name="code-review", body="Review a defined diff."):
        path.mkdir(parents=True, exist_ok=True)
        (path / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Review changes.\n---\n{body}\n")
        return path

    def run_helper(self, *args):
        return subprocess.run([sys.executable, str(HELPER), *args], text=True, capture_output=True)

    def test_invalid_catalog_rejected_before_install(self):
        for entries in (["code-review", "code-review"], ["../escape"], ["UpperCase"], []):
            with self.subTest(entries=entries):
                root = self.home / "package"
                self.skill(root / "skills/code-review")
                (root / "manifest.yaml").write_text(json.dumps({"skills": entries, "default_install_mode": "copy"}))
                run = self.run_helper("catalog", "--root", str(root))
                self.assertNotEqual(run.returncode, 0, run.stdout)
                self.assertIn("ERROR:", run.stderr)

    def test_alias_identity_blocks_installer_without_mutation(self):
        target = self.home / "skills"
        alias = self.skill(target / "old-review")
        original = (alias / "SKILL.md").read_bytes()
        run = subprocess.run(["bash", str(ROOT / "scripts/install-skills.sh"), "--copy", "--replace", "--target", str(target)], text=True, capture_output=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("old-review", run.stderr)
        self.assertEqual((alias / "SKILL.md").read_bytes(), original)
        self.assertFalse((target / "memory").exists())
        self.assertFalse((self.home / ".ai-workflow-backups").exists())

    def test_nested_archive_and_legacy_alias_are_detected(self):
        target = self.home / ".agents/skills"
        other = self.home / ".codex/skills"
        self.skill(target / ".old-backup/review")
        self.skill(other / "review-alias")
        run = self.run_helper("preflight", "--root", str(ROOT), "--target", str(target), "--other-root", str(other))
        self.assertNotEqual(run.returncode, 0)
        self.assertIn(".old-backup", run.stderr)
        self.assertIn("review-alias", run.stderr)

    def test_host_discovery_distinguishes_copies_from_conflicts(self):
        self.skill(self.home / ".agents/skills/code-review")
        self.skill(self.home / ".cursor/skills/code-review")
        args = ("audit", "--root", str(ROOT), "--home", str(self.home), "--host", "cursor", "--json")
        run = self.run_helper(*args)
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result["conflicts"], [])
        self.assertEqual(len(result["equivalent_copies"]), 1)
        self.skill(self.home / ".claude/skills/renamed", body="Always fix and commit everything.")
        run = self.run_helper(*args)
        self.assertNotEqual(run.returncode, 0)
        self.assertEqual(json.loads(run.stdout)["conflicts"][0]["name"], "code-review")

    def test_symlink_cycles_do_not_hide_a_managed_alias(self):
        target = self.home / "skills"
        source = self.skill(target / "code-review")
        try:
            (target / "alias").symlink_to(source, target_is_directory=True)
            (source / "loop").symlink_to(target, target_is_directory=True)
        except OSError:
            self.skipTest("symlinks unavailable")
        run = self.run_helper("preflight", "--root", str(ROOT), "--target", str(target))
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("alias", run.stderr)

    def test_other_root_pruning_does_not_remove_independent_skills(self):
        other = self.home / ".codex/skills"
        independent = self.skill(other / "release", "release", "Independent release capability.")
        self.skill(other / "code-review")
        target = self.home / ".agents/skills"
        run = subprocess.run(["bash", str(ROOT / "scripts/install-skills.sh"), "--copy", "--replace", "--prune-other-root", "--target", str(target)], text=True, capture_output=True, env={**os.environ, "HOME": str(self.home), "CODEX_HOME": str(self.home / ".codex")})
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertTrue((independent / "SKILL.md").exists())
        self.assertFalse((other / "code-review").exists())

    def test_malformed_parent_skill_does_not_hide_nested_managed_alias(self):
        target = self.home / ".agents/skills"
        self.skill(target / "code-review")
        wrapper = target / "historical-container"
        wrapper.mkdir()
        (wrapper / "SKILL.md").write_text("old malformed Skill document\n")
        alias = self.skill(wrapper / "old-review", body="Conflicting nested instructions.")
        before = (alias / "SKILL.md").read_bytes()
        preflight = self.run_helper("preflight", "--target", str(target))
        self.assertNotEqual(preflight.returncode, 0, preflight.stdout)
        self.assertIn(str(alias), preflight.stderr)
        audit = self.run_helper("audit", "--home", str(self.home), "--host", "codex", "--json")
        self.assertNotEqual(audit.returncode, 0, audit.stdout)
        data = json.loads(audit.stdout)
        self.assertEqual(data["conflicts"][0]["name"], "code-review")
        self.assertIn(str(alias), data["conflicts"][0]["paths"])
        self.assertTrue(data["metadata_errors"])
        self.assertEqual((alias / "SKILL.md").read_bytes(), before)

    def test_other_root_prune_requires_matching_declared_identity_before_any_write(self):
        for content in (None, "malformed old document\n",
                        "---\nname: independent-report\ndescription: Keep this useful capability.\n---\nUser content\n"):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as temp:
                home = Path(temp)
                other = home / ".codex/skills"
                candidate = other / "code-review"
                candidate.mkdir(parents=True)
                sentinel = candidate / "personal.txt"
                sentinel.write_text("keep exact private contents\n")
                if content is not None:
                    (candidate / "SKILL.md").write_text(content)
                target = home / ".agents/skills"
                env = {**os.environ, "HOME": str(home), "CODEX_HOME": str(home / ".codex")}
                result = subprocess.run(["bash", str(ROOT / "scripts/install-skills.sh"), "--copy", "--replace", "--prune-other-root", "--target", str(target)], text=True, capture_output=True, env=env)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("refusing to prune", result.stderr)
                self.assertEqual(sentinel.read_text(), "keep exact private contents\n")
                if content is not None:
                    self.assertEqual((candidate / "SKILL.md").read_text(), content)
                self.assertFalse(target.exists())
                self.assertEqual(list(home.rglob("*.bak")), [])


    def test_replace_requires_valid_matching_identity_before_any_write(self):
        cases = (None, "malformed old document\n",
                 "---\nname: code-review\n---\nMissing description.\n",
                 "---\nname: independent-report\ndescription: Independent useful capability.\n---\nKeep.\n")
        for content in cases:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as temp:
                home = Path(temp)
                target = home / "skills"
                independent = target / "code-review"
                independent.mkdir(parents=True)
                sentinel = independent / "personal.txt"
                sentinel.write_text("keep exact private contents\n")
                if content is not None:
                    (independent / "SKILL.md").write_text(content)
                for mode in ("--dry-run", "--copy"):
                    result = subprocess.run(["bash", str(ROOT / "scripts/install-skills.sh"), mode, "--replace", "--target", str(target)], text=True, capture_output=True)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn("refusing to replace", result.stderr)
                    self.assertEqual(sentinel.read_text(), "keep exact private contents\n")
                    if content is not None:
                        self.assertEqual((independent / "SKILL.md").read_text(), content)
                    self.assertFalse((target / "memory").exists())
                    self.assertEqual(list(home.rglob("*.bak")), [])


if __name__ == "__main__":
    unittest.main()
