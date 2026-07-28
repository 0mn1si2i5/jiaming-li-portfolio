from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.verification import browser, facts, privacy


class TestStructuredFacts(unittest.TestCase):
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

    def test_source_semantics_exclude_comments_and_unrelated_strings(self) -> None:
        source = """
// category: temporal
const decoy = "category: temporal";
const mode = { category: "spatial" };
"""
        semantic = facts.extract_source_semantics(source)
        self.assertNotIn("category: temporal", semantic)
        self.assertIn('category: "spatial"', semantic)

    def test_json_path_checks_structure_not_unrelated_literal(self) -> None:
        document = {"note": '"spriteVersionNumber": 2', "spriteVersionNumber": 1}
        rule = {"type": "json_path", "path": ["spriteVersionNumber"], "equals": 2}
        self.assertFalse(facts.match_json_rules(document, [rule]))

    def test_fact_catalog_keeps_31_bidirectional_rules(self) -> None:
        rules = facts.load_rules(Path("scripts/verification/facts.json"))

        self.assertEqual(len(rules), 31)
        self.assertTrue(all(rule["claim"]["rules"] for rule in rules))
        self.assertTrue(all(rule["evidence"]["rules"] for rule in rules))

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
                        "scenario": "home-en-light-desktop",
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
                        "scenario": "home-en-light-desktop",
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
            self.assertEqual(
                browser.validate_all(
                    root,
                    project / "docs/verification/assets",
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
            )

        self.assertIn("scenario order", " ".join(errors))

    def test_matrix_rejects_reordered_or_unsuccessful_scenario(self) -> None:
        project = Path(__file__).parents[1]
        matrix_path = project / "docs/verification/evidence/browser-matrix.json"
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
        matrix["scenarios"][0], matrix["scenarios"][1] = (
            matrix["scenarios"][1],
            matrix["scenarios"][0],
        )
        matrix["scenarios"][0]["brokenImageCount"] = 1
        errors = browser.validate_matrix(matrix)
        self.assertIn("order", " ".join(errors))
        self.assertIn("brokenImageCount", " ".join(errors))

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
                '<link href="/_astro/index.Bw6D59th.css">',
                encoding="utf-8",
            )

            self.assertEqual(privacy.scan_dist(root), [])


if __name__ == "__main__":
    unittest.main()
