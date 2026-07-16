import contextlib
import io
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_validator(path: Path):
    spec = importlib.util.spec_from_file_location("validator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_complete_skill(root: Path, name: str) -> Path:
    skill = root / name
    for directory in ("agents", "references", "templates", "examples", "scripts"):
        (skill / directory).mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: test skill\n---\n[ref](references/guide.md)\n",
        encoding="utf-8",
    )
    (skill / "agents" / "openai.yaml").write_text(
        "interface:\n"
        "  display_name: \"Test\"\n"
        "  short_description: \"Test skill description for validation.\"\n"
        f"  default_prompt: \"Use ${name} for this test.\"\n",
        encoding="utf-8",
    )
    (skill / "references" / "guide.md").write_text("guide\n", encoding="utf-8")
    (skill / "templates" / "report.md").write_text("# Report\n", encoding="utf-8")
    (skill / "examples" / "example.md").write_text("# Example\n", encoding="utf-8")
    (skill / "scripts" / "check.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    return skill


class ValidateAllSkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.validator = load_validator(ROOT / "scripts" / "validate-all-skills.py")

    def test_complete_skill_has_no_errors(self) -> None:
        skill = create_complete_skill(self.root, "sample")

        self.assertEqual(self.validator.validate_skill(skill), [])

    def test_optional_resource_directories_may_be_absent(self) -> None:
        skill = create_complete_skill(self.root, "sample")
        (skill / "SKILL.md").write_text(
            "---\nname: sample\ndescription: test skill\n---\n",
            encoding="utf-8",
        )
        for directory, filename in (
            ("references", "guide.md"),
            ("templates", "report.md"),
            ("examples", "example.md"),
            ("scripts", "check.sh"),
        ):
            (skill / directory / filename).unlink()
            (skill / directory).rmdir()

        errors = self.validator.validate_skill(skill)

        self.assertEqual(errors, [])

    def test_invalid_frontmatter_yaml_is_reported(self) -> None:
        skill = create_complete_skill(self.root, "sample")
        (skill / "SKILL.md").write_text(
            "---\nname: sample: broken\ndescription: test skill\n---\n",
            encoding="utf-8",
        )

        _, error_text = self.validator.load_skill_metadata(skill / "SKILL.md")

        self.assertIn("invalid YAML", error_text)

    def test_broken_relative_link_is_reported(self) -> None:
        skill = create_complete_skill(self.root, "sample")
        (skill / "SKILL.md").write_text(
            "---\nname: sample\ndescription: sample code\n---\n"
            "[missing](references/nope.md)\n",
            encoding="utf-8",
        )

        errors = self.validator.validate_skill(skill)

        self.assertIn("broken relative reference: references/nope.md", errors)

    def test_invalid_configuration_yaml_is_reported(self) -> None:
        config = self.root / "defaults.yaml"
        config.write_text("language: zh-CN: broken\n", encoding="utf-8")

        errors = self.validator.validate_config(config)

        self.assertIn("invalid YAML", errors)

    def test_configuration_unknown_key_is_reported_against_schema(self) -> None:
        config = self.root / "hogen-codex.yaml"
        schema = self.root / "project-config.schema.yaml"
        config.write_text("tools:\n  unexpected: true\n", encoding="utf-8")
        schema.write_text(
            "type: mapping\nallowed_keys:\n  tools:\n    type: mapping\n    allowed_keys: {}\n",
            encoding="utf-8",
        )

        errors = self.validator.validate_config(config, schema)

        self.assertIn("unknown configuration key: tools.unexpected", errors)

    def test_configuration_type_mismatch_is_reported_against_schema(self) -> None:
        config = self.root / "hogen-codex.yaml"
        schema = self.root / "project-config.schema.yaml"
        config.write_text('change_policy:\n  minimal_change: "yes"\n', encoding="utf-8")
        schema.write_text(
            "type: mapping\nallowed_keys:\n  change_policy:\n    type: mapping\n    allowed_keys:\n      minimal_change:\n        type: boolean\n",
            encoding="utf-8",
        )

        errors = self.validator.validate_config(config, schema)

        self.assertIn(
            "configuration change_policy.minimal_change must be a boolean", errors
        )

    def test_existing_empty_optional_resource_directory_is_allowed(self) -> None:
        skill = create_complete_skill(self.root, "sample")
        (skill / "templates" / "report.md").unlink()

        errors = self.validator.validate_skill(skill)

        self.assertEqual(errors, [])

    def test_example_todo_placeholder_is_reported(self) -> None:
        skill = create_complete_skill(self.root, "sample")
        (skill / "examples" / "example.md").write_text("# TODO: fill this in\n", encoding="utf-8")

        errors = self.validator.validate_skill(skill)

        self.assertIn("placeholder in example: examples/example.md", errors)

    def test_agent_default_prompt_must_reference_its_skill(self) -> None:
        skill = create_complete_skill(self.root, "sample")
        (skill / "agents" / "openai.yaml").write_text(
            "interface:\n"
            "  display_name: \"Test\"\n"
            "  short_description: \"Test skill\"\n"
            "  default_prompt: \"Use $debugging for this test.\"\n",
            encoding="utf-8",
        )

        errors = self.validator.validate_skill(skill)

        self.assertIn("agent default_prompt must reference $sample", errors)

    def test_agent_default_prompt_requires_an_exact_skill_reference(self) -> None:
        skill = create_complete_skill(self.root, "sample")
        (skill / "agents" / "openai.yaml").write_text(
            "interface:\n"
            "  display_name: \"Test\"\n"
            "  short_description: \"Test skill\"\n"
            "  default_prompt: \"Use $sampling for this test.\"\n",
            encoding="utf-8",
        )

        errors = self.validator.validate_skill(skill)

        self.assertIn("agent default_prompt must reference $sample", errors)

    def test_agent_interface_requires_nonempty_metadata_fields(self) -> None:
        skill = create_complete_skill(self.root, "sample")
        (skill / "agents" / "openai.yaml").write_text(
            "interface:\n  display_name: \"\"\n",
            encoding="utf-8",
        )

        errors = self.validator.validate_skill(skill)

        self.assertIn("agent interface display_name must be a non-empty string", errors)
        self.assertIn("agent interface short_description must be a non-empty string", errors)
        self.assertIn("agent interface default_prompt must be a non-empty string", errors)

    def test_agent_short_description_must_be_25_to_64_characters(self) -> None:
        skill = create_complete_skill(self.root, "sample")
        agent_file = skill / "agents" / "openai.yaml"
        agent_file.write_text(
            "interface:\n"
            "  display_name: \"Test\"\n"
            "  short_description: \"Too short\"\n"
            "  default_prompt: \"Use $sample for this test.\"\n",
            encoding="utf-8",
        )

        errors = self.validator.validate_skill(skill)

        self.assertIn("agent short_description must contain 25 to 64 characters", errors)

        agent_file.write_text(
            "interface:\n"
            "  display_name: \"Test\"\n"
            f"  short_description: \"{'x' * 65}\"\n"
            "  default_prompt: \"Use $sample for this test.\"\n",
            encoding="utf-8",
        )

        errors = self.validator.validate_skill(skill)

        self.assertIn("agent short_description must contain 25 to 64 characters", errors)

    def test_agent_interface_metadata_must_use_quoted_scalars(self) -> None:
        skill = create_complete_skill(self.root, "sample")
        (skill / "agents" / "openai.yaml").write_text(
            "interface:\n"
            "  display_name: Test\n"
            "  short_description: \"Test skill\"\n"
            "  default_prompt: \"Use $sample for this test.\"\n",
            encoding="utf-8",
        )

        errors = self.validator.validate_skill(skill)

        self.assertIn(
            "agent interface display_name must use a double-quoted scalar", errors
        )

    def test_main_validates_project_override_against_schema(self) -> None:
        (self.root / "manifest.yaml").write_text("skills: []\n", encoding="utf-8")
        config_dir = self.root / "config"
        config_dir.mkdir()
        (config_dir / "defaults.yaml").write_text("language: zh-CN\n", encoding="utf-8")
        (config_dir / "project-config.schema.yaml").write_text(
            "type: mapping\nallowed_keys:\n  language:\n    type: string\n",
            encoding="utf-8",
        )
        (self.root / "hogen-codex.yaml").write_text("unknown: true\n", encoding="utf-8")
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            status = self.validator.main(["--root", str(self.root)])

        self.assertEqual(status, 1)
        self.assertIn("hogen-codex.yaml: unknown configuration key: unknown", output.getvalue())

    def test_main_validates_configuration_consumer_registry(self) -> None:
        (self.root / "manifest.yaml").write_text("skills: []\n", encoding="utf-8")
        config_dir = self.root / "config"
        config_dir.mkdir()
        (config_dir / "defaults.yaml").write_text("language: zh-CN\n", encoding="utf-8")
        (config_dir / "project-config.schema.yaml").write_text(
            "type: mapping\nallowed_keys:\n  language:\n    type: string\n",
            encoding="utf-8",
        )
        (config_dir / "consumers.yaml").write_text("consumers: {}\n", encoding="utf-8")
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            status = self.validator.main(["--root", str(self.root)])

        self.assertEqual(status, 1)
        self.assertIn("missing configuration consumer: language", output.getvalue())

    def test_external_project_root_merges_nested_override_with_package_defaults(self) -> None:
        package_root = self.root / "package"
        project_root = self.root / "project"
        package_root.mkdir()
        project_root.mkdir()
        (package_root / "manifest.yaml").write_text("skills: []\n", encoding="utf-8")
        config_dir = package_root / "config"
        config_dir.mkdir()
        (config_dir / "defaults.yaml").write_text(
            "change_policy:\n"
            "  minimal_change: true\n"
            "  preserve_dirty_worktree: true\n"
            "tools:\n"
            "  missing_tool_policy: report-and-degrade\n",
            encoding="utf-8",
        )
        (config_dir / "project-config.schema.yaml").write_text(
            "type: mapping\n"
            "allowed_keys:\n"
            "  change_policy:\n"
            "    type: mapping\n"
            "    allowed_keys:\n"
            "      minimal_change:\n"
            "        type: boolean\n"
            "      preserve_dirty_worktree:\n"
            "        type: boolean\n"
            "  tools:\n"
            "    type: mapping\n"
            "    allowed_keys:\n"
            "      missing_tool_policy:\n"
            "        type: string\n",
            encoding="utf-8",
        )
        (config_dir / "consumers.yaml").write_text(
            "consumers:\n"
            "  change_policy.minimal_change: [karpathy-guidelines-zh]\n"
            "  change_policy.preserve_dirty_worktree: [karpathy-guidelines-zh]\n"
            "  tools.missing_tool_policy: [memory]\n",
            encoding="utf-8",
        )
        (project_root / "hogen-codex.yaml").write_text(
            "change_policy:\n  minimal_change: false\n",
            encoding="utf-8",
        )

        config, errors = self.validator.load_effective_config(package_root, project_root)

        self.assertEqual(errors, [])
        self.assertEqual(
            config,
            {
                "change_policy": {
                    "minimal_change": False,
                    "preserve_dirty_worktree": True,
                },
                "tools": {"missing_tool_policy": "report-and-degrade"},
            },
        )
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "validate-all-skills.py"),
                "--root",
                str(package_root),
                "--project-root",
                str(project_root),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_external_project_root_reports_unknown_nested_override_key(self) -> None:
        package_root = self.root / "package"
        project_root = self.root / "project"
        package_root.mkdir()
        project_root.mkdir()
        (package_root / "manifest.yaml").write_text("skills: []\n", encoding="utf-8")
        config_dir = package_root / "config"
        config_dir.mkdir()
        (config_dir / "defaults.yaml").write_text("tools: {}\n", encoding="utf-8")
        (config_dir / "project-config.schema.yaml").write_text(
            "type: mapping\n"
            "allowed_keys:\n"
            "  tools:\n"
            "    type: mapping\n"
            "    allowed_keys:\n"
            "      missing_tool_policy:\n"
            "        type: string\n",
            encoding="utf-8",
        )
        override = project_root / "hogen-codex.yaml"
        override.write_text("tools:\n  unexpected: true\n", encoding="utf-8")
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            status = self.validator.main(
                [
                    "--root",
                    str(package_root),
                    "--project-root",
                    str(project_root),
                ]
            )

        self.assertEqual(status, 1)
        self.assertIn(
            f"{override}: unknown configuration key: tools.unexpected",
            output.getvalue(),
        )

    def test_missing_pyyaml_has_actionable_message(self) -> None:
        result = subprocess.run(
            [sys.executable, "-S", str(ROOT / "scripts" / "validate-all-skills.py")],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("PyYAML is required", result.stderr)
        self.assertIn("pip install -r requirements-dev.txt", result.stderr)


class ManifestTests(unittest.TestCase):
    def test_manifest_lists_standard_skill_names(self) -> None:
        metadata = yaml.safe_load((ROOT / "manifest.yaml").read_text(encoding="utf-8"))

        self.assertEqual(
            metadata["skills"],
            [
                "memory",
                "gitnexus",
                "release",
                "karpathy-guidelines-zh",
                "grill-with-docs",
                "tdd",
                "diagnosing-bugs",
                "codebase-design",
                "resolving-merge-conflicts",
            ],
        )

    def test_ci_uses_the_shared_quality_entry_on_linux_and_macos(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

        self.assertIn("ubuntu-latest", workflow)
        self.assertIn("macos-latest", workflow)
        self.assertIn("config/workflow_check.py", workflow)
        self.assertIn("quality", workflow)

    def test_readme_describes_packaged_mcp_and_runtime_truthfully(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertNotIn("CodexTamplate", readme)
        self.assertNotIn("本包**不包含** MCP", readme)
        self.assertIn("https://www.59005046.xyz:8102/mcp", readme)
        self.assertIn("config/effective_config.py", readme)
        self.assertIn("config/workflow_check.py", readme)
        self.assertTrue((ROOT / "CHANGELOG.md").is_file())
        self.assertTrue((ROOT / "THIRD_PARTY_NOTICES.md").is_file())


class BundledSkillContractTests(unittest.TestCase):
    EXPECTED_METADATA = {
        "memory": {
            "name": "memory",
            "description": (
                "Retrieve and record durable project context, decisions, learned "
                "constraints, and completed outcomes. Use for prior-work questions, "
                "architecture decisions, handoffs, and preserving important conclusions."
            ),
        },
        "gitnexus": {
            "name": "gitnexus",
            "description": (
                "Analyze high-risk code impact, worktrees, and commit scope when graph "
                "evidence is needed."
            ),
        },
        "release": {
            "name": "release",
            "description": (
                "Plan, verify, execute, and report releases with versioning, change notes, "
                "rollback readiness, and post-release checks. Use for release preparation, "
                "deployment, rollout, rollback, or release-status verification."
            ),
        },
        "karpathy-guidelines-zh": {
            "name": "karpathy-guidelines-zh",
            "description": (
                "Apply Karpathy-inspired guardrails as cross-cutting behavior for coding, "
                "review, refactor, and multi-step agent work. Use to reduce silent assumptions, "
                "over-engineering, unrelated edits, weak tests, context drift, and hidden failures."
            ),
        },
        "grill-with-docs": {
            "name": "grill-with-docs",
            "description": (
                "Clarify complex, cross-module, or unclear requirements through a "
                "repository-aware, one-question-at-a-time interview while maintaining Trellis "
                "domain and decision specs. Use as the sole Codex interviewer for Trellis "
                "Phase 1.1; do not combine it with trellis-brainstorm or create a second "
                "spec/task workflow."
            ),
        },
        "tdd": {
            "name": "tdd",
            "description": (
                "Drive feature and bug-fix implementation with a verified "
                "red-green-refactor cycle. Use before writing production code "
                "when behavior changes need automated tests."
            ),
        },
        "diagnosing-bugs": {
            "name": "diagnosing-bugs",
            "description": (
                "Diagnosis loop for hard bugs and performance regressions. Use when the user "
                'says "diagnose"/"debug this", or reports something '
                "broken/throwing/failing/slow."
            ),
        },
        "codebase-design": {
            "name": "codebase-design",
            "description": (
                "Shared vocabulary for designing deep modules. Use when the user wants to "
                "design or improve a module's interface, find deepening opportunities, decide "
                "where a seam goes, make code more testable or AI-navigable, or when another "
                "skill needs the deep-module vocabulary."
            ),
        },
        "resolving-merge-conflicts": {
            "name": "resolving-merge-conflicts",
            "description": (
                "Resolve an already in-progress Git merge or rebase conflict by tracing both "
                "sides to their primary intent and verifying the combined result. Use when the "
                "user explicitly asks to resolve current merge/rebase conflicts; do not start, "
                "abort, commit, continue, or push the Git operation without matching authorization."
            ),
        },
    }

    def test_standard_skill_package_contracts(self) -> None:
        for name, expected_metadata in self.EXPECTED_METADATA.items():
            with self.subTest(skill=name):
                skill = ROOT / "skills" / name
                self.assertTrue((skill / "SKILL.md").is_file())
                self.assertTrue((skill / "agents" / "openai.yaml").is_file())
                self.assertEqual(
                    yaml.safe_load((skill / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[1]),
                    expected_metadata,
                )
                agent = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
                self.assertIn(f"${name}", agent["interface"]["default_prompt"])
                short_description = agent["interface"]["short_description"]
                self.assertGreaterEqual(len(short_description), 25)
                self.assertLessEqual(len(short_description), 64)

    def test_release_workflow_covers_configuration_and_fallbacks(self) -> None:
        content = (ROOT / "skills" / "release" / "SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "config/defaults.yaml",
            "hogen-codex.yaml",
            "默认配置不存在时",
            "发布工具不可用时",
            "不重复 Trellis 的代码质量检查",
        ):
            self.assertIn(phrase, content)

    def test_gitnexus_honors_the_project_impact_analysis_policy(self) -> None:
        content = (ROOT / "skills" / "gitnexus" / "SKILL.md").read_text(encoding="utf-8")

        for phrase in (
            "require_impact_analysis_before_symbol_edit",
            "为 `true`",
            "为 `false`",
            "默认配置不存在时",
            "提交前",
            "`detect_changes` 仅在",
            "低风险",
        ):
            self.assertIn(phrase, content)

    def test_memory_can_run_without_the_optional_default_config_install(self) -> None:
        content = (ROOT / "skills" / "memory" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("默认配置不存在时", content)
        self.assertIn("继续执行", content)

    def test_memory_recallium_reference_uses_the_secure_production_url(self) -> None:
        content = (
            ROOT / "skills" / "memory" / "references" / "memory-backends.md"
        ).read_text(encoding="utf-8")

        self.assertIn("https://www.59005046.xyz:8102/mcp", content)
        self.assertNotIn("http://www.59005046.xyz:8102/mcp", content)

    def test_runtime_config_consumers_prefer_the_effective_config_helper(self) -> None:
        for name in ("memory", "gitnexus", "release"):
            with self.subTest(skill=name):
                content = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("config/effective_config.py", content)
                self.assertIn("--project-root", content)

    def test_agents_templates_route_to_the_shared_workflow_checker(self) -> None:
        for relative in ("trellis/AGENTS.global.md", "trellis/AGENTS.project.md"):
            with self.subTest(file=relative):
                content = (ROOT / relative).read_text(encoding="utf-8")
                for phrase in (
                    "config/workflow_check.py",
                    "readiness",
                    "quality",
                    "completion",
                    "不替代 Trellis",
                ):
                    self.assertIn(phrase, content)

    def test_release_template_uses_fixed_evidence_gates(self) -> None:
        content = (ROOT / "skills" / "release" / "templates/release-checklist.md").read_text(
            encoding="utf-8"
        )
        for heading in (
            "Scope",
            "Pre-release checks",
            "Rollback",
            "Execution record",
            "Post-release checks",
            "Outstanding risks",
        ):
            self.assertIn(f"## {heading}", content)

    def test_grill_with_docs_enables_implicit_invocation_and_trellis_handoff(self) -> None:
        skill = ROOT / "skills" / "grill-with-docs"
        content = (skill / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = yaml.safe_load(content.split("---", 2)[1])
        agent = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))

        self.assertEqual(frontmatter["name"], "grill-with-docs")
        self.assertNotIn("disable-model-invocation", frontmatter)
        self.assertIs(agent["policy"]["allow_implicit_invocation"], True)
        for phrase in (
            "复杂",
            "跨模块",
            "简单且需求完整的任务直接使用 Trellis",
            "Trellis task",
            "Trellis PRD",
            "Phase 1.1",
            "trellis-brainstorm",
            ".trellis/spec/domain/",
            ".trellis/spec/decisions/",
        ):
            self.assertIn(phrase, content)

    def test_selected_matt_capabilities_stay_inside_trellis_and_git_boundaries(self) -> None:
        expected = {
            "diagnosing-bugs": (
                "A request to diagnose authorizes investigation, not a fix",
                "trellis-check",
                "Do not commit, push",
            ),
            "codebase-design": (
                "does not create a second Design, Spec, task, or implementation workflow",
                "GitNexus impact analysis",
                "local `$tdd` skill",
            ),
            "resolving-merge-conflicts": (
                "does not by itself authorize",
                "Do not invent new behavior",
                "only when the user explicitly authorized",
            ),
        }

        for name, phrases in expected.items():
            with self.subTest(skill=name):
                content = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                for phrase in phrases:
                    self.assertIn(phrase, content)

    def test_tdd_skill_defines_red_green_refactor_and_trellis_boundary(self) -> None:
        content = (ROOT / "skills" / "tdd" / "SKILL.md").read_text(encoding="utf-8")

        for phrase in (
            "RED",
            "GREEN",
            "REFACTOR",
            "若项目存在 `.trellis/`",
            "不存在 `.trellis/`",
            "trellis-check",
            "GitNexus",
        ):
            self.assertIn(phrase, content)

    def test_karpathy_guidelines_are_cross_cutting_not_a_duplicate_stage(self) -> None:
        content = (ROOT / "skills" / "karpathy-guidelines-zh" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        for phrase in ("横切行为约束", "不创建独立阶段", "TDD", "Trellis"):
            self.assertIn(phrase, content)
