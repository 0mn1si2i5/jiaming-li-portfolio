"""Structured bidirectional fact verification at pinned Git revisions."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


EXPECTED_REVISIONS = {
    "Mundus": "c6e625fa68879f9771debffebdaf32e295d56769",
}

def extract_mdx_visible_text(text: str) -> str:
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"\{/\*.*?\*/\}", "", text, flags=re.DOTALL)
    hidden_attributes = (
        r"(?:\bhidden(?:\s|>|=)|\baria-hidden\s*=\s*(?:[\"']true[\"']|\{true\})|"
        r"\bstyle\s*=\s*(?:[\"'][^\"']*(?:display\s*:\s*none|visibility\s*:\s*hidden)"
        r"[^\"']*[\"']|\{\{.*?(?:display\s*:\s*[\"']none[\"']|"
        r"visibility\s*:\s*[\"']hidden[\"']).*?\}\}))"
    )
    element = re.compile(
        rf"<(?P<tag>[A-Za-z][\w.-]*)\b(?=[^>]*{hidden_attributes})[^>]*>"
        rf".*?</(?P=tag)\s*>",
        flags=re.DOTALL | re.IGNORECASE,
    )
    previous = None
    while previous != text:
        previous = text
        text = element.sub("", text)
    text = re.sub(r"(?m)^\s*import\b.*$", "", text)
    text = re.sub(
        r"(?ms)^\s*export\s+(?:default\s+)?(?:const|let|var)\b.*?;\s*$",
        "",
        text,
    )
    text = re.sub(
        r"(?ms)^\s*export\s+(?:default\s+)?(?:async\s+)?function\b.*?^}\s*;?\s*$",
        "",
        text,
    )
    text = re.sub(r"(?m)^\s*export\b.*$", "", text)
    return text


def extract_source_semantics(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"(?m)//.*$", "", text)
    # Standalone string variables are not structural evidence.
    text = re.sub(
        r"(?m)^\s*(?:const|let|var)\s+\w+\s*=\s*(['\"]).*?\1\s*;?\s*$",
        "",
        text,
    )
    return text


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
        evidence = assertion.get("evidence")
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
            not isinstance(evidence, dict)
            or not isinstance(evidence.get("rules"), list)
            or not evidence["rules"]
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
        evidence = assertion["evidence"]
        evidence_text = read_at_revision(
            repositories[str(evidence["repository"])],
            EXPECTED_REVISIONS[str(evidence["repository"])],
            str(evidence["source"]),
        )
        for claim in assertion["claims"]:
            claim_text = (portfolio / str(claim["source"])).read_text(
                encoding="utf-8"
            )
            claim_text = extract_mdx_visible_text(claim_text)
            if not match_rules(claim_text, claim["rules"]):
                errors.append(
                    f"{assertion_id}: {claim['locale']} portfolio claim mismatch"
                )
        if str(evidence["source"]).endswith(".json"):
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
            errors.append(f"{assertion_id}: public evidence mismatch")
    return errors
