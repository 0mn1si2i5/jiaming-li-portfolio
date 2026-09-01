from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.verification import browser


_SCENARIO_META = {
    "home-en-light-1440": ("/", "en", "light", 1440, 900, False),
    "home-en-light-1024": ("/", "en", "light", 1024, 768, False),
    "home-zh-dark-768": ("/", "zh", "dark", 768, 1024, True),
    "home-zh-dark-390": ("/", "zh", "dark", 390, 844, True),
    "about-en-light-1440": ("/about", "en", "light", 1440, 900, False),
    "about-zh-dark-390": ("/about", "zh", "dark", 390, 844, True),
    "mundus-en-light-1440": ("/projects/mundus", "en", "light", 1440, 900, False),
    "mundus-zh-dark-desktop": ("/projects/mundus", "zh", "dark", 1440, 900, True),
    "mundus-en-light-390": ("/projects/mundus", "en", "light", 390, 844, False),
    "mundus-zh-dark-mobile": ("/projects/mundus", "zh", "dark", 390, 844, True),
    "bytedance-en-light-1440": (
        "/projects/bytedance-ai-data", "en", "light", 1440, 900, False,
    ),
    "bytedance-zh-dark-390": (
        "/projects/bytedance-ai-data", "zh", "dark", 390, 844, True,
    ),
}


def _build_scenario(name: str) -> dict[str, object]:
    route, locale, theme, width, height, reduced = _SCENARIO_META[name]
    scenario: dict[str, object] = {
        "scenario": name,
        "route": route,
        "locale": locale,
        "theme": theme,
        "viewport": {"width": width, "height": height},
        "overflow": False,
        "brokenImageCount": 0,
        "decodedImageCount": 0,
        "totalImageCount": 0,
        "focusableCount": 1,
        "focusVisible": True,
        "visibleTextLength": 100,
        "reducedMotion": reduced,
        "pagesBaseCorrect": True,
    }
    if name.startswith("home-"):
        scenario["totalImageCount"] = 4
        scenario["decodedImageCount"] = 4
        scenario["featured"] = ["DialogTree", "Mundus"]
        scenario["internship"] = ["Speech Evaluation & Data Tooling at ByteDance"]
        scenario["other"] = ["NBTI", "Side B", "dsh-handoff", "RSZ Namelist"]
        scenario["mediaCount"] = 0
    elif name.startswith("about-"):
        scenario["emailAddressCount"] = 2
        scenario["emailCopyButtonCount"] = 2
        scenario["emailCopySuccessVisible"] = True
        scenario["emailCopyFallbackVisible"] = True
        scenario["educationEntryCount"] = 2
    elif name.startswith("mundus-"):
        scenario["totalImageCount"] = 2
        scenario["decodedImageCount"] = 2
        scenario["productVisualCount"] = 1
        scenario["previewDefaultMode"] = "antipodes"
        scenario["previewPointerModes"] = ["antipodes", "development", "sunline"]
        scenario["previewKeyboardModes"] = ["antipodes", "development", "sunline"]
        scenario["previewLinkTargetsCorrect"] = True
        scenario["previewSelectionSynchronized"] = True
        scenario["previewLayout"] = "vertical" if width <= 760 else "columns"
        scenario["previewMinTargetHeight"] = 44
        scenario["previewTransitionDurationMs"] = 0 if reduced else 160
    elif name.startswith("bytedance-"):
        scenario["responsibilityModuleCount"] = 3
        scenario["comparisonCellCount"] = 4
        scenario["sharedQcGroupCount"] = 1
        scenario["mediaSectionCount"] = 0
    if reduced:
        scenario["activeAnimationCount"] = 0
    return scenario


def _build_valid_matrix() -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "scenarios": [
            _build_scenario(name) for name in browser.REQUIRED_SCENARIOS
        ],
    }


