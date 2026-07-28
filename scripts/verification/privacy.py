"""Scan final static output for publish-boundary violations."""

from __future__ import annotations

import math
import re
from pathlib import Path


PATTERNS = {
    "absolute path": re.compile(
        r"(?:file://|/(?:Users|home|root|Volumes|private|var/folders)/|"
        r"[A-Za-z]:\\(?:Users|Documents|Desktop)\\)"
    ),
    "internal URL": re.compile(
        r"https?://(?:localhost|127\.0\.0\.1|0\.0\.0\.0|10\.\d+\.\d+\.\d+|"
        r"192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)"
        r"|https?://[A-Za-z0-9.-]+\.(?:internal|local|corp)(?=[:/])"
    ),
    "credential": re.compile(
        r"(?:Bearer\s+[A-Za-z0-9._~+/=-]{20,}|"
        r"(?:api[_-]?key|password|secret|token)\s*[:=]\s*[\"']?"
        r"[A-Za-z0-9._~+/=-]{20,})",
        re.IGNORECASE,
    ),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}
TOKEN = re.compile(r"[A-Za-z0-9+/=_-]{32,}")


def entropy(value: str) -> float:
    counts = {character: value.count(character) for character in set(value)}
    length = len(value)
    return -sum(
        (count / length) * math.log2(count / length)
        for count in counts.values()
    )


def scan_dist(root: Path) -> list[str]:
    if not root.is_dir():
        return ["dist: output directory is missing"]
    findings: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        data = path.read_bytes()
        texts = [data.decode("latin-1")]
        for encoding in ("utf-8", "utf-16-le", "utf-16-be"):
            try:
                decoded = data.decode(encoding)
            except UnicodeDecodeError:
                continue
            if decoded not in texts:
                texts.append(decoded)
        relative = path.relative_to(root).as_posix()
        for name, pattern in PATTERNS.items():
            if any(pattern.search(text) for text in texts):
                findings.append(f"{relative}: {name}")
        for text in texts:
            for token in TOKEN.findall(text):
                if (
                    entropy(token) >= 4.3
                    and not re.fullmatch(r"[0-9a-f]{40,64}", token)
                    and not token.startswith(("_astro", "fontsource"))
                ):
                    findings.append(f"{relative}: high-entropy token")
                    break
            else:
                continue
            break
    return findings
