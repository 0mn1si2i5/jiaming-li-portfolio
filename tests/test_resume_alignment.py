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

    def test_bytedance_uses_speech_evaluation_positioning_and_metrics(
        self,
    ) -> None:
        source = (
            self.root / "src/content/projects/bytedance-ai-data.mdx"
        ).read_text(encoding="utf-8")
        self.assertIn("字节跳动语音评测与数据工具", source)
        self.assertIn("Speech Evaluation & Data Tooling at ByteDance", source)
        self.assertNotIn("字节跳动 AI 评测与数据工具", source)
        self.assertNotIn("AI Evaluation & Data Tooling", source)
        self.assertIn("实习项目（内容已脱敏）", source)
        self.assertIn("语音评测与内部工具", source)
        self.assertIn("## 项目说明", source)
        self.assertIn("## 语音评测集迭代", source)
        self.assertIn("## 语音数据生产工具", source)
        self.assertNotIn("语音数据生产平台（内部工具）", source)
        for metric in ("88.6%", "82%", "97%", "20%", "三倍", "约 30"):
            self.assertIn(metric, source)

    def test_home_positioning_and_external_work_are_bilingual(self) -> None:
        home = (self.root / "src/pages/index.astro").read_text(encoding="utf-8")
        site = (self.root / "src/config/site.ts").read_text(encoding="utf-8")
        self.assertIn("产品、研究与独立开发。", home)
        self.assertIn("项目形态不同", home)
        self.assertNotIn("我做 AI 评测、数据工具和交互产品。", home)
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
