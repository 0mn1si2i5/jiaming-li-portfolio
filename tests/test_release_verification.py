from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.verification import browser, facts, privacy


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
                "A personal globe in use today",
                "Three ways to read the same place",
                "One system beneath the views",
                "Chronorbis: time, events, and place",
            ],
        )
        self.assertEqual(
            headings_by_locale["zh"],
            [
                "一颗正在使用的个人数字地球",
                "从同一地点进入三种观察方式",
                "三种视角下的同一套空间系统",
                "Chronorbis：让时间、事件与地点共存",
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


class TestStructuredFacts(unittest.TestCase):
    def test_mundus_uses_live_v11_deployed_revision(self) -> None:
        self.assertEqual(
            facts.EXPECTED_REVISIONS["Mundus"],
            "378fe528ca1c8f83f0280f83383b5e785e851285",
        )

        rules = facts.load_rules(Path("scripts/verification/facts.json"))
        self.assertEqual(
            [rule["id"] for rule in rules],
            [
                "mundus-personal-globe",
                "mundus-current-modes",
                "mundus-parchment-atlas",
                "mundus-shared-experience",
            ],
        )

    def test_source_revision_evidence_records_reviewed_commits(self) -> None:
        evidence = json.loads(
            Path(
                "docs/verification/evidence/source-revisions.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(evidence["schemaVersion"], 3)
        self.assertTrue(evidence["gatePassed"])
        revisions = {
            item["repository"]: item for item in evidence["repositories"]
        }
        self.assertEqual(
            revisions["Mundus"]["revision"],
            "378fe528ca1c8f83f0280f83383b5e785e851285",
        )
        self.assertEqual(set(revisions), {"Mundus"})
        for item in revisions.values():
            self.assertEqual(item["revisionType"], "immutable-commit")
            self.assertEqual(item["reviewStatus"], "reviewed")
            self.assertEqual(item["verificationMethod"], "git show")
            self.assertTrue(item["objectVerified"])
            self.assertNotIn("branch", item)
            self.assertNotIn("dirty", item)
            self.assertNotIn("expectedClean", item)

    def test_retained_fact_evidence_matches_the_catalog(self) -> None:
        rules = facts.load_rules(Path("scripts/verification/facts.json"))
        evidence = json.loads(
            Path(
                "docs/verification/evidence/task7-fact-assertions.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(evidence["schemaVersion"], 4)
        self.assertEqual(evidence["total"], len(rules))
        self.assertEqual(evidence["passed"], len(rules))
        self.assertEqual(
            [item["id"] for item in evidence["assertions"]],
            [item["id"] for item in rules],
        )
        self.assertTrue(all(item["passed"] for item in evidence["assertions"]))

    def test_mdx_visible_text_excludes_hidden_jsx_and_multiline_export(self) -> None:
        hidden = """
<div hidden>hidden claim</div>
<section aria-hidden="true">aria claim</section>
<aside style={{ display: "none" }}>display claim</aside>
<p style="visibility: hidden">visibility claim</p>
export const metadata = {
  claim: "export claim",
};
Visible claim.
"""
        visible = facts.extract_mdx_visible_text(hidden)
        for claim in (
            "hidden claim",
            "aria claim",
            "display claim",
            "visibility claim",
            "export claim",
        ):
            self.assertNotIn(claim, visible)
        self.assertIn("Visible claim", visible)

    def test_mdx_visible_text_excludes_comments_and_imports(self) -> None:
        text = """---
title: hidden
---
import Demo from './Demo.astro'
<!-- secret claim -->
{/* another secret claim */}
Visible claim.
"""
        visible = facts.extract_mdx_visible_text(text)
        self.assertIn("Visible claim", visible)
        self.assertNotIn("secret claim", visible)
        self.assertNotIn("import Demo", visible)

    def test_astro_semantics_include_only_rendered_model_fields(self) -> None:
        source = """---
const modes = [
  {
    title: { en: 'Rendered title', zh: '已渲染标题' },
    unused: 'unused object field',
  },
];
const dead = { title: { en: 'dead constant' } };
---
{modes.map((mode) => (
  <Localized {...mode.title} />
))}
"""
        self.assertTrue(
            hasattr(facts, "extract_astro_rendered_semantics"),
            "Astro rendered-semantics extractor is required",
        )

        semantic = facts.extract_astro_rendered_semantics(source)

        self.assertIn("Rendered title", semantic)
        self.assertIn("已渲染标题", semantic)
        self.assertNotIn("unused object field", semantic)
        self.assertNotIn("dead constant", semantic)

    def test_astro_frontmatter_scanner_ignores_commented_const(self) -> None:
        source = """---
const modes = [
  { title: { en: 'Real // title', zh: 'Real /* title */' } },
];
// const modes = [{ title: { en: 'Line-comment fake' } }];
/*
const modes = [{ title: { en: 'Block-comment fake' } }];
*/
---
{modes.map((mode) => (
  <Localized {...mode.title} />
))}
"""

        semantic = facts.extract_astro_rendered_semantics(source)

        self.assertIn("Real // title", semantic)
        self.assertIn("Real /* title */", semantic)
        self.assertNotIn("Line-comment fake", semantic)
        self.assertNotIn("Block-comment fake", semantic)

    def test_astro_literal_parser_rejects_unknown_and_trailing_tokens(
        self,
    ) -> None:
        for literal in (
            "{ title: 'accepted' } @",
            "{ title: 'accepted' } false",
        ):
            with self.subTest(literal=literal):
                with self.assertRaises(ValueError):
                    facts._AstroLiteralParser(literal).parse()

    def test_astro_literal_parser_accepts_only_supported_identifiers(
        self,
    ) -> None:
        self.assertEqual(
            facts._AstroLiteralParser("[true, false, null]").parse(),
            [True, False, None],
        )
        with self.assertRaises(ValueError):
            facts._AstroLiteralParser(
                "{ title: unknownIdentifier }"
            ).parse()

    def test_astro_models_reject_trailing_declaration_syntax(self) -> None:
        source = """---
const model = { title: 'Trailing declaration token' } unexpected();
---
<h2>{model.title}</h2>
"""

        semantic = facts.extract_astro_rendered_semantics(source)

        self.assertNotIn("Trailing declaration token", semantic)

    def test_astro_semantics_include_only_consumed_alt_fields(self) -> None:
        source = """---
const modes = [
  {
    alt: { en: 'First alt', zh: '第一条替代文本' },
    href: 'https://invalid.example/first',
  },
  {
    alt: { en: 'Second alt', zh: '第二条替代文本' },
    href: 'https://invalid.example/second',
  },
];
const defaultMode = modes[0];
---
<img alt={defaultMode.alt.en} />
{modes.map((mode) => (
  <button data-alt-en={mode.alt.en} data-alt-zh={mode.alt.zh} />
))}
"""
        self.assertTrue(
            hasattr(facts, "extract_astro_rendered_semantics"),
            "Astro rendered-semantics extractor is required",
        )

        semantic = facts.extract_astro_rendered_semantics(source)

        for value in (
            "First alt",
            "第一条替代文本",
            "Second alt",
            "第二条替代文本",
        ):
            self.assertIn(value, semantic)
        self.assertNotIn("https://invalid.example", semantic)

    def test_astro_semantics_exclude_hidden_content_and_hidden_references(
        self,
    ) -> None:
        source = """---
const content = {
  visible: 'Visible model value',
  hidden: 'Hidden model value',
};
---
<p>{content.visible}</p>
<div hidden>{content.hidden} hidden literal</div>
<section aria-hidden="true">aria hidden literal</section>
<aside style={{ display: "none" }}>display hidden literal</aside>
"""
        self.assertTrue(
            hasattr(facts, "extract_astro_rendered_semantics"),
            "Astro rendered-semantics extractor is required",
        )

        semantic = facts.extract_astro_rendered_semantics(source)

        self.assertIn("Visible model value", semantic)
        for value in (
            "Hidden model value",
            "hidden literal",
            "aria hidden literal",
            "display hidden literal",
        ):
            self.assertNotIn(value, semantic)

    def test_astro_semantics_exclude_hidden_self_closing_references(
        self,
    ) -> None:
        source = """---
const model = {
  hiddenLocalized: 'Hidden localized token',
  hiddenImage: 'Hidden image token',
  hiddenInput: 'Hidden input token',
  visible: 'Visible sibling token',
};
---
<Localized hidden {...model.hiddenLocalized} />
<img aria-hidden="true" alt={model.hiddenImage} />
<input style={{ display: 'none' }} data-alt={model.hiddenInput} />
<p>{model.visible}</p>
"""

        semantic = facts.extract_astro_rendered_semantics(source)

        self.assertIn("Visible sibling token", semantic)
        for value in (
            "Hidden localized token",
            "Hidden image token",
            "Hidden input token",
        ):
            self.assertNotIn(value, semantic)

    def test_claim_semantics_routes_mdx_and_astro_sources(self) -> None:
        mdx = """---
title: hidden frontmatter
---
Visible MDX claim.
"""
        astro = """---
const model = { title: 'Rendered Astro claim' };
---
<h2>{model.title}</h2>
"""
        self.assertTrue(
            hasattr(facts, "extract_claim_semantics"),
            "Claim source routing is required",
        )

        mdx_semantic = facts.extract_claim_semantics("project.mdx", mdx)
        astro_semantic = facts.extract_claim_semantics("story.astro", astro)

        self.assertIn("Visible MDX claim", mdx_semantic)
        self.assertNotIn("hidden frontmatter", mdx_semantic)
        self.assertIn("Rendered Astro claim", astro_semantic)

    def test_source_semantics_exclude_comments_and_unrelated_strings(self) -> None:
        source = """
// category: temporal
const decoy = "category: temporal";
const mode = { category: "spatial" };
"""
        semantic = facts.extract_source_semantics(source)
        self.assertNotIn("category: temporal", semantic)
        self.assertIn('category: "spatial"', semantic)

    def test_source_semantics_normalize_wrapped_evidence(self) -> None:
        semantic = facts.extract_source_semantics(
            "preserved the intended\n  selected point while switching modes"
        )

        self.assertIn(
            "preserved the intended selected point while switching modes",
            semantic,
        )

    def test_json_path_checks_structure_not_unrelated_literal(self) -> None:
        document = {"note": '"spriteVersionNumber": 2', "spriteVersionNumber": 1}
        rule = {"type": "json_path", "path": ["spriteVersionNumber"], "equals": 2}
        self.assertFalse(facts.match_json_rules(document, [rule]))

    def test_fact_catalog_uses_fewer_atomic_product_claims(self) -> None:
        rules = facts.load_rules(Path("scripts/verification/facts.json"))

        self.assertEqual(len(rules), 4)
        self.assertTrue(
            all(
                len(rule["claims"]) == 3
                and {claim["locale"] for claim in rule["claims"]}
                == {"en", "zh", "story"}
                for rule in rules
            )
        )
        self.assertTrue(
            all(
                evidence["rules"]
                for rule in rules
                for evidence in rule["evidence"]
            )
        )
        rule_ids = {rule["id"] for rule in rules}
        self.assertEqual(
            rule_ids,
            {
                "mundus-personal-globe",
                "mundus-current-modes",
                "mundus-parchment-atlas",
                "mundus-shared-experience",
            },
        )
        self.assertNotIn(
            "Chronorbis",
            json.dumps(rules, ensure_ascii=False),
        )

    def test_each_public_statement_has_claim_and_evidence_coverage(self) -> None:
        rules = {
            rule["id"]: rule
            for rule in facts.load_rules(Path("scripts/verification/facts.json"))
        }
        expected = {
            "mundus-personal-globe": {
                "claims": {
                    "public personal globe",
                    "same geographic context",
                    "read the result with its source and method",
                    "share that state",
                    "已经公开的个人数字地球",
                    "同一个地理上下文",
                    "阅读结果及其来源与方法",
                    "分享当前状态",
                    "Three views of the same globe",
                    "同一颗地球上的三种观察方式",
                },
                "evidence": {
                    "long-lived personal digital globe",
                    "different scientific lenses",
                    "explicit about its methods",
                },
            },
            "mundus-current-modes": {
                "claims": {
                    "Other Side",
                    "selected point through Earth to its antipode",
                    "Development, Unpacked",
                    "published HDI",
                    "Sunline",
                    "day-night boundary",
                    "地球另一端",
                    "沿地心找到所选地点的对跖点",
                    "发展的不同侧面",
                    "已发布 HDI",
                    "日照线",
                    "昼夜边界",
                },
                "evidence": {
                    "calculates exact antipodal endpoints",
                    "compares reported HDI",
                    "visualizes the day-night boundary",
                },
            },
            "mundus-parchment-atlas": {
                "claims": {
                    "represented cities at both ends",
                    "shared globe and location state",
                    "两端收录城市之间的关系",
                    "共享的地球与地点状态",
                    "Parchment Atlas · Preview",
                    "Parchment Atlas · 预览",
                    "through-Earth relationship",
                    "穿过地球的两端空间关系",
                },
                "evidence": {
                    "Parchment Atlas",
                    "bilateral city relations",
                    "Natural Earth vector globe",
                },
            },
            "mundus-shared-experience": {
                "claims": {
                    "same globe and location context",
                    "Reviewed data snapshots and hashes",
                    "static delivery",
                    "public build reproducible",
                    "共用同一颗地球和地点上下文",
                    "经过审核的数据快照和哈希",
                    "静态交付",
                    "线上构建可以复现",
                    "current public views",
                    "当前公开界面",
                },
                "evidence": {
                    "static, one-Canvas architecture",
                    "SHA-256",
                    "selected point while switching modes",
                    "build/artifact verification",
                    "literal subpath gate is closed",
                },
            },
        }

        self.assertEqual(set(rules), set(expected))
        for fact_id, coverage in expected.items():
            with self.subTest(fact_id=fact_id):
                assertion = rules[fact_id]
                self.assertIsInstance(assertion["evidence"], list)
                claim_values = {
                    value
                    for claim in assertion["claims"]
                    for rule in claim["rules"]
                    for value in rule.get("values", [])
                }
                evidence_values = {
                    value
                    for evidence in assertion["evidence"]
                    for rule in evidence["rules"]
                    for value in rule.get("values", [])
                }
                self.assertEqual(claim_values, coverage["claims"])
                self.assertEqual(evidence_values, coverage["evidence"])

    def test_fact_catalog_rejects_missing_story_claim(self) -> None:
        catalog = {
            "schemaVersion": 2,
            "assertions": [
                {
                    "id": "missing-story",
                    "claims": [
                        {"locale": "en", "source": "a", "rules": []},
                        {"locale": "zh", "source": "a", "rules": []},
                    ],
                    "evidence": {
                        "repository": "Mundus",
                        "source": "README.md",
                        "rules": [{"type": "contains", "value": "evidence"}],
                    },
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "facts.json"
            path.write_text(json.dumps(catalog), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "en, zh, and story"):
                facts.load_rules(path)

            catalog["assertions"][0]["claims"].extend(
                [
                    {"locale": "story", "source": "a", "rules": []},
                    {"locale": "en", "source": "a", "rules": []},
                ]
            )
            path.write_text(json.dumps(catalog), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "en, zh, and story"):
                facts.load_rules(path)

    def test_all_semantic_rules_must_match(self) -> None:
        rules = [
            {"type": "contains", "value": "three modes"},
            {"type": "contains_all", "values": ["spatial", "human", "temporal"]},
        ]

        self.assertFalse(
            facts.match_rules("three modes: spatial only", rules)
        )
        self.assertTrue(
            facts.match_rules(
                "three modes: spatial, human, temporal",
                rules,
            )
        )

    def test_read_at_revision_ignores_working_tree_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(
                ["git", "-C", str(root), "config", "user.email", "test@example.com"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(root), "config", "user.name", "Test"],
                check=True,
            )
            source = root / "README.md"
            source.write_text("reviewed evidence", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "README.md"], check=True)
            subprocess.run(
                ["git", "-C", str(root), "commit", "-qm", "fixture"],
                check=True,
            )
            revision = facts.git(root, "rev-parse", "HEAD")
            source.write_text("unreviewed working tree", encoding="utf-8")

            observed = facts.read_at_revision(root, revision, "README.md")

        self.assertEqual(observed, "reviewed evidence")


class TestBrowserEvidence(unittest.TestCase):
    def write_bound_dist(self, evidence_root: Path, dist_root: Path) -> None:
        manifest_path = evidence_root / "browser-build.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in manifest["html"]:
            content = f"<html><body>{item['path']}</body></html>".encode()
            target = dist_root / item["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            item["sha256"] = hashlib.sha256(content).hexdigest()
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    def test_generated_route_contract_uses_about_not_notes(self) -> None:
        self.assertEqual(
            browser.DIST_HTML_FILES,
            (
                "index.html",
                "about/index.html",
                "projects/dialogtree/index.html",
                "projects/mundus/index.html",
                "projects/nbti/index.html",
                "projects/side-b/index.html",
            ),
        )
        self.assertNotIn("notes/index.html", browser.DIST_HTML_FILES)

    def test_each_scenario_requires_exact_identity_values(self) -> None:
        project = Path(__file__).parents[1]
        matrix = json.loads(
            (
                project / "docs/verification/evidence/browser-matrix.json"
            ).read_text(encoding="utf-8")
        )
        mutations = (
            ("route", "/wrong"),
            ("locale", "en"),
            ("theme", "light"),
            ("viewport", {"width": 1, "height": 1}),
            ("reducedMotion", False),
        )
        for field, value in mutations:
            with self.subTest(field=field):
                changed = json.loads(json.dumps(matrix))
                changed["scenarios"][2][field] = value
                self.assertIn(field, " ".join(browser.validate_matrix(changed)))

    def test_matrix_rejects_incorrect_pages_base_evidence(self) -> None:
        project = Path(__file__).parents[1]
        matrix = json.loads(
            (
                project / "docs/verification/evidence/browser-matrix.json"
            ).read_text(encoding="utf-8")
        )
        matrix["scenarios"][0]["pagesBaseCorrect"] = False

        errors = browser.validate_matrix(matrix)

        self.assertIn("pagesBaseCorrect", " ".join(errors))

    def test_matrix_rejects_missing_or_incorrect_mundus_preview_evidence(
        self,
    ) -> None:
        project = Path(__file__).parents[1]
        matrix = json.loads(
            (
                project / "docs/verification/evidence/browser-matrix.json"
            ).read_text(encoding="utf-8")
        )
        preview_fields = (
            "previewDefaultMode",
            "previewPointerModes",
            "previewKeyboardModes",
            "previewLinkTargetsCorrect",
            "previewSelectionSynchronized",
            "previewLayout",
            "previewMinTargetHeight",
            "previewTransitionDurationMs",
        )
        for item in matrix["scenarios"]:
            if not item["scenario"].startswith("mundus-"):
                continue
            item.update(
                {
                    "previewDefaultMode": "antipodes",
                    "previewPointerModes": [
                        "antipodes",
                        "development",
                        "sunline",
                    ],
                    "previewKeyboardModes": [
                        "antipodes",
                        "development",
                        "sunline",
                    ],
                    "previewLinkTargetsCorrect": True,
                    "previewSelectionSynchronized": True,
                    "previewLayout": (
                        "vertical"
                        if item["viewport"]["width"] <= 760
                        else "columns"
                    ),
                    "previewMinTargetHeight": 44,
                    "previewTransitionDurationMs": (
                        0 if item["reducedMotion"] else 100
                    ),
                }
            )

        self.assertEqual(browser.validate_matrix(matrix), [])

        mundus_indexes = [
            i
            for i, item in enumerate(matrix["scenarios"])
            if item["scenario"].startswith("mundus-")
        ]
        scenario_indexes = {
            item["scenario"]: i
            for i, item in enumerate(matrix["scenarios"])
        }
        desktop_index = scenario_indexes["mundus-en-light-1440"]
        mobile_index = next(
            i
            for i, item in enumerate(matrix["scenarios"])
            if item["scenario"] == "mundus-en-light-390"
        )
        reduced_index = scenario_indexes["mundus-zh-dark-desktop"]

        for index in mundus_indexes:
            scenario = matrix["scenarios"][index]["scenario"]
            for field in preview_fields:
                with self.subTest(
                    scenario=scenario,
                    field=field,
                    mutation="missing",
                ):
                    changed = json.loads(json.dumps(matrix))
                    del changed["scenarios"][index][field]
                    errors = " ".join(browser.validate_matrix(changed))
                    self.assertIn(field, errors)

        mutations = (
            (desktop_index, "previewDefaultMode", "development"),
            (desktop_index, "previewPointerModes", ["antipodes"]),
            (
                desktop_index,
                "previewKeyboardModes",
                ["antipodes", "development"],
            ),
            (desktop_index, "previewLinkTargetsCorrect", False),
            (desktop_index, "previewSelectionSynchronized", False),
            (mobile_index, "previewLayout", "columns"),
            (mobile_index, "previewMinTargetHeight", 43),
            (reduced_index, "previewTransitionDurationMs", 100),
        )
        for index, field, value in mutations:
            scenario = matrix["scenarios"][index]["scenario"]
            with self.subTest(
                scenario=scenario,
                field=field,
                mutation="invalid",
            ):
                changed = json.loads(json.dumps(matrix))
                changed["scenarios"][index][field] = value
                self.assertIn(field, " ".join(browser.validate_matrix(changed)))

    def write_json(self, root: Path, name: str, value: object) -> None:
        (root / name).write_text(json.dumps(value), encoding="utf-8")

    def test_validator_rejects_inconsistent_network_summary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_json(
                root,
                "browser-network.json",
                {
                    "schemaVersion": 1,
                    "requestCount": 2,
                    "failureCount": 0,
                    "failures": [],
                    "statusCounts": {"200": 1},
                    "resourceTypeCounts": {"Document": 1},
                    "requests": [
                        {
                            "method": "GET",
                            "path": "/",
                            "resourceType": "Document",
                            "status": 200,
                        }
                    ],
                },
            )

            errors = browser.validate_network(root / "browser-network.json")

        self.assertIn("requestCount", " ".join(errors))

    def test_screenshot_manifest_checks_sha256(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / "capture.webp"
            image.write_bytes(b"image")
            manifest = {
                "schemaVersion": 1,
                "screenshots": [
                    {
                        "scenario": "home-en-light-1440",
                        "path": "capture.webp",
                        "width": 1,
                        "height": 1,
                        "sha256": hashlib.sha256(b"different").hexdigest(),
                    }
                ],
            }
            self.write_json(root, "screenshots.json", manifest)

            errors = browser.validate_screenshots(
                root / "screenshots.json",
                root,
                check_dimensions=False,
            )

        self.assertIn("sha256", " ".join(errors))

    def test_screenshot_manifest_rejects_path_escape_symlink_and_wrong_filename(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assets = root / "assets"
            assets.mkdir()
            outside = root / "outside.webp"
            outside.write_bytes(b"outside")
            link = assets / "linked.webp"
            link.symlink_to(outside)
            base = {
                "schemaVersion": 1,
                "screenshots": [
                    {
                        "scenario": "home-en-light-1440",
                        "path": "",
                        "width": 1,
                        "height": 1,
                        "sha256": hashlib.sha256(b"outside").hexdigest(),
                    }
                ],
            }
            cases = {
                "../outside.webp": "path is unsafe",
                str(outside): "path is unsafe",
                "linked.webp": "symlink is forbidden",
                "wrong.webp": "filename is invalid",
            }
            for value, expected_error in cases.items():
                with self.subTest(path=value):
                    base["screenshots"][0]["path"] = value
                    manifest = root / "screenshots.json"
                    manifest.write_text(json.dumps(base), encoding="utf-8")
                    errors = browser.validate_screenshots(
                        manifest,
                        assets,
                        check_dimensions=False,
                    )
                    self.assertIn(expected_error, " ".join(errors))

    def test_real_evidence_is_consistent_and_missing_scenario_fails(self) -> None:
        project = Path(__file__).parents[1]
        source = project / "docs/verification/evidence"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for path in source.glob("browser-*.json"):
                shutil.copy2(path, root / path.name)
            dist = root / "dist"
            self.write_bound_dist(root, dist)
            self.assertEqual(
                browser.validate_all(
                    root,
                    project / "docs/verification/assets",
                    dist,
                ),
                [],
            )
            matrix_path = root / "browser-matrix.json"
            matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
            matrix["scenarios"].pop()
            matrix_path.write_text(json.dumps(matrix), encoding="utf-8")

            errors = browser.validate_all(
                root,
                project / "docs/verification/assets",
                dist,
            )

        self.assertIn("scenario order", " ".join(errors))

    def test_old_browser_evidence_fails_for_changed_dist_html(self) -> None:
        project = Path(__file__).parents[1]
        evidence = project / "docs/verification/evidence"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            copied_evidence = root / "evidence"
            copied_dist = root / "dist"
            copied_evidence.mkdir()
            for path in evidence.glob("browser-*.json"):
                shutil.copy2(path, copied_evidence / path.name)
            self.write_bound_dist(copied_evidence, copied_dist)

            self.assertEqual(
                browser.validate_all(
                    copied_evidence,
                    project / "docs/verification/assets",
                    copied_dist,
                ),
                [],
            )
            html = copied_dist / "projects/mundus/index.html"
            html.write_text(
                html.read_text(encoding="utf-8") + "\n<!-- changed build -->\n",
                encoding="utf-8",
            )

            errors = browser.validate_all(
                copied_evidence,
                project / "docs/verification/assets",
                copied_dist,
            )

        self.assertIn("dist HTML digest mismatch", " ".join(errors))

    def test_browser_evidence_without_build_binding_fails_cleanly(self) -> None:
        project = Path(__file__).parents[1]
        evidence = project / "docs/verification/evidence"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for path in evidence.glob("browser-*.json"):
                if path.name != "browser-build.json":
                    shutil.copy2(path, root / path.name)

            errors = browser.validate_all(
                root,
                project / "docs/verification/assets",
                project / "dist",
            )

        self.assertIn(
            "browser-build.json: evidence is missing",
            errors,
        )

    def test_matrix_rejects_reordered_or_unsuccessful_scenario(self) -> None:
        project = Path(__file__).parents[1]
        matrix_path = project / "docs/verification/evidence/browser-matrix.json"
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
        matrix["scenarios"][0], matrix["scenarios"][1] = (
            matrix["scenarios"][1],
            matrix["scenarios"][0],
        )
        matrix["scenarios"][0]["brokenImageCount"] = 1
        matrix["scenarios"][4]["totalImageCount"] = 3
        matrix["scenarios"][4]["productVisualCount"] = 2
        errors = browser.validate_matrix(matrix)
        self.assertIn("order", " ".join(errors))
        self.assertIn("brokenImageCount", " ".join(errors))
        self.assertIn("image count", " ".join(errors))
        self.assertIn("productVisualCount", " ".join(errors))

    def test_console_requires_structured_levels_and_no_failures(self) -> None:
        console = {
            "schemaVersion": 1,
            "messageCount": 1,
            "errorCount": 1,
            "warningCount": 0,
            "messages": [{"level": "error", "text": "boom"}],
        }
        errors = browser.validate_console(console)
        self.assertIn("console must be empty", " ".join(errors))


class TestPrivacyScan(unittest.TestCase):
    def test_scan_recursively_decodes_html_entities_and_urls(self) -> None:
        encoded = (
            "%2526%2523x2F%253BUsers%2526%2523x2F%253Bexample"
            "%2526%2523x2F%253Bprivate"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text(encoded, encoding="utf-8")
            findings = privacy.scan_dist(root)
        self.assertIn("absolute path", " ".join(findings))
    def test_scan_rejects_sensitive_bytes_in_fake_webp(self) -> None:
        samples = (
            b"/Users/example/private/file",
            b"http://127.0.0.1:4321/private",
            b"Bearer abcdefghijklmnopqrstuvwxyz012345",
            b"secret=QWxhZGRpbjpvcGVuIHNlc2FtZV9yYW5kb21fMTIzNDU2",
        )
        for payload in samples:
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "fake.webp").write_bytes(
                    b"RIFF\x20\x00\x00\x00WEBPVP8 " + b"\xff\xfe\x00" + payload
                )
                self.assertTrue(privacy.scan_dist(root))
    def test_scan_requires_built_dist_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "dist"

            self.assertEqual(
                privacy.scan_dist(missing),
                ["dist: output directory is missing"],
            )

    def test_scan_rejects_paths_internal_urls_credentials_and_entropy(self) -> None:
        samples = {
            "path": "source=/Users/example/private/file.txt",
            "internal": "http://127.0.0.1:4321/private",
            "internal-domain": "https://service.example.internal/api",
            "credential": "Bearer abcdefghijklmnopqrstuvwxyz012345",
            "entropy": "secret=QWxhZGRpbjpvcGVuIHNlc2FtZV9yYW5kb21fMTIzNDU2",
        }
        for name, text in samples.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "index.html").write_text(text, encoding="utf-8")

                findings = privacy.scan_dist(root)

                self.assertTrue(findings)

    def test_scan_allows_normal_built_assets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text(
                '<link href="/jiaming-li-portfolio/_astro/index.Bw6D59th.css">'
                '<img src="/jiaming-li-portfolio/media/side-b/01-parse-link.webp">',
                encoding="utf-8",
            )

            self.assertEqual(privacy.scan_dist(root), [])


if __name__ == "__main__":
    unittest.main()
