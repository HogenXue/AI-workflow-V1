import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GrillMeTrellisRouteTests(unittest.TestCase):
    def test_global_template_assigns_the_required_workflow_owners(self) -> None:
        content = (ROOT / "trellis" / "AGENTS.global.md").read_text(encoding="utf-8")

        markers = (
            "复杂需求",
            "$grill-me",
            "由 OpenSpec 维护正式 Spec",
            "创建 Trellis task",
            "TDD",
            "GitNexus",
        )
        positions = [content.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("Trellis 维护 task 级 PRD/计划", content)
        self.assertIn("不复制需求、场景或验收", content)
        self.assertIn("OpenSpec 不维护任务清单", content)


if __name__ == "__main__":
    unittest.main()
