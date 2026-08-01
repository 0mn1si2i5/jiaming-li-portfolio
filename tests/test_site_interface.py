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


if __name__ == "__main__":
    unittest.main()
