"""Structured bidirectional fact verification at pinned Git revisions."""

from __future__ import annotations

import ast
import json
import re
import subprocess
from pathlib import Path


EXPECTED_REVISIONS = {
    "Mundus": "378fe528ca1c8f83f0280f83383b5e785e851285",
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


class _AstroLiteralParser:
    TOKEN = re.compile(
        r"""
        \s+
        |//[^\n]*
        |/\*.*?\*/
        |(?P<string>'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*")
        |(?P<number>-?\d+(?:\.\d+)?)
        |(?P<identifier>[A-Za-z_$][\w$]*)
        |(?P<punctuation>[\[\]{},:])
        """,
        flags=re.DOTALL | re.VERBOSE,
    )

    def __init__(self, source: str) -> None:
        self.tokens = []
        position = 0
        for match in self.TOKEN.finditer(source):
            if match.start() != position:
                raise ValueError("unsupported Astro literal token")
            position = match.end()
            if match.lastgroup is not None:
                self.tokens.append((match.lastgroup, match.group()))
        if position != len(source):
            raise ValueError("unsupported Astro literal token")
        self.index = 0

    def parse(self) -> object:
        value = self._parse_value()
        if self.index != len(self.tokens):
            raise ValueError("trailing Astro literal token")
        return value

    def _parse_value(self) -> object:
        token_type, value = self._take()
        if token_type == "string":
            return ast.literal_eval(value)
        if token_type == "number":
            return float(value) if "." in value else int(value)
        if token_type == "identifier":
            identifiers = {"true": True, "false": False, "null": None}
            if value not in identifiers:
                raise ValueError(f"unsupported Astro identifier: {value}")
            return identifiers[value]
        if value == "[":
            items = []
            while not self._accept("]"):
                items.append(self._parse_value())
                self._accept(",")
            return items
        if value == "{":
            result = {}
            while not self._accept("}"):
                key_type, key = self._take()
                if key_type == "string":
                    key = ast.literal_eval(key)
                elif key_type != "identifier":
                    raise ValueError("unsupported Astro object key")
                self._expect(":")
                result[str(key)] = self._parse_value()
                self._accept(",")
            return result
        raise ValueError("unsupported Astro literal")

    def _take(self) -> tuple[str | None, str]:
        if self.index >= len(self.tokens):
            raise ValueError("incomplete Astro literal")
        token = self.tokens[self.index]
        self.index += 1
        return token

    def _accept(self, value: str) -> bool:
        if self.index < len(self.tokens) and self.tokens[self.index][1] == value:
            self.index += 1
            return True
        return False

    def _expect(self, value: str) -> None:
        if not self._accept(value):
            raise ValueError(f"expected {value!r} in Astro literal")


def _mask_js_comments(source: str) -> str:
    masked = list(source)
    quote = None
    escaped = False
    index = 0
    while index < len(source):
        character = source[index]
        if quote is not None:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            index += 1
            continue
        if character in "'\"`":
            quote = character
            index += 1
            continue
        if source.startswith("//", index):
            end = source.find("\n", index + 2)
            end = len(source) if end < 0 else end
            for position in range(index, end):
                masked[position] = " "
            index = end
            continue
        if source.startswith("/*", index):
            end = source.find("*/", index + 2)
            end = len(source) if end < 0 else end + 2
            for position in range(index, end):
                if masked[position] != "\n":
                    masked[position] = " "
            index = end
            continue
        index += 1
    return "".join(masked)


def _balanced_literal(source: str, start: int) -> str | None:
    opening = source[start]
    if opening not in "[{":
        return None
    closing = {"]": "[", "}": "{"}
    stack = [opening]
    quote = None
    escaped = False
    index = start + 1
    while index < len(source):
        character = source[index]
        if quote is not None:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
        elif character in "'\"":
            quote = character
        elif source.startswith("//", index):
            newline = source.find("\n", index + 2)
            index = len(source) if newline < 0 else newline
            continue
        elif source.startswith("/*", index):
            end = source.find("*/", index + 2)
            if end < 0:
                return None
            index = end + 2
            continue
        elif character in "[{":
            stack.append(character)
        elif character in "]}":
            if not stack or stack[-1] != closing[character]:
                return None
            stack.pop()
            if not stack:
                return source[start : index + 1]
        index += 1
    return None


def _astro_frontmatter_models(
    frontmatter: str,
) -> tuple[dict[str, object], dict[str, tuple[str, int]]]:
    models: dict[str, object] = {}
    aliases: dict[str, tuple[str, int]] = {}
    frontmatter = _mask_js_comments(frontmatter)
    for match in re.finditer(r"\bconst\s+([A-Za-z_$][\w$]*)\s*=", frontmatter):
        name = match.group(1)
        start = match.end()
        while start < len(frontmatter) and frontmatter[start].isspace():
            start += 1
        literal = _balanced_literal(frontmatter, start)
        if literal is not None:
            literal_end = start + len(literal)
            terminator = re.match(
                r"\s*(?:as\s+const\s*)?;",
                frontmatter[literal_end:],
            )
            if terminator is None:
                continue
            try:
                models[name] = _AstroLiteralParser(literal).parse()
            except (SyntaxError, ValueError):
                pass
            continue
        alias = re.match(
            r"([A-Za-z_$][\w$]*)\s*\[\s*(\d+)\s*\]",
            frontmatter[start:],
        )
        if alias and re.match(r"\s*;", frontmatter[start + alias.end() :]):
            aliases[name] = (alias.group(1), int(alias.group(2)))
    return models, aliases


def _path_values(value: object, path: list[str]) -> list[object]:
    values = value if isinstance(value, list) else [value]
    for segment in path:
        next_values = []
        for item in values:
            if isinstance(item, dict) and segment in item:
                child = item[segment]
                next_values.extend(child if isinstance(child, list) else [child])
        values = next_values
    return values


def _flatten_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [
            item
            for child in value.values()
            for item in _flatten_strings(child)
        ]
    if isinstance(value, list):
        return [item for child in value for item in _flatten_strings(child)]
    return []


_HTML_VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


def _has_hidden_attributes(attributes: str) -> bool:
    if re.search(r"(?:^|\s)hidden(?=\s|=|/|$)", attributes):
        return True
    if re.search(
        r"\baria-hidden\s*=\s*(?:[\"']true[\"']|\{true\})",
        attributes,
        flags=re.IGNORECASE,
    ):
        return True
    style = re.search(
        r"\bstyle\s*=\s*(\"[^\"]*\"|'[^']*'|\{\{.*?\}\})",
        attributes,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return bool(
        style
        and re.search(
            r"(?:display\s*:\s*[\"']?none[\"']?"
            r"|visibility\s*:\s*[\"']?hidden[\"']?)",
            style.group(1),
            flags=re.IGNORECASE,
        )
    )


def _remove_hidden_self_closing_nodes(template: str) -> str:
    opening_tag = re.compile(
        r"<(?P<tag>[A-Za-z][\w.-]*)\b(?P<attributes>[^>]*)>",
        flags=re.DOTALL,
    )

    def remove_if_hidden(match: re.Match[str]) -> str:
        tag = match.group("tag").lower()
        attributes = match.group("attributes")
        self_closing = attributes.rstrip().endswith("/")
        if (
            (self_closing or tag in _HTML_VOID_TAGS)
            and _has_hidden_attributes(attributes)
        ):
            return ""
        return match.group(0)

    return opening_tag.sub(remove_if_hidden, template)


def extract_astro_rendered_semantics(text: str) -> str:
    frontmatter_match = re.match(
        r"\A---\s*\n(?P<frontmatter>.*?)\n---\s*(?:\n|\Z)",
        text,
        flags=re.DOTALL,
    )
    if frontmatter_match is None:
        frontmatter = ""
        template = text
    else:
        frontmatter = frontmatter_match.group("frontmatter")
        template = text[frontmatter_match.end() :]

    template = re.sub(
        r"<(?P<tag>script|style)\b[^>]*>.*?</(?P=tag)\s*>",
        "",
        template,
        flags=re.DOTALL | re.IGNORECASE,
    )
    template = _remove_hidden_self_closing_nodes(template)
    visible_template = extract_mdx_visible_text(template)
    models, aliases = _astro_frontmatter_models(frontmatter)
    map_bindings = {
        item: collection
        for collection, item in re.findall(
            r"\b([A-Za-z_$][\w$]*)\.map\(\s*\(\s*"
            r"([A-Za-z_$][\w$]*)",
            visible_template,
        )
    }
    references = set(
        re.findall(
            r"\{\s*(?:\.\.\.\s*)?"
            r"([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)+)\s*\}",
            visible_template,
        )
    )

    consumed = []
    for reference in references:
        root, *path = reference.split(".")
        if root in map_bindings:
            value = models.get(map_bindings[root])
        elif root in aliases:
            collection, index = aliases[root]
            items = models.get(collection)
            value = (
                items[index]
                if isinstance(items, list) and index < len(items)
                else None
            )
        else:
            value = models.get(root)
        if value is None:
            continue
        for resolved in _path_values(value, path):
            consumed.extend(_flatten_strings(resolved))

    return " ".join([visible_template, *consumed])


def extract_claim_semantics(source: str, text: str) -> str:
    if Path(source).suffix.lower() == ".astro":
        return extract_astro_rendered_semantics(text)
    return extract_mdx_visible_text(text)


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
