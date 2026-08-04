from __future__ import annotations

import unittest

from scripts.check_repository_hygiene import find_violations


class TestRepositoryHygiene(unittest.TestCase):
    def test_rejects_agent_process_paths(self) -> None:
        paths = (
            ".agent-work/current-plan.md",
            ".claude/plans/feature.md",
            "docs/aegis/plans/implementation.md",
            "docs/aegis/work/feature/checkpoint.md",
            "docs/superpowers/plans/feature.md",
            "notes/checkpoint-release.md",
            "notes/resume-state.md",
            "notes/agent-plan.md",
            "notes/worklog.md",
            "notes/todo.md",
        )

        self.assertEqual(find_violations(paths), sorted(paths))

    def test_allows_product_files_and_explicit_persistent_roots(self) -> None:
        paths = (
            "AGENTS.md",
            "src/components/BaseLayout.astro",
            "docs/specifications/product-contract.md",
            "docs/decisions/0001-pages-deployment.md",
            "docs/verification/mundus-release-verification.md",
        )

        self.assertEqual(find_violations(paths), [])


if __name__ == "__main__":
    unittest.main()