class TestBrowserEvidence(unittest.TestCase):
    def load_matrix_with_preview_evidence(self) -> dict[str, object]:
        project = Path(__file__).parents[1]
        matrix = json.loads(
            (
                project / "docs/verification/evidence/browser-matrix.json"
            ).read_text(encoding="utf-8")
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
        return matrix

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
                "projects/bytedance-ai-data/index.html",
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

    def test_matrix_rejects_malformed_mundus_preview_measurements(
        self,
    ) -> None:
        matrix = self.load_matrix_with_preview_evidence()
        scenario_index = next(
            index
            for index, item in enumerate(matrix["scenarios"])
            if item["scenario"] == "mundus-en-light-390"
        )
        valid_floats = json.loads(json.dumps(matrix))
        valid_floats["scenarios"][scenario_index]["viewport"]["width"] = 390.0
        valid_floats["scenarios"][scenario_index][
            "previewMinTargetHeight"
        ] = 44.0
        self.assertEqual(browser.validate_matrix(valid_floats), [])

        viewport_mutations = (
            None,
            "390",
            {},
            {"height": 844},
            {"width": "390", "height": 844},
            {"width": True, "height": 844},
            {"width": float("nan"), "height": 844},
            {"width": float("inf"), "height": 844},
            {"width": float("-inf"), "height": 844},
        )
        for viewport in viewport_mutations:
            with self.subTest(field="viewport", value=viewport):
                changed = json.loads(json.dumps(matrix))
                changed["scenarios"][scenario_index]["viewport"] = viewport
                errors = " ".join(browser.validate_matrix(changed))
                self.assertIn("viewport", errors)
                self.assertIn("previewLayout", errors)

        changed = json.loads(json.dumps(matrix))
        del changed["scenarios"][scenario_index]["viewport"]
        errors = " ".join(browser.validate_matrix(changed))
        self.assertIn("viewport", errors)
        self.assertIn("previewLayout", errors)

        for height in (
            True,
            float("nan"),
            float("inf"),
            float("-inf"),
        ):
            with self.subTest(field="previewMinTargetHeight", value=height):
                changed = json.loads(json.dumps(matrix))
                changed["scenarios"][scenario_index][
                    "previewMinTargetHeight"
                ] = height
                errors = " ".join(browser.validate_matrix(changed))
                self.assertIn("previewMinTargetHeight", errors)

    def test_matrix_rejects_invalid_reduced_preview_duration(self) -> None:
        matrix = self.load_matrix_with_preview_evidence()
        scenario_index = next(
            index
            for index, item in enumerate(matrix["scenarios"])
            if item["scenario"] == "mundus-zh-dark-desktop"
        )
        valid_fraction = json.loads(json.dumps(matrix))
        valid_fraction["scenarios"][scenario_index][
            "previewTransitionDurationMs"
        ] = 0.01
        self.assertEqual(browser.validate_matrix(valid_fraction), [])

        for duration in (
            False,
            float("nan"),
            float("inf"),
            float("-inf"),
        ):
            with self.subTest(value=duration):
                changed = json.loads(json.dumps(matrix))
                changed["scenarios"][scenario_index][
                    "previewTransitionDurationMs"
                ] = duration
                errors = " ".join(browser.validate_matrix(changed))
                self.assertIn("previewTransitionDurationMs", errors)

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
        mundus_index = next(
            i
            for i, item in enumerate(matrix["scenarios"])
            if item["scenario"] == "mundus-en-light-1440"
        )
        matrix["scenarios"][mundus_index]["totalImageCount"] = 3
        matrix["scenarios"][mundus_index]["productVisualCount"] = 2
        errors = browser.validate_matrix(matrix)
        self.assertIn("order", " ".join(errors))
        self.assertIn("brokenImageCount", " ".join(errors))
        self.assertIn("image count", " ".join(errors))
        self.assertIn("productVisualCount", " ".join(errors))

    def test_matrix_validates_new_homepage_about_and_bytedance_fields(
        self,
    ) -> None:
        valid = _build_valid_matrix()
        self.assertEqual(browser.validate_matrix(valid), [])

        def mutate(scenario_name: str, field: str, value: object) -> dict:
            changed = json.loads(json.dumps(valid))
            for item in changed["scenarios"]:
                if item["scenario"] == scenario_name:
                    item[field] = value
            return changed

        cases = (
            ("home-en-light-1440", "featured", ["Mundus", "DialogTree"]),
            ("home-en-light-1440", "internship", []),
            ("home-en-light-1440", "other", ["NBTI"]),
            ("home-en-light-1440", "mediaCount", 1),
            ("about-en-light-1440", "emailAddressCount", 1),
            ("about-en-light-1440", "emailCopyButtonCount", 1),
            ("about-en-light-1440", "emailCopySuccessVisible", False),
            ("about-en-light-1440", "emailCopyFallbackVisible", False),
            ("about-en-light-1440", "educationEntryCount", 1),
            ("bytedance-en-light-1440", "responsibilityModuleCount", 2),
            ("bytedance-en-light-1440", "comparisonCellCount", 3),
            ("bytedance-en-light-1440", "sharedQcGroupCount", 2),
            ("bytedance-en-light-1440", "mediaSectionCount", 1),
        )
        for scenario, field, value in cases:
            with self.subTest(scenario=scenario, field=field):
                errors = browser.validate_matrix(mutate(scenario, field, value))
                self.assertTrue(errors, f"{field} mutation was not rejected")

    def test_matrix_requires_about_scenarios_in_order(self) -> None:
        valid = _build_valid_matrix()
        self.assertEqual(browser.validate_matrix(valid), [])
        changed = json.loads(json.dumps(valid))
        changed["scenarios"].pop(4)  # drop about-en-light-1440
        self.assertIn("order", " ".join(browser.validate_matrix(changed)))

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
