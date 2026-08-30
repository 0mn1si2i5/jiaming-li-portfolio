from __future__ import annotations

import unittest
from pathlib import Path


class TestResumeAlignment(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).parents[1]

    def test_bytedance_case_uses_public_safe_names_and_two_anchors(self) -> None:
        source_path = self.root / "src/content/projects/bytedance-ai-data.mdx"
        self.assertTrue(source_path.exists(), "ByteDance case study is missing")
        source = source_path.read_text(encoding="utf-8")
        self.assertIn('id="speech-evaluation"', source)
        self.assertIn('id="data-tooling"', source)
        self.assertNotIn("botts-web.bytedance.net", source.lower())
        self.assertNotIn("lark-comment-tts", source.lower())
        self.assertNotIn("bytedance-202608-archive", source.lower())

    def test_home_positioning_and_external_work_are_bilingual(self) -> None:
        home = (self.root / "src/pages/index.astro").read_text(encoding="utf-8")
        site = (self.root / "src/config/site.ts").read_text(encoding="utf-8")
        self.assertIn("我做 AI 评测、数据工具和交互产品。", home)
        self.assertIn("dsh-handoff", site)
        self.assertIn("resume", site)

    def test_dialogtree_date_matches_resume(self) -> None:
        source = (
            self.root / "src/content/projects/dialogtree.mdx"
        ).read_text(encoding="utf-8")
        self.assertIn("Sep–Nov 2025", source)
        self.assertIn("2025 年 9–11 月", source)


if __name__ == "__main__":
    unittest.main()
