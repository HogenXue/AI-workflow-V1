import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GrillWithDocsTrellisRouteTests(unittest.TestCase):
    def test_global_template_routes_simple_and_complex_trellis_work(self) -> None:
        content = (ROOT / "trellis" / "AGENTS.global.md").read_text(encoding="utf-8")

        markers = (
            "Trellis 是该项目的工作流来源",
            "简单且需求明确的任务：遵循 Trellis 的轻量流程",
            "复杂、跨模块或需求不明确的任务：先使用 `$grill-with-docs`",
            "GitNexus",
            "使用 TDD",
        )
        positions = [content.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("不自动触发 Grill with Docs", content)
        self.assertIn("不得再运行 `trellis-brainstorm`", content)

    def test_global_template_keeps_capability_boundaries_explicit(self) -> None:
        content = (ROOT / "trellis" / "AGENTS.global.md").read_text(encoding="utf-8")

        for phrase in (
            "TDD 是 Trellis 执行阶段的实现方法，不是第二套工作流",
            "Karpathy Guidelines 是横切行为约束，不是独立阶段",
            "GitNexus 只负责影响分析与提交安全，不写业务代码",
            "Release 只负责发布说明、版本记录",
            "Memory 只负责长期记忆与跨会话上下文",
        ):
            self.assertIn(phrase, content)

    def test_project_override_resolves_native_trellis_skill_aliases(self) -> None:
        content = (ROOT / "trellis" / "AGENTS.project.md").read_text(encoding="utf-8")

        for phrase in (
            "$grill-with-docs` 视为 Phase 1.1",
            "不要再加载 `trellis-brainstorm`",
            "项目原生 `trellis-check`",
        ):
            self.assertIn(phrase, content)

    def test_repository_dogfoods_the_codex_phase_override(self) -> None:
        content = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("$grill-with-docs` 视为 Trellis Phase 1.1", content)
        self.assertIn("简单且需求明确的任务直接走 Trellis", content)
        self.assertIn("不要再加载 `trellis-brainstorm`", content)
        self.assertIn("项目原生 `trellis-check`", content)

    def test_skill_replaces_grill_me_without_creating_parallel_artifacts(self) -> None:
        manifest = (ROOT / "manifest.yaml").read_text(encoding="utf-8")
        skill_path = ROOT / "skills" / "grill-with-docs"
        skill = (skill_path / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("  - grill-with-docs", manifest)
        self.assertNotIn("  - grill-me", manifest)
        for capability in (
            "diagnosing-bugs",
            "codebase-design",
            "resolving-merge-conflicts",
        ):
            self.assertIn(f"  - {capability}", manifest)
            self.assertTrue((ROOT / "skills" / capability / "SKILL.md").is_file())
        self.assertFalse((ROOT / "skills" / "grill-me").exists())
        self.assertIn("name: grill-with-docs", skill)
        self.assertIn("Trellis Phase 1.1", skill)
        self.assertIn("Trellis PRD", skill)
        self.assertIn(".trellis/spec/domain/", skill)
        self.assertIn("术语", skill)
        self.assertIn(".trellis/spec/decisions/", skill)
        self.assertIn("难以逆转", skill)
        self.assertNotIn("`CONTEXT.md`", skill)
        self.assertNotIn("`docs/adr/`", skill)
        for forbidden in ("`to-spec`", "`to-tickets`", "`implement`"):
            self.assertNotIn(forbidden, skill)


if __name__ == "__main__":
    unittest.main()
