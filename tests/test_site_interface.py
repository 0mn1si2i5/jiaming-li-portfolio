from __future__ import annotations

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

    def test_navigation_uses_home_work_and_about(self) -> None:
        self.assertIn('<Localized en="Home" zh="主页" />', self.layout)
        self.assertIn('href={`${base}#work`}', self.layout)
        self.assertIn('href={`${base}about`}', self.layout)
        self.assertNotIn('href={`${base}notes`}', self.layout)

    def test_about_page_owns_about_copy_and_empty_notes_section(self) -> None:
        about = (self.root / "src/pages/about.astro").read_text(encoding="utf-8")
        self.assertIn('id="about-title"', about)
        self.assertIn('id="notes-title"', about)
        self.assertIn('href={site.github}', about)
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


if __name__ == "__main__":
    unittest.main()
