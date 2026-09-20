import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GrillWithDocsTrellisRouteTests(unittest.TestCase):
    def test_global_template_routes_simple_and_complex_trellis_work(self) -> None:
        content = (ROOT / "AGENTS.global.md").read_text(encoding="utf-8")

        for phrase in (
            "Trellis 是任务、规格和状态的唯一工作流来源",
            "`$grill-me` 仅在用户显式调用时使用",
            "Grill 期间只进行无状态对话",
            "没有专用工具不等于跳过 Trellis",
            "进入 Trellis 轻量流程",
            "不自动启动复杂规划或全仓验证",
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
            "`$grill-me` 是唯一 Grill Skill",
            "仅在用户显式调用时进行无状态澄清",
            "项目原生 `trellis-check`",
            "纯咨询不建 Task",
        ):
            self.assertIn(phrase, content)

    def test_repository_dogfoods_the_codex_phase_override(self) -> None:
        path = ROOT / "AGENTS.md"
        if not path.is_file():
            self.skipTest("project-owned AGENTS.md is absent in this working tree")
        content = path.read_text(encoding="utf-8")

        self.assertIn("`$grill-me` 是唯一 Grill Skill", content)
        self.assertIn("简单且需求明确的任务直接走 Trellis", content)
        self.assertIn("不要再加载 `trellis-brainstorm`", content)
        self.assertIn("实现稳定后，按当前 Task 要求使用项目原生 `trellis-check`", content)

    def test_single_grill_skill_is_explicit_and_stateless(self) -> None:
        manifest = (ROOT / "manifest.yaml").read_text(encoding="utf-8")
        for capability in (
            "grill-me",
            "diagnosing-bugs",
            "codebase-design",
            "resolving-merge-conflicts",
        ):
            self.assertIn(f"  - {capability}", manifest)
            self.assertTrue((ROOT / "skills" / capability / "SKILL.md").is_file())

        for removed in ("grill-with-docs", "grilling", "domain-modeling"):
            self.assertNotIn(f"  - {removed}", manifest)
            self.assertFalse((ROOT / "skills" / removed / "SKILL.md").exists())

        skill = ROOT / "skills" / "grill-me"
        content = (skill / "SKILL.md").read_text(encoding="utf-8")
        agent = (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
        for phrase in ("disable-model-invocation: true", "stateless", "decision tree", "frontier", "do not write files"):
            self.assertIn(phrase, content)
        self.assertIn("allow_implicit_invocation: false", agent)


if __name__ == "__main__":
    unittest.main()
