"""Structured bidirectional fact verification at pinned Git revisions."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from .claim_semantics import (
    _AstroLiteralParser,
    extract_astro_rendered_semantics,
    extract_claim_semantics,
    extract_mdx_visible_text,
)


EXPECTED_REVISIONS = {
    "Mundus": "378fe528ca1c8f83f0280f83383b5e785e851285",
}


def extract_source_semantics(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"(?m)//.*$", "", text)
    # Standalone string variables are not structural evidence.
    text = re.sub(
        r"(?m)^\s*(?:const|let|var)\s+\w+\s*=\s*(['\"]).*?\1\s*;?\s*$",
        "",
        text,
    )
    return re.sub(r"\s+", " ", text)


def match_json_rules(document: object, rules: list[dict[str, object]]) -> bool:
    for rule in rules:
        if rule.get("type") != "json_path":
            raise ValueError(f"unsupported JSON rule: {rule.get('type')}")
        value = document
        try:
            for segment in rule.get("path", []):
                value = value[segment]  # type: ignore[index]
        except (KeyError, IndexError, TypeError):
            return False
        if value != rule.get("equals"):
            return False
    return True


def load_rules(path: Path) -> list[dict[str, object]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    rules = value.get("assertions")
    if value.get("schemaVersion") != 2 or not isinstance(rules, list):
        raise ValueError("invalid fact assertion catalog")
    for assertion in rules:
        claims = assertion.get("claims")
        evidence_items = assertion.get("evidence")
        if (
            not isinstance(claims, list)
            or len(claims) != 3
            or {claim.get("locale") for claim in claims}
            != {"en", "zh", "story"}
        ):
            raise ValueError(
                "each fact assertion requires en, zh, and story claims"
            )
        if (
            not isinstance(evidence_items, list)
            or not evidence_items
            or any(
                not isinstance(evidence, dict)
                or not isinstance(evidence.get("repository"), str)
                or not isinstance(evidence.get("source"), str)
                or not isinstance(evidence.get("rules"), list)
                or not evidence["rules"]
                for evidence in evidence_items
            )
        ):
            raise ValueError("each fact assertion requires public evidence")
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
        for claim in assertion["claims"]:
            claim_source = str(claim["source"])
            claim_text = (portfolio / claim_source).read_text(
                encoding="utf-8"
            )
            claim_text = extract_claim_semantics(claim_source, claim_text)
            if not match_rules(claim_text, claim["rules"]):
                errors.append(
                    f"{assertion_id}: {claim['locale']} portfolio claim mismatch"
                )
        for evidence in assertion["evidence"]:
            repository_name = str(evidence["repository"])
            evidence_source = str(evidence["source"])
            evidence_text = read_at_revision(
                repositories[repository_name],
                EXPECTED_REVISIONS[repository_name],
                evidence_source,
            )
            if evidence_source.endswith(".json"):
                evidence_matches = match_json_rules(
                    json.loads(evidence_text),
                    evidence["rules"],
                )
            else:
                evidence_matches = match_rules(
                    extract_source_semantics(evidence_text),
                    evidence["rules"],
                )
            if not evidence_matches:
                errors.append(
                    f"{assertion_id}: public evidence mismatch "
                    f"({evidence_source})"
                )
    return errors
