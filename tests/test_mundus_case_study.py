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
                "Three released modes",
                "The shared spatial base",
                "Chronorbis",
            ],
        )
        self.assertEqual(
            headings_by_locale["zh"],
            [
                "一颗持续扩展的个人数字地球",
                "三种已上线模式",
                "共用的空间基座",
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

    def test_mundus_story_defines_three_accessible_linked_previews(self) -> None:
        story = (
            self.project / "src/components/MundusStory.astro"
        ).read_text(encoding="utf-8")

        modes_start = story.find("const modes = [")
        self.assertNotEqual(modes_start, -1)
        modes_end = story.find("] as const", modes_start)
        self.assertNotEqual(modes_end, -1)
        modes_source = story[modes_start:modes_end]
        mode_matches = list(
            re.finditer(r"\bid:\s*'([^']+)'", modes_source)
        )
        mode_ids = [match.group(1) for match in mode_matches]
        self.assertEqual(
            mode_ids,
            ["antipodes", "development", "sunline"],
        )
        self.assertEqual(len(mode_ids), len(mode_matches))
        mode_blocks = {
            mode_id: modes_source[
                match.start() : (
                    mode_matches[index + 1].start()
                    if index + 1 < len(mode_matches)
                    else len(modes_source)
                )
            ]
            for index, (mode_id, match) in enumerate(
                zip(mode_ids, mode_matches)
            )
        }
        expected_modes = {
            "antipodes": (
                "title: { en: 'Other Side', zh: '地球另一端' }",
                "description: { en: 'Spherical relationships', "
                "zh: '球面空间关系' }",
                "image: '/media/mundus/other-side-detail.webp'",
                "The Mundus Other Side mode showing the through-Earth "
                "relationship between two endpoints.",
                "Mundus“地球另一端”模式，展示穿过地球的两端空间关系。",
                "https://0mn1si2i5.github.io/Mundus/?mode=antipodes&v=1",
            ),
            "development": (
                "title: { en: 'Development, Unpacked', zh: '发展的不同侧面' }",
                "description: { en: 'Development structure over time', "
                "zh: '发展结构与时间变化' }",
                "image: '/media/mundus/development.webp'",
                "The Mundus Development mode comparing published development "
                "indicators on the globe.",
                "Mundus“发展的不同侧面”模式，在地球上比较已发布的发展指标。",
                "https://0mn1si2i5.github.io/Mundus/?mode=development"
                "&indicator=hdi&year=2023&v=1",
            ),
            "sunline": (
                "title: { en: 'Sunline', zh: '日照线' }",
                "description: { en: 'Time and sunlight', zh: '时间与日照变化' }",
                "image: '/media/mundus/sunline.webp'",
                "The Mundus Sunline mode showing sunlight and the day-night "
                "boundary on the globe.",
                "Mundus“日照线”模式，展示地球上的日照与昼夜边界。",
                "https://0mn1si2i5.github.io/Mundus/?mode=sunline&v=1",
            ),
        }
        for mode_id, block in mode_blocks.items():
            for token in expected_modes[mode_id]:
                with self.subTest(mode=mode_id, token=token):
                    self.assertIn(token, block)

        self.assertEqual(story.count("<img"), 1)
        for token in (
            "const defaultMode = modes[0]",
            "href={defaultMode.href}",
            "src={asset(defaultMode.image)}",
            "alt={defaultMode.alt.en}",
            'aria-labelledby="mundus-preview-antipodes '
            'mundus-preview-new-tab-label"',
            'role="tablist"',
            'role="tab"',
            'aria-controls="mundus-preview-panel"',
            'aria-selected={index === 0 ? "true" : "false"}',
            "tabindex={index === 0 ? 0 : -1}",
            "data-src={asset(mode.image)}",
            "data-href={mode.href}",
            "data-alt-en={mode.alt.en}",
            "data-alt-zh={mode.alt.zh}",
            'target="_blank"',
            'rel="noopener noreferrer"',
            "const panel = preview.querySelector<HTMLElement>("
            "'#mundus-preview-panel')",
            "const candidate = new Image()",
            "candidate.onload = () => {",
            "candidate.onerror = () => {",
            "const syncLocale = (tab: HTMLButtonElement) => {",
            "new MutationObserver",
            "syncLocale(tabs[0]);",
            "ArrowLeft",
            "ArrowRight",
            "ArrowUp",
            "ArrowDown",
            "Home",
            "End",
        ):
            self.assertIn(token, story)

        panel_match = re.search(
            r'<div\b(?=[^>]*\bid="mundus-preview-panel")'
            r'(?=[^>]*\brole="tabpanel")'
            r'(?=[^>]*\baria-labelledby="mundus-preview-antipodes")'
            r"[^>]*>(?P<body>.*?)</div>",
            story,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(panel_match)
        self.assertRegex(
            panel_match.group("body"),
            r'(?s)<a\b(?=[^>]*\bdata-preview-link\b)'
            r'(?=[^>]*\baria-labelledby="mundus-preview-antipodes '
            r'mundus-preview-new-tab-label")[^>]*>.*?<img\b',
        )
        self.assertNotRegex(
            panel_match.group("body"),
            r"<a\b[^>]*\brole=",
        )

        onload_match = re.search(
            r"candidate\.onload = \(\) => \{(?P<body>.*?)"
            r"^\s*\};",
            story,
            flags=re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(onload_match)
        src_assignment = story.find(
            "candidate.src = src;",
            onload_match.end(),
        )
        self.assertNotEqual(src_assignment, -1)
        self.assertLess(onload_match.start(), src_assignment)
        onload = onload_match.group("body")
        update_tokens = (
            "image.src = src;",
            "link.href = href;",
            "item.setAttribute('aria-selected', String(selected));",
            "item.tabIndex = selected ? 0 : -1;",
            "panel.setAttribute('aria-labelledby', tab.id);",
            "`${tab.id} mundus-preview-new-tab-label`,",
            "syncLocale(tab);",
        )
        for token in update_tokens:
            self.assertIn(token, onload)
        self.assertRegex(
            onload,
            r"(?s)panel\.setAttribute\('aria-labelledby', tab\.id\);.*?"
            r"link\.setAttribute\(\s*'aria-labelledby',\s*"
            r"`\$\{tab\.id\} mundus-preview-new-tab-label`,\s*\);.*?"
            r"syncLocale\(tab\);",
        )
        self.assertNotIn("moveFocus", story)
        onerror_match = re.search(
            r"candidate\.onerror = \(\) => \{(?P<body>.*?)"
            r"^\s*\};",
            story,
            flags=re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(onerror_match)
        onerror = onerror_match.group("body")
        self.assertRegex(
            onerror,
            r"(?s)if \(\s*currentRequest !== requestId\s*\|\|\s*"
            r"document\.activeElement !== tab\s*\) return;.*?"
            r"const selected = tabs\.find\(.*?"
            r"item\.getAttribute\('aria-selected'\) === 'true'.*?"
            r"if \(selected\) selected\.focus\(\);",
        )
        for mutation in (
            "image.src",
            "link.href",
            "setAttribute",
            "tabIndex",
        ):
            self.assertNotIn(mutation, onerror)
        keydown_match = re.search(
            r"tab\.addEventListener\('keydown', \(event\) => \{"
            r"(?P<body>.*?)^\s*\}\);",
            story,
            flags=re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(keydown_match)
        keydown = keydown_match.group("body")
        prevent_default = keydown.find("event.preventDefault();")
        focus_next = keydown.find("tabs[next].focus();")
        activate_next = keydown.find("activate(tabs[next]);")
        self.assertNotEqual(prevent_default, -1)
        self.assertNotEqual(focus_next, -1)
        self.assertNotEqual(activate_next, -1)
        self.assertLess(prevent_default, focus_next)
        self.assertLess(focus_next, activate_next)
        observer_match = re.search(
            r"new MutationObserver\(\(\) => \{(?P<callback>.*?)"
            r"\}\)\.observe\((?P<options>.*?)\);",
            story,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(observer_match)
        self.assertRegex(
            observer_match.group("callback"),
            r"(?s)tab\.getAttribute\('aria-selected'\) === 'true'.*?"
            r"if \(selected\) syncLocale\(selected\);",
        )
        self.assertRegex(
            observer_match.group("options"),
            r"attributeFilter: \['data-locale'\]",
        )
        self.assertIn("syncLocale(tabs[0]);", story)
        self.assertRegex(
            story,
            r"(?s)@media \(prefers-reduced-motion: reduce\) \{.*?"
            r"\.preview-link img\s*\{\s*transition: none;",
        )

        expected = {
            "https://0mn1si2i5.github.io/Mundus/?mode=antipodes&v=1",
            "https://0mn1si2i5.github.io/Mundus/"
            "?mode=development&indicator=hdi&year=2023&v=1",
            "https://0mn1si2i5.github.io/Mundus/?mode=sunline&v=1",
        }
        self.assertEqual(
            {
                value.replace("&amp;", "&")
                for value in re.findall(
                    r"https://0mn1si2i5\.github\.io/Mundus/[^\"']+",
                    story,
                )
            },
            expected,
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
        for path in (
            "/media/mundus/other-side-detail.webp",
            "/media/mundus/development.webp",
            "/media/mundus/sunline.webp",
        ):
            self.assertIn(path, story)
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
                "story-development",
                "story-sunline",
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
            5,
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
