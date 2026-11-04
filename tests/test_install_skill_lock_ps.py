"""Ownership adoption must preserve independent data on both installer peers."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'scripts/lib/adopt_skill_lock.py'


class SkillLockHelperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        spec = importlib.util.spec_from_file_location('adopt_skill_lock_test', HELPER)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_duplicate_keys_fail_before_lock_mutation(self):
        lock = self.root / '.skill-lock.json'
        raw = b'{"skills":{"independent":{}},"skills":{"tdd":{}}}\n'
        lock.write_bytes(raw)
        with self.assertRaises(ValueError):
            self.module.adopt_skill_lock(lock, ['tdd'], True)
        self.assertEqual(lock.read_bytes(), raw)

    def test_custom_symlink_keeps_caller_adjacent_lock(self):
        home = self.root / 'home'
        standard = home / '.agents/skills'
        standard.mkdir(parents=True)
        custom = self.root / 'custom/skills'
        custom.parent.mkdir()
        try:
            custom.symlink_to(standard, target_is_directory=True)
        except OSError:
            self.skipTest('directory symlinks unavailable')
        env = {**os.environ, 'HOME': str(home), 'USERPROFILE': str(home)}
        env.pop('CODEX_HOME', None)
        env.pop('XDG_STATE_HOME', None)
        run = subprocess.run([sys.executable, str(HELPER), '--resolve-for', str(custom)], env=env, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(Path(run.stdout.strip()), custom.parent / '.skill-lock.json')

    def test_relative_target_retains_verified_logical_cwd(self):
        home = self.root / 'home'
        standard = home / '.agents/skills'
        standard.mkdir(parents=True)
        alias = self.root / 'custom/skills'
        alias.parent.mkdir()
        try:
            alias.symlink_to(standard, target_is_directory=True)
        except OSError:
            self.skipTest('directory symlinks unavailable')
        env = {**os.environ, 'HOME': str(home), 'USERPROFILE': str(home), 'PWD': str(alias)}
        env.pop('XDG_STATE_HOME', None)
        run = subprocess.run([sys.executable, str(HELPER), '--resolve-for', '.'], cwd=alias, env=env, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(Path(run.stdout.strip()), alias.parent / '.skill-lock.json')
        # A stale/mismatched PWD cannot redirect registration elsewhere.
        env['PWD'] = str(self.root)
        run = subprocess.run([sys.executable, str(HELPER), '--resolve-for', '.'], cwd=standard, env=env, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(Path(run.stdout.strip()), home / '.agents/.skill-lock.json')

    def test_apply_does_not_require_unix_fchmod(self):
        lock = self.root / 'lock.json'
        lock.write_text('{"skills":{"tdd":{},"independent":{}},"version":3}')
        # Supported Windows Python 3.10-3.12 lacks this API.
        with mock.patch.object(self.module.os, 'fchmod', create=True, side_effect=AttributeError('not available on Windows')):
            self.module.adopt_skill_lock(lock, ['tdd'], True)
        self.assertEqual(json.loads(lock.read_text()), {'skills': {'independent': {}}, 'version': 3})


class AdoptionContract:
    shell = None

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / 'home'
        self.home.mkdir()
        self.target = self.home / '.agents/skills'
        self.lock = self.home / '.agents/.skill-lock.json'
        self.lock.parent.mkdir()
        self.original = b'{"version":3,"skills":{"tdd":{"source":"upstream"},"independent":{"source":"keep"}},"preferences":{"keep":true}}\n'
        self.lock.write_bytes(self.original)
        self.env = dict(os.environ)
        for name in ['CODEX_HOME','XDG_STATE_HOME','CURSOR_MCP_FILE','CLAUDE_MCP_FILE','MINIMAX_DATA_DIR','MAVIS_DATA_DIR','CODEBUDDY_CONFIG_DIR']:
            self.env.pop(name, None)
        self.env.update(HOME=str(self.home), USERPROFILE=str(self.home))

    def install(self, *args):
        package = getattr(self, 'package', ROOT)
        if self.shell == 'pwsh':
            cmd = [shutil.which('pwsh'), '-NoProfile', '-File', str(package / 'scripts/install-skills.ps1')]
        else:
            cmd = ['bash', str(package / 'scripts/install-skills.sh')]
        return subprocess.run([*cmd, *args, '--target', str(self.target)], cwd=ROOT, env=self.env, capture_output=True, text=True)

    def test_explicit_adoption_preserves_unrelated_data_and_backup(self):
        run = self.install('--copy', '--adopt-skill-lock')
        self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
        expected = json.loads(self.original)
        del expected['skills']['tdd']
        self.assertEqual(json.loads(self.lock.read_bytes()), expected)
        backups = list((self.home / '.agents/.ai-workflow-backups').glob('.skill-lock.json.*.bak'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), self.original)
        self.assertTrue((self.target / 'retro/SKILL.md').exists())

    def test_failed_adoption_restores_payload_and_lock(self):
        self.package = self.root / 'package'
        for name in ['scripts', 'skills']:
            shutil.copytree(ROOT / name, self.package / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        shutil.copy2(ROOT / 'manifest.yaml', self.package / 'manifest.yaml')
        helper = self.package / 'scripts/lib/adopt_skill_lock.py'
        source = helper.read_text()
        needle = '    try:\n        detached = adopt_skill_lock(args.target, args.skills, args.apply)'
        self.assertIn(needle, source)
        source = source.replace(needle, '    if args.apply:\n        args.target.write_text("partial lock")\n        return 1\n' + needle)
        helper.write_text(source)
        old = self.target / 'tdd/SKILL.md'
        old.parent.mkdir(parents=True)
        original = '---\nname: tdd\ndescription: Previous installed TDD.\n---\nKeep old payload.\n'
        old.write_text(original)
        run = self.install('--copy', '--replace', '--adopt-skill-lock')
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('rolling back', run.stderr)
        self.assertEqual(old.read_text(), original)
        self.assertEqual({p.name for p in self.target.iterdir()}, {'tdd'})
        self.assertEqual(self.lock.read_bytes(), self.original)
        self.assertEqual(len(list((self.home / '.agents/.ai-workflow-backups').glob('.skill-lock.json.*.bak'))), 1)

    def test_preview_and_opt_out_preserve_lock_bytes(self):
        for args in [('--dry-run', '--adopt-skill-lock'), ('--copy',)]:
            run = self.install(*args)
            self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
            self.assertEqual(self.lock.read_bytes(), self.original)
            self.assertEqual(list(self.home.rglob('*.bak')), [])

    def test_malformed_lock_blocks_before_skill_writes(self):
        self.lock.write_text('{invalid')
        run = self.install('--copy', '--adopt-skill-lock')
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('skill lock:', run.stderr)
        self.assertFalse(self.target.exists())
        self.assertEqual(self.lock.read_text(), '{invalid')
        self.assertEqual(list(self.home.rglob('*.bak')), [])


@unittest.skipUnless(os.name != 'nt' and shutil.which('bash'), 'Unix Bash required')
class BashAdoptionTests(AdoptionContract, unittest.TestCase):
    shell = 'bash'


@unittest.skipUnless(shutil.which('pwsh'), 'PowerShell 7+ required')
class PowerShellAdoptionTests(AdoptionContract, unittest.TestCase):
    shell = 'pwsh'
