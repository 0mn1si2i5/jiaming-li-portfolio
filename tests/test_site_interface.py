from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


class TestSiteInterface(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).parents[1]
        self.layout = (self.root / "src/components/BaseLayout.astro").read_text(
            encoding="utf-8"
        )
        self.home = (self.root / "src/pages/index.astro").read_text(
            encoding="utf-8"
        )
        self.project = (
            self.root / "src/pages/projects/[...slug].astro"
        ).read_text(encoding="utf-8")
        self.dialogtree = (
            self.root / "src/content/projects/dialogtree.mdx"
        ).read_text(encoding="utf-8")
        self.side_b = (
            self.root / "src/content/projects/side-b.mdx"
        ).read_text(encoding="utf-8")

    def test_navigation_uses_home_work_and_about(self) -> None:
        self.assertIn('<Localized en="Home" zh="主页" />', self.layout)
        self.assertIn('href={`${base}#work`}', self.layout)
        self.assertIn('href={`${base}about`}', self.layout)
        self.assertNotIn('href={`${base}notes`}', self.layout)

    def test_header_has_one_home_destination_without_monogram(self) -> None:
        header = self.layout.split('<header class="site-header">', 1)[1].split(
            "</header>", 1
        )[0]
        self.assertEqual(header.count('<Localized en="Home" zh="主页" />'), 1)
        self.assertNotIn('class="monogram"', header)
        self.assertNotIn(".monogram", self.layout)

    def test_home_cards_omit_status_while_project_details_keep_it(self) -> None:
        self.assertNotIn('class="status"', self.home)
        self.assertNotIn(".project-copy .status", self.home)
        self.assertIn(
            '<dt><Localized en="Status" zh="状态" /></dt>',
            self.project,
        )

    def test_project_details_use_natural_shared_labels(self) -> None:
        self.assertIn('<Localized en="Status" zh="状态" />', self.project)
        self.assertIn('<Localized en="My work" zh="我的工作" />', self.project)
        self.assertIn(
            '<Localized en="About this project" zh="项目说明" />',
            self.project,
        )
        self.assertNotIn('zh="项目状态"', self.project)
        self.assertNotIn('zh="负责内容"', self.project)
        self.assertNotIn('zh="探索"', self.project)

    def test_non_featured_project_index_localizes_archive(self) -> None:
        self.assertIn('<Localized en="Archive" zh="其他项目" />', self.project)

    def test_project_breadcrumbs_use_global_labels(self) -> None:
        self.assertIn(
            "en={project.data.featured ? 'Work' : 'More projects'}",
            self.project,
        )
        self.assertIn(
            "zh={project.data.featured ? '项目' : '更多项目'}",
            self.project,
        )
        self.assertNotIn("'Selected work'", self.project)
        self.assertNotIn("'Other work'", self.project)
        self.assertNotIn("精选项目", self.project)
        self.assertNotIn("其他作品", self.project)

    def test_dialogtree_capcut_credit_is_removed(self) -> None:
        self.assertNotIn("视频由 CapCut 剪辑", self.project)
        self.assertNotIn("Video edited in CapCut", self.project)

    def test_package_and_local_pages_base_use_canonical_repository_name(self) -> None:
        package = json.loads(
            (self.root / "package.json").read_text(encoding="utf-8")
        )
        lock = json.loads(
            (self.root / "package-lock.json").read_text(encoding="utf-8")
        )
        config = (self.root / "astro.config.mjs").read_text(encoding="utf-8")
        self.assertEqual(package["name"], "jiaming-li-portfolio")
        self.assertEqual(lock["name"], "jiaming-li-portfolio")
        self.assertEqual(lock["packages"][""]["name"], "jiaming-li-portfolio")
        self.assertIn(
            "const localProjectBase = '/jiaming-li-portfolio';",
            config,
        )

    def test_about_page_has_positioning_contact_and_no_empty_notes(self) -> None:
        about = (self.root / "src/pages/about.astro").read_text(encoding="utf-8")
        self.assertIn('id="about-title"', about)
        self.assertNotIn('id="notes-title"', about)
        self.assertIn('href={site.github}', about)
        self.assertIn('site.email', about)
        self.assertIn('site.resumePath', about)
        self.assertNotIn('class="note"', about)
        self.assertFalse((self.root / "src/pages/notes.astro").exists())
        self.assertNotIn('id="about"', self.home)

    def test_footer_keeps_copyright_without_github(self) -> None:
        footer = self.layout.split('<footer class="site-footer">', 1)[1].split(
            "</footer>", 1
        )[0]
        self.assertIn("site.name", footer)
        self.assertNotIn("site.github", footer)
        self.assertNotIn("GitHub", footer)

    def test_internal_project_ctas_are_removed_but_titles_and_media_link(self) -> None:
        self.assertNotIn("Read the exploration", self.home)
        self.assertNotIn("查看项目详情", self.home)
        self.assertIn('class="media-link"', self.home)
        self.assertIn('<h3><a href={`${base}projects/${project.id}`}>', self.home)
        self.assertIn('class="other-media"', self.home)

    def test_external_links_are_blue_and_use_external_arrow(self) -> None:
        about = (self.root / "src/pages/about.astro").read_text(encoding="utf-8")
        self.assertIn('class="external-link"', about)
        self.assertIn('aria-hidden="true">↗</span>', about)
        self.assertIn('class="external-link"', self.home)
        self.assertIn("--external-link: var(--blue);", self.layout)
        self.assertIn("color: var(--external-link);", self.project)

    def test_project_titles_do_not_inherit_external_link_color(self) -> None:
        self.assertRegex(
            self.home,
            r"\.other-copy > h3 a\s*\{[^}]*color: var\(--ink\);",
        )
        self.assertNotIn(".other-card a { color: var(--blue);", self.home)

    def test_dialogtree_story_images_use_pages_base(self) -> None:
        self.assertIn("const dialogTreeAsset =", self.dialogtree)
        self.assertNotIn('src="../../media/dialogtree-live-', self.dialogtree)
        self.assertEqual(
            self.dialogtree.count(
                'src={dialogTreeAsset("dialogtree-live-tree.png")}'
            ),
            2,
        )
        self.assertEqual(
            self.dialogtree.count(
                'src={dialogTreeAsset("dialogtree-live-node-switch.png")}'
            ),
            2,
        )

    def test_nbti_uses_play_matching_boundaries_sections(self) -> None:
        nbti = (self.root / "src/content/projects/nbti.mdx").read_text(
            encoding="utf-8"
        )
        for heading in ("## 玩法", "## 如何匹配", "## 使用边界"):
            self.assertIn(heading, nbti)
        for old in ("## 起点", "## 体验", "## 背后的系统", "## 谨慎地使用历史"):
            self.assertNotIn(old, nbti)
        self.assertNotIn(
            "人格测试为人们提供了一种理解自身选择的语言",
            nbti,
        )
        for token in (
            "18",
            "6",
            "32",
            "六种行动倾向",
            "确定性",
            "本地",
            "不要求账户",
            "不使用 Cookie",
            "分析追踪",
            "不保存回答",
            "不是心理测评",
            "科学诊断",
        ):
            self.assertIn(token, nbti)
        self.assertIn("How it plays", nbti)
        self.assertIn("How matching works", nbti)
        self.assertIn("Boundaries", nbti)

    def test_side_b_uses_prototype_flow_and_available_links(self) -> None:
        side_b = (self.root / "src/content/projects/side-b.mdx").read_text(
            encoding="utf-8"
        )
        gallery = (
            self.root / "src/components/SideBGallery.astro"
        ).read_text(encoding="utf-8")
        for heading in (
            "## 问题",
            "## Side B 的处理方式",
            "## 原型实现",
            "## 下一步验证",
        ):
            self.assertIn(heading, side_b)
        for platform in ("Spotify", "Apple Music", "网易云音乐", "QQ 音乐"):
            self.assertIn(platform, side_b)
        self.assertIn("可用的平台链接", side_b)
        self.assertIn("四家音乐平台", side_b)
        self.assertIn("four music services", side_b)
        self.assertIn("原型流程", gallery)
        self.assertIn("一段演示对话", side_b)
        self.assertIn("sample room conversation", side_b)
        self.assertNotIn("全平台链接", side_b)
        self.assertNotIn("全平台跳转", side_b)
        self.assertNotIn("实际使用", gallery)
        self.assertNotIn("实际聊天室中的一段对话", side_b)

    def test_side_b_uses_dedicated_homepage_preview(self) -> None:
        self.assertIn(
            "preview: /media/side-b/side-b-journey-preview.webp",
            self.side_b,
        )
        self.assertIn(
            "src: /media/side-b/side-b-journey-hero.webp",
            self.side_b,
        )
        preview = (
            self.root
            / "public/media/side-b/side-b-journey-preview.webp"
        )
        self.assertTrue(preview.is_file())
        self.assertEqual(
            hashlib.sha256(preview.read_bytes()).hexdigest(),
            "079260c356eee7df46dc21eecb8f96ec0fbd26bf833b74678d65b390ac649d26",
        )
        self.assertIn(
            ".other-media :global(.project-media) { width: 100%; height: 100%; "
            "aspect-ratio: auto;",
            self.home,
        )
        self.assertIn(
            ".other-media :global(.preview-media img) { object-fit: contain; }",
            self.home,
        )


if __name__ == "__main__":
    unittest.main()
