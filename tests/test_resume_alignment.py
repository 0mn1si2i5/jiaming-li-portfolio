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
        self.assertNotIn("## Project overview", source)
        self.assertNotIn("## 项目说明", source)
        self.assertIn("## 语音评测集迭代", source)
        self.assertIn("## 语音数据生产工具", source)
        self.assertNotIn("语音数据生产平台（内部工具）", source)
        self.assertIn("本案例以通用方式描述工作流程", source)
        self.assertIn(
            "This case describes the workflow in general terms",
            source,
        )
        for metric in ("88.6%", "82%", "97%", "20%", "三倍", "约 30"):
            self.assertIn(metric, source)

    def test_home_positioning_and_external_work_are_bilingual(self) -> None:
        home = (self.root / "src/pages/index.astro").read_text(encoding="utf-8")
        site = (self.root / "src/config/site.ts").read_text(encoding="utf-8")
        self.assertIn("产品、研究与独立开发。", home)
        self.assertIn("这里收录了我持续维护的个人作品", home)
        self.assertIn("independent projects I continue to maintain", home)
        self.assertNotIn("项目形态不同", home)
        self.assertNotIn("有实习期间交付的内部工具", home)
        self.assertNotIn("我做 AI 评测、数据工具和交互产品。", home)
        self.assertIn("dsh-handoff", site)
        self.assertIn("resume", site)

    def test_homepage_uses_explicit_featured_and_internship_groups(self) -> None:
        home = (self.root / "src/pages/index.astro").read_text(encoding="utf-8")
        self.assertIn("['dialogtree', 'mundus']", home)
        self.assertIn("['bytedance-ai-data']", home)
        self.assertIn("实习项目", home)
        self.assertIn("Internship", home)

    def test_dialogtree_date_matches_resume(self) -> None:
        source = (
            self.root / "src/content/projects/dialogtree.mdx"
        ).read_text(encoding="utf-8")
        self.assertIn("Sep–Nov 2025", source)
        self.assertIn("2025 年 9–11 月", source)

    def test_dialogtree_uses_direct_chinese_headings(self) -> None:
        source = (
            self.root / "src/content/projects/dialogtree.mdx"
        ).read_text(encoding="utf-8")
        for heading in (
            "## 问题",
            "## 设计思路",
            "## DialogTree",
            "## 交互方式",
            "## 从原型到 Branchat",
        ):
            self.assertIn(heading, source)
        for old in ("我们观察到的问题", "我们探索的方向", "我们实现的产品"):
            self.assertNotIn(old, source)
        self.assertIn("我和李然想把对话从线性记录变成可导航的知识结构。", source)
        self.assertNotIn("我和李然关注的是：能否", source)


if __name__ == "__main__":
    unittest.main()
