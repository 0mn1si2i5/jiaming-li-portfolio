from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

from scripts.verification import browser, facts


class TestProductCaseStudyFocus(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Path(__file__).parents[1]

    def test_mundus_case_uses_direct_editorial_voice(self) -> None:
        case = (
            self.project / "src/content/projects/mundus.mdx"
        ).read_text(encoding="utf-8")
        story = (
            self.project / "src/components/MundusStory.astro"
        ).read_text(encoding="utf-8")
        visitor_copy = f"{case}\n{story}"
        sections = re.findall(
            r'<section\b[^>]*data-locale-content="(en|zh)"[^>]*>'
            r"(.*?)</section>",
            case,
            flags=re.DOTALL,
        )
        headings_by_locale = {"en": [], "zh": []}
        for locale, section in sections:
            headings_by_locale[locale].extend(
                line.removeprefix("## ")
                for line in section.splitlines()
                if line.startswith("## ")
            )
        all_headings = [
            line.removeprefix("## ")
            for line in case.splitlines()
            if line.startswith("## ")
        ]

        self.assertEqual(
            headings_by_locale["en"],
            [
                "An evolving personal globe",
                "What every mode shares",
                "How it is built and published",
                "Chronorbis",
            ],
        )
        self.assertEqual(
            headings_by_locale["zh"],
            [
                "一颗持续扩展的个人数字地球",
                "所有模式共用的部分",
                "构建与发布",
                "Chronorbis",
            ],
        )
        self.assertEqual(len(all_headings), 8)

        for phrase in (
            "a globe i can keep extending",
            "built for continued maintenance",
            "how it grows",
            "product governance",
            "not a final",
            "not a candidate",
            "rather than",
            "instead of",
            "ghsl",
            "stop_global_morphology",
        ):
            self.assertNotIn(phrase, visitor_copy.casefold())

        for phrase in (
            "一颗持续生长",
            "为长期维护做出的选择",
            "如何继续生长",
            "产品治理",
            "不是最终",
            "不是候选",
            "而不是",
            "不代表",
        ):
            self.assertNotIn(phrase, visitor_copy)

        self.assertEqual(story.count("<img"), 1)

    def test_chronorbis_is_personal_unfinished_and_not_a_mundus_capability(
        self,
    ) -> None:
        case = (
            self.project / "src/content/projects/mundus.mdx"
        ).read_text(encoding="utf-8")
        locale_sections = re.findall(
            r"<section\b([^>]*)>(.*?)</section>",
            case,
            flags=re.DOTALL,
        )
        chronorbis_sections: dict[str, str] = {}
        mundus_sections: dict[str, list[str]] = {"en": [], "zh": []}
        for attributes, section in locale_sections:
            locale_match = re.search(
                r'\bdata-locale-content="(en|zh)"',
                attributes,
            )
            if locale_match is None:
                continue
            locale = locale_match.group(1)
            visible = facts.extract_mdx_visible_text(section)
            class_match = re.search(r'\bclass="([^"]*)"', attributes)
            if (
                class_match
                and "chronorbis-vision" in class_match.group(1).split()
            ):
                self.assertNotIn(
                    locale,
                    chronorbis_sections,
                    f"multiple Chronorbis sections found for {locale}",
                )
                chronorbis_sections[locale] = visible
            else:
                mundus_sections[locale].append(visible)

        self.assertEqual(set(chronorbis_sections), {"en", "zh"})
        self.assertTrue(all(mundus_sections.values()))

        required_by_locale = {
            "en": (
                ("Chronorbis", "Not built", "released"),
                ("alternate-history", "authoring simulator"),
                ("specific", "times", "places"),
                ("persistent", "editable", "knowledge base"),
                ("built-in", "multi-agent", "roles"),
                ("technically unresolved",),
                ("separate", "unfinished", "direction"),
            ),
            "zh": (
                ("Chronorbis", "尚未实现", "发布"),
                ("架空历史", "创作模拟器"),
                ("具体", "时间", "空间"),
                ("长期保存", "随时编辑", "知识库"),
                ("内置", "multi-agent", "分工"),
                ("技术条件", "未解决"),
                ("独立", "尚未实现", "方向"),
            ),
        }
        for locale, semantic_groups in required_by_locale.items():
            with self.subTest(locale=locale):
                visible = chronorbis_sections[locale]
                for tokens in semantic_groups:
                    with self.subTest(locale=locale, tokens=tokens):
                        for token in tokens:
                            self.assertIn(token, visible)

        forbidden_mundus_mechanisms = {
            "en": (
                "alternate-history",
                "authoring simulator",
                "knowledge base",
                "multi-agent",
                "history simulation",
                "historical simulation",
                "historical event simulation",
                "simulates historical events",
            ),
            "zh": (
                "架空历史",
                "创作模拟器",
                "知识库",
                "multi-agent",
                "历史模拟",
                "历史事件模拟",
                "模拟历史事件",
            ),
        }
        for locale, sections in mundus_sections.items():
            for section_index, visible in enumerate(sections):
                for token in forbidden_mundus_mechanisms[locale]:
                    with self.subTest(
                        locale=locale,
                        section=section_index,
                        forbidden_mundus_token=token,
                    ):
                        self.assertNotIn(token, visible.casefold())

    def test_mundus_copy_names_no_mode_and_no_mode_count(self) -> None:
        case = (
            self.project / "src/content/projects/mundus.mdx"
        ).read_text(encoding="utf-8")
        story = (
            self.project / "src/components/MundusStory.astro"
        ).read_text(encoding="utf-8")
        copy = f"{case}\n{story}"

        # Released and retired mode names. `npm run verify` also rejects every
        # title in the Mundus mode registry at the pinned revision.
        for name in (
            "Other Side",
            "Surname Atlas",
            "Urban Proximity",
            "Sunline",
            "Development, Unpacked",
            "地球另一端",
            "姓氏观察",
            "城市邻近性",
            "日照线",
            "发展的不同侧面",
        ):
            with self.subTest(name=name):
                self.assertNotIn(name, copy)
        self.assertNotRegex(
            copy.casefold(),
            r"\b(?:two|three|four|five|six)\s+(?:public\s+|released\s+)?"
            r"(?:modes|views|observations)\b",
        )
        self.assertNotRegex(copy, r"[二两三四五六][个种]\S{0,4}(?:模式|视角|观察)")

    def test_mundus_story_reads_previews_from_the_live_manifest(self) -> None:
        story = (
            self.project / "src/components/MundusStory.astro"
        ).read_text(encoding="utf-8")

        self.assertNotIn("const modes = [", story)
        self.assertEqual(story.count("<img"), 1)
        for token in (
            "new URL('previews/manifest.json', site.links.mundusWebsite)",
            "data-manifest-url={manifestUrl}",
            "href={site.links.mundusWebsite}",
            "src={asset(fallback.image)}",
            "alt={fallback.alt.en}",
            'role="tablist"',
            "data-preview-tabs hidden",
            'target="_blank"',
            'rel="noopener noreferrer"',
            "manifest?.schemaVersion !== 1",
            "new URL(url).origin === origin",
            "if (![href, images.en, images.zh].every(sameSite)) return [];",
            "tab.setAttribute('role', 'tab');",
            "tab.setAttribute('aria-controls', 'mundus-preview-panel');",
            "tab.dataset.modeId = mode.id;",
            "tab.dataset.href = mode.href;",
            "span.textContent = text[key];",
            "const candidate = new Image()",
            "candidate.onload = () => {",
            "candidate.onerror = () => {",
            "panel.setAttribute('role', 'tabpanel');",
            "panel.setAttribute('aria-labelledby', tab.id);",
            "tablist.hidden = false;",
            "new IntersectionObserver(",
            "controller.abort()",
            "attributeFilter: ['data-locale']",
            "ArrowLeft",
            "ArrowRight",
            "ArrowUp",
            "ArrowDown",
            "Home",
            "End",
        ):
            with self.subTest(token=token):
                self.assertIn(token, story)

        # Manifest text is inserted as text, never as markup.
        self.assertNotIn("innerHTML", story)
        self.assertNotIn("insertAdjacentHTML", story)

        keydown_match = re.search(
            r"tab\.addEventListener\('keydown', \(event\) => \{"
            r"(?P<body>.*?)^\s*\}\);",
            story,
            flags=re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(keydown_match)
        keydown = keydown_match.group("body")
        self.assertLess(
            keydown.find("event.preventDefault();"),
            keydown.find("tabs[next].focus();"),
        )
        self.assertLess(
            keydown.find("tabs[next].focus();"),
            keydown.find("activate(tabs[next]);"),
        )
        onerror_match = re.search(
            r"candidate\.onerror = \(\) => \{(?P<body>.*?)^\s*\};",
            story,
            flags=re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(onerror_match)
        for mutation in ("image.src", "link.href", "setAttribute", "tabIndex"):
            self.assertNotIn(mutation, onerror_match.group("body"))
        self.assertRegex(
            story,
            r"(?s)@media \(prefers-reduced-motion: reduce\) \{.*?"
            r"\.preview-link img\s*\{\s*transition: none;",
        )

    def test_mundus_media_has_three_distinct_roles(self) -> None:
        case = (
            self.project / "src/content/projects/mundus.mdx"
        ).read_text(encoding="utf-8")
        story = (
            self.project / "src/components/MundusStory.astro"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "src: /media/mundus/other-side-full.webp",
            case,
        )
        self.assertIn(
            "preview: /media/mundus/globe-preview.webp",
            case,
        )
        self.assertIn("previewAlt:", case)
        self.assertIn("/media/mundus/other-side-detail.webp", story)
        for path in (
            "/media/mundus/development.webp",
            "/media/mundus/sunline.webp",
        ):
            self.assertNotIn(path, story)
            self.assertFalse((self.project / "public" / path.lstrip("/")).exists())
        self.assertNotIn(
            "/media/mundus/modes-overview.webp",
            story,
        )

    def test_mundus_source_media_is_bound_to_current_public_deployment(
        self,
    ) -> None:
        manifest = json.loads(
            (
                self.project
                / "docs/verification/evidence/mundus-media.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(
            manifest["sourceRevision"],
            "378fe528ca1c8f83f0280f83383b5e785e851285",
        )
        self.assertEqual(manifest["captureLocale"], "zh-CN")
        self.assertEqual(manifest["previewVisibleUiCount"], 0)
        self.assertEqual(
            [item["role"] for item in manifest["images"]],
            [
                "homepage-globe",
                "project-full-interface",
                "story-other-side",
            ],
        )
        self.assertEqual(
            {
                (item["width"], item["height"])
                for item in manifest["images"]
                if item["role"].startswith("story-")
            },
            {(1920, 1080)},
        )
        self.assertEqual(manifest["panelOverflowCount"], 0)
        self.assertEqual(manifest["storyPanelOverflowCount"], 0)
        self.assertEqual(manifest["consoleErrorCount"], 0)
        self.assertEqual(manifest["pageErrorCount"], 0)
        self.assertEqual(manifest["failedRequestCount"], 0)
        self.assertGreaterEqual(manifest["images"][1]["width"], 1920)
        self.assertEqual(
            len({item["sha256"] for item in manifest["images"]}),
            3,
        )

        for item in manifest["images"]:
            path = self.project / "public/media/mundus" / item["path"]
            self.assertTrue(path.is_file())
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                item["sha256"],
            )
            self.assertEqual(
                browser.webp_dimensions(path),
                (item["width"], item["height"]),
            )

    def test_mundus_media_capture_rejects_failed_responses_before_writes(
        self,
    ) -> None:
        script = (
            self.project / "scripts/capture-mundus-media.mjs"
        ).read_text(encoding="utf-8")

        self.assertRegex(
            script,
            r"(?s)page\.on\('response', \(response\) => \{.*?"
            r"const responseUrl = response\.url\(\);.*?"
            r"response\.request\(\)\.resourceType\(\) === 'document'.*?"
            r"responseUrl\.startsWith\('http://'\).*?"
            r"responseUrl\.startsWith\('https://'\).*?"
            r"if \(!response\.ok\(\)\) \{.*?"
            r"requestFailures\.push\(\{\s*url: responseUrl,\s*"
            r"status: response\.status\(\),\s*\}\);",
        )
        self.assertRegex(
            script,
            r"\[\.\.\.document\.images\]\.every\(\s*"
            r"\(image\) =>\s*image\.complete\s*&&\s*"
            r"image\.naturalWidth > 0\s*&&\s*"
            r"image\.naturalHeight > 0",
        )
        self.assertRegex(
            script,
            r"(?s)async function visiblePanelOverflows\(page\) \{.*?"
            r"page\s*\.locator\(\s*"
            r"'\[role=\"complementary\"\], "
            r"\[role=\"complementary\"\] \*'\s*\)"
            r"\s*\.evaluateAll\(\(elements\) =>.*?"
            r"element\.scrollWidth > element\.clientWidth \+ 1.*?"
            r"element\.scrollHeight > element\.clientHeight \+ 1",
        )
        self.assertRegex(
            script,
            r"(?s)for \(const capture of storyCaptures\) \{.*?"
            r"const overflows = await visiblePanelOverflows\(page\);.*?"
            r"storyOverflows\[capture\.mode\] = overflows;.*?"
            r"assert\.deepEqual\("
            r"overflows, \[\], `\$\{capture\.mode\} content is clipped`\);",
        )
        self.assertRegex(
            script,
            r"(?s)async function publishArtifacts\(artifacts\) \{.*?"
            r"await fs\.copyFile\(artifact\.target, artifact\.backup\);.*?"
            r"await fs\.rename\(artifact\.staged, artifact\.target\);.*?"
            r"catch \(publicationError\) \{.*?"
            r"const rollbackErrors = \[\];.*?"
            r"await fs\.rename\(artifact\.backup, artifact\.target\);.*?"
            r"await fs\.rm\(artifact\.target, \{ force: true \}\);.*?"
            r"rollbackErrors\.push\(rollbackError\);.*?"
            r"const rollbackFailure = new AggregateError\(\s*"
            r"\[publicationError, \.\.\.rollbackErrors\]",
        )
        self.assertIn("rollbackFailure.rollbackIncomplete = true;", script)
        self.assertIn(
            "preserveStagingRoot = error.rollbackIncomplete === true;",
            script,
        )

        gates = (
            script.index("assert.deepEqual(consoleErrors, []);"),
            script.index("assert.deepEqual(pageErrors, []);"),
            script.index("assert.deepEqual(requestFailures, []);"),
            script.index("assert.deepEqual(overflows, []"),
        )
        public_media_write = script.index("const images = [];")
        manifest_write = script.index("await fs.writeFile(")
        publication_start = script.index(
            "await publishArtifacts(publicationArtifacts)"
        )
        for gate in gates:
            self.assertLess(gate, public_media_write)
            self.assertLess(gate, manifest_write)
            self.assertLess(gate, publication_start)
