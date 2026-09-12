import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GrillWithDocsTrellisRouteTests(unittest.TestCase):
    def test_global_template_routes_simple_and_complex_trellis_work(self) -> None:
        content = (ROOT / "AGENTS.global.md").read_text(encoding="utf-8")

        for phrase in (
            "Trellis 是任务、规格和状态的唯一工作流来源",
            "主动读取并使用 `$grill-with-docs`",
            "使用 Skill 与向用户提问分开判断",
            "没有专用工具不等于跳过 Trellis",
            "进入 Trellis 轻量流程",
            "已有充分的 Phase 1.1 结论且本次范围未变化时复用",
            "不自动启动复杂规划或全仓验证",
            "使用 Grill with Docs 后不再运行 `trellis-brainstorm`",
        ):
            self.assertIn(phrase, content)
        self.assertNotIn("复杂、跨模块或需求不明确的任务：先使用", content)

    def test_global_template_keeps_capability_boundaries_explicit(self) -> None:
        content = (ROOT / "AGENTS.global.md").read_text(encoding="utf-8")

        for phrase in (
            "Skill 不得创建与 Trellis 平行的任务生命周期",
            "不作为每次修改都必须单独执行的工作流阶段",
            "局部低风险修改不自动调用",
            "最终验证是**任务级门禁**",
            "可用命令清单不是默认必跑清单",
            "`quality` 会执行所选检查并记录结果",
            "证据复用必须以 helper 的实际校验结果为准",
        ):
            self.assertIn(phrase, content)

    def test_project_override_resolves_native_trellis_skill_aliases(self) -> None:
        content = (ROOT / "AGENTS.project.md").read_text(encoding="utf-8")

        for phrase in (
            "主动使用 `$grill-with-docs` 完成 Phase 1.1 需求审查",
            "不要再加载 `trellis-brainstorm`",
            "项目原生 `trellis-check`",
            "纯咨询不建 Task",
        ):
            self.assertIn(phrase, content)

    def test_repository_dogfoods_the_codex_phase_override(self) -> None:
        content = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("主动使用 `$grill-with-docs` 完成 Trellis Phase 1.1 需求审查", content)
        self.assertIn("简单且需求明确的任务直接走 Trellis", content)
        self.assertIn("不要再加载 `trellis-brainstorm`", content)
        self.assertIn("实现稳定后，按当前 Task 要求使用项目原生 `trellis-check`", content)

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
