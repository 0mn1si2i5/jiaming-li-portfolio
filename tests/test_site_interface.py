from __future__ import annotations

import hashlib
import json
import re
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
        self.assertIn('site.emails', about)
        self.assertNotIn('${site.email}', about)
        self.assertIn('site.resumePath', about)
        self.assertNotIn('class="note"', about)
        self.assertFalse((self.root / "src/pages/notes.astro").exists())
        self.assertNotIn('id="about"', self.home)

    def test_about_has_complete_intro_and_two_education_entries(self) -> None:
        about = (self.root / "src/pages/about.astro").read_text(encoding="utf-8")
        site = (self.root / "src/config/site.ts").read_text(encoding="utf-8")
        self.assertIn(
            "目前在新加坡国立大学攻读计算机硕士，在 AI4SG Lab 研究人机协作与生成式 AI 创作",
            about,
        )
        for token in (
            "National University of Singapore",
            "AI4SG Lab",
            "human–AI collaboration",
            "generative-AI creation",
            "ByteDance",
            "HCI",
            "DialogTree",
            "Mundus",
        ):
            self.assertIn(token, about)
        self.assertNotIn("项目类型虽然不同", about)
        self.assertNotIn("The projects differ", about)
        self.assertIn("emails: [", site)
        self.assertIn("nomisomnis@gmail.com", site)
        self.assertIn("E1442419@u.nus.edu", site)
        self.assertNotIn("email: 'nomisomnis@gmail.com'", site)
        self.assertIn("新加坡国立大学", about)
        self.assertIn("北京大学", about)
        self.assertIn("俄语语言文学", about)
        self.assertIn("北京大学社会工作奖", about)
        for banned in ("GPA", "GRE", "IELTS"):
            self.assertNotIn(banned, about)
            self.assertNotIn(banned, site)

    def test_email_contact_component_is_accessible_and_copyable(self) -> None:
        component = (
            self.root / "src/components/EmailContact.astro"
        ).read_text(encoding="utf-8")
        self.assertIn('mailto:${address}', component)
        self.assertIn('class="email-address"', component)
        self.assertIn('type="button"', component)
        self.assertIn('data-copy-email', component)
        self.assertIn('data-address={address}', component)
        self.assertIn('role="status"', component)
        self.assertIn('aria-live="polite"', component)
        self.assertIn('Copy', component)
        self.assertIn('复制', component)
        self.assertIn('Copied', component)
        self.assertIn('已复制', component)
        self.assertIn('Select and copy the address manually.', component)
        self.assertIn('请选中邮箱地址手动复制', component)
        self.assertIn('navigator.clipboard.writeText', component)
        about = (self.root / "src/pages/about.astro").read_text(encoding="utf-8")
        self.assertIn('import EmailContact', about)
        self.assertIn('<EmailContact', about)

    def test_internship_section_titles_use_distinct_two_level_text(self) -> None:
        self.assertIn('zh="经历"', self.home)
        self.assertIn('en="Experience"', self.home)
        self.assertIn('en="Internship project"', self.home)
        # the eyebrow (before the heading) must not reuse the heading's Chinese text
        self.assertNotIn('zh="实习项目"', self.home.split('id="internship-title"')[0])

    def test_email_copy_buttons_have_distinct_accessible_names(self) -> None:
        component = (
            self.root / "src/components/EmailContact.astro"
        ).read_text(encoding="utf-8")
        site = (self.root / "src/config/site.ts").read_text(encoding="utf-8")
        self.assertIn('label.en', component)
        self.assertIn('label.zh', component)
        self.assertIn('aria-hidden="true"', component)
        self.assertIn("'Personal email'", site)
        self.assertIn("'University email'", site)
        self.assertIn('个人邮箱', site)
        self.assertIn('学校邮箱', site)

    def test_bytedance_media_uses_public_workspace_concept_map(self) -> None:
        media = (
            self.root / "src/components/ProjectMedia.astro"
        ).read_text(encoding="utf-8")
        component = (
            self.root / "src/components/ByteDanceWorkspaceMap.astro"
        ).read_text(encoding="utf-8")
        self.assertIn('ByteDanceWorkspaceMap', media)
        self.assertNotIn('ByteDanceOverview', media)
        self.assertFalse(
            (self.root / "src/components/ByteDanceOverview.astro").exists()
        )
        self.assertIn('data-public-concept', component)
        self.assertIn('Public workflow concept', component)
        self.assertIn('公开流程概念图', component)
        self.assertIn('data-workspace-region="files"', component)
        self.assertIn('data-workspace-region="sheet"', component)
        self.assertIn('data-workspace-region="workbench"', component)
        self.assertIn('File hierarchy', component)
        self.assertIn('Lark sheet workspace', component)
        self.assertIn('Floating speech workbench', component)
        self.assertIn('浮动语音工作台', component)
        for stage in (
            "Table and sheet",
            "Source range and result columns",
            "Voice candidate pool and conflict policy",
            "Start preflight",
            "Progress and status feedback",
        ):
            self.assertIn(stage, component)

    def test_bytedance_before_after_uses_four_quadrant_matrix(self) -> None:
        source = (
            self.root / "src/content/projects/bytedance-ai-data.mdx"
        ).read_text(encoding="utf-8")
        component = (
            self.root / "src/components/BeforeAfterMatrix.astro"
        ).read_text(encoding="utf-8")
        self.assertIn('BeforeAfterMatrix', source)
        self.assertNotIn('BeforeAfterFlow', source)
        self.assertNotIn('before={', source)
        self.assertNotIn('after={', source)
        self.assertFalse(
            (self.root / "src/components/BeforeAfterFlow.astro").exists()
        )
        self.assertIn('comment bot', source)
        self.assertIn('评论机器人', source)
        self.assertIn('floating speech workbench', source)
        self.assertIn('浮动语音工作台', source)
        for token in (
            'audience',
            'audienceLabel',
            'data-audience',
            'data-state',
            'rows',
            'sharedQcLabel',
            'sharedQcItems',
        ):
            self.assertIn(token, component)
        self.assertIn('internal', component)
        self.assertIn('external', component)

    def test_public_output_does_not_contain_botts_name(self) -> None:
        pattern = re.compile(r"\bbotts\b", re.IGNORECASE)
        for path in (self.root / "src").rglob("*"):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            self.assertIsNone(pattern.search(text), f"Botts leaked in {path}")
        dist = self.root / "dist"
        if dist.is_dir():
            for path in dist.rglob("*"):
                if (
                    not path.is_file()
                    or path.suffix not in (".html", ".css", ".js")
                ):
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except (UnicodeDecodeError, OSError):
                    continue
                self.assertIsNone(
                    pattern.search(text), f"Botts leaked in {path}"
                )

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

    def test_homepage_sections_order_featured_internship_more(self) -> None:
        self.assertIn('id="internship"', self.home)
        self.assertIn('zh="实习项目"', self.home)
        featured = self.home.index('id="work"')
        internship = self.home.index('id="internship"')
        more = self.home.index('id="other-title"')
        self.assertLess(featured, internship)
        self.assertLess(internship, more)

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
