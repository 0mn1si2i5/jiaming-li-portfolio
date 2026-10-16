from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.verification import facts


class TestStructuredFacts(unittest.TestCase):
    def test_mundus_uses_the_pinned_deployed_revision(self) -> None:
        self.assertEqual(
            facts.EXPECTED_REVISIONS["Mundus"],
            "67fdcf8f69fd34bf06f314b3b6d6f3f92f99b77d",
        )

        rules = facts.load_rules(Path("scripts/verification/facts.json"))
        self.assertEqual(
            [rule["id"] for rule in rules],
            [
                "mundus-personal-globe",
                "mundus-shared-modes",
                "mundus-live-preview",
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
            "67fdcf8f69fd34bf06f314b3b6d6f3f92f99b77d",
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
                "mundus-shared-modes",
                "mundus-live-preview",
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
                    "reads the result with its source and method",
                    "share that state as a link",
                    "已经公开的个人数字地球",
                    "同一个地理上下文",
                    "阅读结果及其来源与方法",
                    "把当前状态作为链接分享出去",
                    "Preview",
                    "预览",
                },
                "evidence": {
                    "long-lived personal digital globe",
                    "different scientific lenses",
                    "explicit about its methods",
                },
            },
            "mundus-shared-modes": {
                "claims": {
                    "One 3D globe and one selected place",
                    "Switching modes keeps the place",
                    "A missing value stays marked as missing",
                    "One About dialog that lists the methods, data sources, and licences",
                    "Share links that reopen the same mode, place, and settings",
                    "一颗三维地球和一个选中的地点",
                    "切换模式时，地点保持不变",
                    "缺失的数据标为缺失",
                    "列出所有方法、数据来源和许可",
                    "打开后回到同一个模式、地点和设置",
                    "Main modes on the live site",
                    "线上的主要模式",
                },
                "evidence": {
                    "move to another observation while keeping the selected place",
                    "share the state",
                    "Methods, data sources, licences and software notices live in one About dialog",
                    "turn missing values into zero",
                    "missing fields remain explicit",
                },
            },
            "mundus-live-preview": {
                "claims": {
                    "I keep adding modes to it",
                    "我会继续给它增加模式",
                    "loaded from the live site",
                    "replaced each time Mundus is deployed",
                    "从线上版本读取",
                    "每次部署后都会更新",
                },
                "evidence": {
                    "node scripts/capture-portfolio-previews.mjs dist",
                    "--require-previews",
                    "previews/manifest.json",
                    "follows the tier in `modeRegistry.ts`",
                },
            },
            "mundus-shared-experience": {
                "claims": {
                    "static site with no backend or database",
                    "pinned by SHA-256 hashes",
                    "only change after I review a new version",
                    "public build can be reproduced",
                    "没有后端和数据库的静态网站",
                    "SHA-256 哈希固定",
                    "审核过新版本后才会更换",
                    "线上构建可以从仓库复现",
                    "Opens Mundus in a new tab",
                    "在新标签页打开 Mundus",
                },
                "evidence": {
                    "static browser application with one shared 3D globe and no backend or database",
                    "pin upstream URLs and SHA-256 hashes",
                    "fail-closed",
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

    def test_case_copy_must_not_name_a_registered_mode(self) -> None:
        registry = """
export const MODE_DEFINITIONS = {
  antipodes: {
    title: { zh: '地球另一端', en: 'Other Side' },
  },
  newmode: {
    title: { zh: '新观察', en: 'New Lens' },
  },
};
"""
        titles = facts.mode_titles(registry)
        self.assertEqual(titles, ["地球另一端", "Other Side", "新观察", "New Lens"])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in facts.MODE_AGNOSTIC_SOURCES:
                (root / source).parent.mkdir(parents=True, exist_ok=True)
                (root / source).write_text("A shared globe.", encoding="utf-8")
            self.assertEqual(facts.find_mode_titles(root, titles), [])

            case = root / facts.MODE_AGNOSTIC_SOURCES[0]
            case.write_text("summary: Try New Lens today.", encoding="utf-8")
            errors = facts.find_mode_titles(root, titles)
        self.assertEqual(len(errors), 1)
        self.assertIn("'New Lens'", errors[0])

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
