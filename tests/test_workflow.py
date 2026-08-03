from __future__ import annotations

import re
import unittest
from pathlib import Path


class TestPullRequestWorkflow(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = Path(".github/workflows/deploy.yml").read_text(
            encoding="utf-8"
        )

    def test_pull_requests_run_the_complete_non_deploying_gate(self) -> None:
        self.assertIn("pull_request:", self.workflow)
        for command in (
            "npm ci",
            "npm test",
            "npm run build",
            "npm run verify --",
        ):
            self.assertIn(command, self.workflow)
        self.assertIn(
            "ref: c6e625fa68879f9771debffebdaf32e295d56769",
            self.workflow,
        )
        self.assertNotIn("OmniPet", self.workflow)
        self.assertNotIn("--omnipet-root", self.workflow)
        self.assertNotIn("--omnipets-root", self.workflow)
        self.assertIn(
            "github.event_name != 'pull_request'",
            self.workflow,
        )
        self.assertIn("github.ref == 'refs/heads/main'", self.workflow)

    def test_jobs_have_minimal_permissions_and_separate_concurrency(self) -> None:
        self.assertIn(
            "build:\n    permissions:\n      contents: read",
            self.workflow,
        )
        self.assertIn(
            "deploy:\n    if:",
            self.workflow,
        )
        self.assertIn(
            "permissions:\n      pages: write\n      id-token: write",
            self.workflow,
        )
        self.assertIn("github.event.pull_request.number", self.workflow)
        self.assertIn(
            "cancel-in-progress: ${{ github.event_name == 'pull_request' }}",
            self.workflow,
        )

    def test_actions_are_pinned_to_full_commit_shas(self) -> None:
        action_uses = re.findall(
            r"uses:\s+([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([^\s#]+)",
            self.workflow,
        )
        self.assertGreaterEqual(len(action_uses), 5)
        for action, revision in action_uses:
            with self.subTest(action=action):
                self.assertRegex(revision, r"^[0-9a-f]{40}$")

    def test_local_and_ci_builds_share_the_pages_base(self) -> None:
        config = Path("astro.config.mjs").read_text(encoding="utf-8")
        self.assertIn("const localProjectBase = '/jiaming-li-portfolio';", config)
        self.assertIn(": localProjectBase", config)


if __name__ == "__main__":
    unittest.main()
