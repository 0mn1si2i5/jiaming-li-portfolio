"""Reject tracked agent scratch files and process-only documentation."""

from __future__ import annotations

import re
import subprocess
from collections.abc import Iterable


FORBIDDEN_PREFIXES = (
    ".agent-work/",
    ".claude/plans/",
    "docs/aegis/plans/",
    "docs/aegis/work/",
    "docs/superpowers/plans/",
)

PROCESS_DOCUMENT = re.compile(
    r"(^|/)(?:agent-plan|checkpoint|resume-state|todo|worklog)"
    r"(?:[-_.][^/]*)?\.md$",
    flags=re.IGNORECASE,
)

PERSISTENT_DOCUMENT_ROOTS = (
    "docs/specifications/",
    "docs/decisions/",
    "docs/verification/",
)


def find_violations(paths: Iterable[str]) -> list[str]:
    violations = []
    for path in paths:
        if path.startswith(FORBIDDEN_PREFIXES):
            violations.append(path)
            continue
        if (
            PROCESS_DOCUMENT.search(path)
            and not path.startswith(PERSISTENT_DOCUMENT_ROOTS)
        ):
            violations.append(path)
    return sorted(set(violations))


def tracked_paths() -> list[str]:
    output = subprocess.check_output(["git", "ls-files", "-z"])
    return [
        path.decode("utf-8")
        for path in output.split(b"\0")
        if path
    ]


def main() -> int:
    violations = find_violations(tracked_paths())
    if not violations:
        print("repository hygiene: pass")
        return 0

    print("repository hygiene: tracked process-only files are forbidden")
    for path in violations:
        print(f"- {path}")
    print(
        "Use .agent-work/ for temporary material. Commit persistent documents "
        "only when explicitly requested, under docs/specifications/, "
        "docs/decisions/, or docs/verification/."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
