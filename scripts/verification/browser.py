"""Validate retained browser evidence and screenshot integrity."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


REQUIRED_SCENARIOS = {
    "home-en-light-desktop",
    "home-zh-dark-tablet",
    "mundus-zh-dark-desktop",
    "mundus-zh-dark-mobile",
    "omnipet-zh-dark-desktop",
    "omnipet-zh-dark-mobile",
}
REDUCED_SCENARIOS = REQUIRED_SCENARIOS - {
    "home-en-light-desktop",
    "home-zh-dark-tablet",
}


def read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schemaVersion") != 1:
        raise ValueError(f"{path.name}: invalid schemaVersion")
    return value


def validate_network(path: Path) -> list[str]:
    value = read_json(path)
    requests = value.get("requests")
    errors: list[str] = []
    if not isinstance(requests, list):
        return ["network requests must be an array"]
    statuses = Counter(str(item["status"]) for item in requests)
    types = Counter(str(item["resourceType"]) for item in requests)
    failures = [item for item in requests if int(item["status"]) >= 400]
    checks = {
        "requestCount": len(requests),
        "failureCount": len(failures),
        "statusCounts": dict(sorted(statuses.items())),
        "resourceTypeCounts": dict(sorted(types.items())),
        "failures": failures,
    }
    for key, expected in checks.items():
        if value.get(key) != expected:
            errors.append(f"network {key} is inconsistent")
    return errors


def webp_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    marker = data.find(b"VP8X")
    if marker >= 0:
        width = 1 + int.from_bytes(data[marker + 12 : marker + 15], "little")
        height = 1 + int.from_bytes(data[marker + 15 : marker + 18], "little")
        return width, height
    frame = data.find(b"\x9d\x01\x2a")
    if frame >= 0:
        width = int.from_bytes(data[frame + 3 : frame + 5], "little") & 0x3FFF
        height = int.from_bytes(data[frame + 5 : frame + 7], "little") & 0x3FFF
        return width, height
    marker = data.find(b"VP8L")
    if marker >= 0 and data[marker + 8] == 0x2F:
        packed = int.from_bytes(data[marker + 9 : marker + 13], "little")
        return (packed & 0x3FFF) + 1, ((packed >> 14) & 0x3FFF) + 1
    raise ValueError(f"{path.name}: unsupported WebP header")


def validate_screenshots(
    manifest_path: Path,
    assets_root: Path,
    *,
    check_dimensions: bool = True,
) -> list[str]:
    manifest = read_json(manifest_path)
    screenshots = manifest.get("screenshots")
    if not isinstance(screenshots, list):
        return ["screenshots must be an array"]
    errors: list[str] = []
    scenarios = {str(item.get("scenario")) for item in screenshots}
    if scenarios != REQUIRED_SCENARIOS - {"home-zh-dark-tablet"}:
        errors.append("screenshot scenarios are incomplete")
    for item in screenshots:
        path = assets_root / str(item["path"])
        if not path.is_file():
            errors.append(f"{item['path']}: screenshot missing")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != item.get("sha256"):
            errors.append(f"{item['path']}: sha256 mismatch")
        if check_dimensions:
            dimensions = webp_dimensions(path)
            if dimensions != (item.get("width"), item.get("height")):
                errors.append(f"{item['path']}: dimensions mismatch")
    return errors


def validate_all(evidence_root: Path, assets_root: Path) -> list[str]:
    errors = validate_network(evidence_root / "browser-network.json")
    matrix = read_json(evidence_root / "browser-matrix.json")
    reduced = read_json(evidence_root / "browser-reduced-motion.json")
    console = read_json(evidence_root / "browser-console.json")
    scenarios = {
        item.get("scenario"): item for item in matrix.get("scenarios", [])
    }
    if set(scenarios) != REQUIRED_SCENARIOS:
        errors.append("browser matrix scenarios are incomplete")
    reduced_items = {
        item.get("scenario"): item for item in reduced.get("scenarios", [])
    }
    if set(reduced_items) != REDUCED_SCENARIOS:
        errors.append("reduced-motion scenarios are incomplete")
    for name, item in reduced_items.items():
        matrix_item = scenarios.get(name, {})
        for key in ("route", "viewport", "reducedMotion", "overflow", "brokenImageCount"):
            expected_key = "matches" if key == "reducedMotion" else key
            if item.get(expected_key) != matrix_item.get(key):
                errors.append(f"{name}: reduced-motion {key} mismatch")
        if item.get("activeAnimationCount") != 0:
            errors.append(f"{name}: active animation remains")
    messages = console.get("messages", [])
    if console.get("messageCount") != len(messages):
        errors.append("console messageCount is inconsistent")
    error_count = sum(
        str(message).lower().startswith("error") for message in messages
    )
    warning_count = sum(
        str(message).lower().startswith(("warn", "warning"))
        for message in messages
    )
    if console.get("errorCount") != error_count:
        errors.append("console errorCount is inconsistent")
    if console.get("warningCount") != warning_count:
        errors.append("console warningCount is inconsistent")
    errors.extend(
        validate_screenshots(
            evidence_root / "browser-screenshots.json",
            assets_root,
        )
    )
    return errors
