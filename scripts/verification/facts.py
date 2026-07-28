"""Structured bidirectional fact verification at pinned Git revisions."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


EXPECTED_REVISIONS = {
    "Mundus": "b7b2d0f9e453efd8be83216a43e642f0ee7350ed",
    "OmniPet": "f08e47c7dcee1bf7d89e1c673c73abb6fa90c20d",
    "OmniPets": "081b7c6f651183987c79c4321ff46e1b082e03b7",
}


def load_rules(path: Path) -> list[dict[str, object]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    rules = value.get("assertions")
    if value.get("schemaVersion") != 1 or not isinstance(rules, list):
        raise ValueError("invalid fact assertion catalog")
    return rules


def match_rules(text: str, rules: list[dict[str, object]]) -> bool:
    for rule in rules:
        kind = rule.get("type")
        if kind == "contains" and rule.get("value") not in text:
            return False
        if kind == "contains_all":
            values = rule.get("values", [])
            if not all(value in text for value in values):
                return False
        if kind == "regex" and not re.search(str(rule.get("value")), text):
            return False
        if kind not in {"contains", "contains_all", "regex"}:
            raise ValueError(f"unsupported fact rule: {kind}")
    return True


def git(repository: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repository), *args],
        text=True,
        stderr=subprocess.STDOUT,
    ).strip()


def read_at_revision(repository: Path, revision: str, source: str) -> str:
    return git(repository, "show", f"{revision}:{source}")


def verify(
    portfolio: Path,
    repositories: dict[str, Path],
    catalog: Path,
) -> list[str]:
    errors: list[str] = []
    for name, expected in EXPECTED_REVISIONS.items():
        repository = repositories[name]
        try:
            git(repository, "cat-file", "-e", f"{expected}^{{commit}}")
        except subprocess.CalledProcessError:
            errors.append(f"{name}: pinned revision is unavailable")

    if errors:
        return errors

    for assertion in load_rules(catalog):
        assertion_id = str(assertion["id"])
        claim = assertion["claim"]
        evidence = assertion["evidence"]
        claim_text = (portfolio / str(claim["source"])).read_text(encoding="utf-8")
        evidence_text = read_at_revision(
            repositories[str(evidence["repository"])],
            EXPECTED_REVISIONS[str(evidence["repository"])],
            str(evidence["source"]),
        )
        if not match_rules(claim_text, claim["rules"]):
            errors.append(f"{assertion_id}: portfolio claim mismatch")
        if not match_rules(evidence_text, evidence["rules"]):
            errors.append(f"{assertion_id}: public evidence mismatch")
    return errors
