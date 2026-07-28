from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "verify-task7-facts.py"
SPEC = importlib.util.spec_from_file_location("verify_task7_facts", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
verify_task7_facts = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = verify_task7_facts
SPEC.loader.exec_module(verify_task7_facts)


class TestRevisionGate(unittest.TestCase):
    def setUp(self) -> None:
        self.expected = verify_task7_facts.ExpectedRevision(
            sha="a" * 40,
            branch="main",
            clean=True,
        )

    def test_validate_revision_accepts_exact_clean_main_revision(self) -> None:
        actual = {"sha": "a" * 40, "branch": "main", "dirty": False}

        result = verify_task7_facts.validate_revision(actual, self.expected)

        self.assertTrue(result["passed"])
        self.assertEqual(result["failures"], [])

    def test_expected_revisions_are_fixed_to_reviewed_clean_main_sources(self) -> None:
        expected = verify_task7_facts.EXPECTED_REVISIONS

        self.assertEqual(
            expected["Mundus"].sha,
            "b7b2d0f9e453efd8be83216a43e642f0ee7350ed",
        )
        self.assertEqual(
            expected["OmniPet"].sha,
            "f08e47c7dcee1bf7d89e1c673c73abb6fa90c20d",
        )
        self.assertEqual(
            expected["OmniPets"].sha,
            "081b7c6f651183987c79c4321ff46e1b082e03b7",
        )
        self.assertTrue(
            all(
                revision.branch == "main" and revision.clean
                for revision in expected.values()
            )
        )

    def test_validate_revision_rejects_wrong_sha(self) -> None:
        actual = {"sha": "b" * 40, "branch": "main", "dirty": False}

        result = verify_task7_facts.validate_revision(actual, self.expected)

        self.assertFalse(result["passed"])
        self.assertIn("sha", result["failures"])

    def test_validate_revision_rejects_non_main_branch(self) -> None:
        actual = {"sha": "a" * 40, "branch": "feature", "dirty": False}

        result = verify_task7_facts.validate_revision(actual, self.expected)

        self.assertFalse(result["passed"])
        self.assertIn("branch", result["failures"])

    def test_validate_revision_rejects_dirty_repository(self) -> None:
        actual = {"sha": "a" * 40, "branch": "main", "dirty": True}

        result = verify_task7_facts.validate_revision(actual, self.expected)

        self.assertFalse(result["passed"])
        self.assertIn("clean", result["failures"])


class TestBidirectionalAssertions(unittest.TestCase):
    def make_assertion(self) -> object:
        return verify_task7_facts.Assertion(
            assertion_id="paired-claim",
            portfolio_source="src/content/projects/example.mdx",
            portfolio_needle="portfolio claim",
            evidence_repository="Mundus",
            evidence_source="README.md",
            evidence_needle="public evidence",
            claim="A paired public claim.",
        )

    def test_evaluate_assertion_requires_portfolio_claim(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "portfolio/src/content/projects").mkdir(parents=True)
            (root / "portfolio/src/content/projects/example.mdx").write_text(
                "different text",
                encoding="utf-8",
            )
            (root / "mundus").mkdir()
            (root / "mundus/README.md").write_text(
                "public evidence",
                encoding="utf-8",
            )

            result = verify_task7_facts.evaluate_assertion(
                self.make_assertion(),
                {"Portfolio": root / "portfolio", "Mundus": root / "mundus"},
            )

        self.assertFalse(result["claimPassed"])
        self.assertTrue(result["evidencePassed"])
        self.assertFalse(result["passed"])

    def test_evaluate_assertion_requires_public_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "portfolio/src/content/projects").mkdir(parents=True)
            (root / "portfolio/src/content/projects/example.mdx").write_text(
                "portfolio claim",
                encoding="utf-8",
            )
            (root / "mundus").mkdir()
            (root / "mundus/README.md").write_text(
                "different text",
                encoding="utf-8",
            )

            result = verify_task7_facts.evaluate_assertion(
                self.make_assertion(),
                {"Portfolio": root / "portfolio", "Mundus": root / "mundus"},
            )

        self.assertTrue(result["claimPassed"])
        self.assertFalse(result["evidencePassed"])
        self.assertFalse(result["passed"])

    def test_assertion_catalog_has_31_paired_items_and_required_sources(self) -> None:
        assertions = verify_task7_facts.ASSERTIONS
        sources = {
            (item.evidence_repository, item.evidence_source)
            for item in assertions
        }

        self.assertEqual(len(assertions), 31)
        self.assertTrue(
            all(item.portfolio_source and item.portfolio_needle for item in assertions)
        )
        self.assertIn(("Mundus", "src/data/registry.ts"), sources)
        self.assertIn(("Mundus", "README.md"), sources)
        self.assertIn(("OmniPet", "README.md"), sources)
        self.assertIn(("OmniPets", "README.md"), sources)


if __name__ == "__main__":
    unittest.main()
