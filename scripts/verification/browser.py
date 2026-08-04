"""Validate retained browser evidence and screenshot integrity."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from pathlib import Path


REQUIRED_SCENARIOS = (
    "home-en-light-1440",
    "home-en-light-1024",
    "home-zh-dark-768",
    "home-zh-dark-390",
    "mundus-en-light-1440",
    "mundus-zh-dark-desktop",
    "mundus-en-light-390",
    "mundus-zh-dark-mobile",
)
REDUCED_SCENARIOS = (
    "home-zh-dark-768",
    "home-zh-dark-390",
    "mundus-zh-dark-desktop",
    "mundus-zh-dark-mobile",
)
SCENARIO_EXPECTATIONS = {
    "home-en-light-1440": {
        "route": "/", "locale": "en", "theme": "light",
        "viewport": {"width": 1440, "height": 900}, "reducedMotion": False,
    },
    "home-en-light-1024": {
        "route": "/", "locale": "en", "theme": "light",
        "viewport": {"width": 1024, "height": 768}, "reducedMotion": False,
    },
    "home-zh-dark-768": {
        "route": "/", "locale": "zh", "theme": "dark",
        "viewport": {"width": 768, "height": 1024}, "reducedMotion": True,
    },
    "home-zh-dark-390": {
        "route": "/", "locale": "zh", "theme": "dark",
        "viewport": {"width": 390, "height": 844}, "reducedMotion": True,
    },
    "mundus-en-light-1440": {
        "route": "/projects/mundus", "locale": "en", "theme": "light",
        "viewport": {"width": 1440, "height": 900}, "reducedMotion": False,
    },
    "mundus-zh-dark-desktop": {
        "route": "/projects/mundus", "locale": "zh", "theme": "dark",
        "viewport": {"width": 1440, "height": 900}, "reducedMotion": True,
    },
    "mundus-en-light-390": {
        "route": "/projects/mundus", "locale": "en", "theme": "light",
        "viewport": {"width": 390, "height": 844}, "reducedMotion": False,
    },
    "mundus-zh-dark-mobile": {
        "route": "/projects/mundus", "locale": "zh", "theme": "dark",
        "viewport": {"width": 390, "height": 844}, "reducedMotion": True,
    },
}
SCREENSHOT_FILES = {
    "home-en-light-1440": "task7-home-en-light-1440x900.webp",
    "home-en-light-1024": "task7-home-en-light-1024x768.webp",
    "home-zh-dark-768": "task7-home-zh-dark-reduced-768x1024.webp",
    "home-zh-dark-390": "task7-home-zh-dark-reduced-390x844.webp",
    "mundus-en-light-1440": "task7-mundus-en-light-1440x900.webp",
    "mundus-zh-dark-desktop": "task7-mundus-zh-dark-reduced-1440x900.webp",
    "mundus-en-light-390": "task7-mundus-en-light-390x844.webp",
    "mundus-zh-dark-mobile": "task7-mundus-zh-dark-reduced-390x844.webp",
}
DIST_HTML_FILES = (
    "index.html",
    "about/index.html",
    "projects/dialogtree/index.html",
    "projects/mundus/index.html",
    "projects/nbti/index.html",
    "projects/side-b/index.html",
)
PROJECT_ORDER = ["DialogTree", "Mundus", "NBTI"]
OTHER_ORDER = ["Side B", "RSZ Namelist"]


def is_finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and (not isinstance(value, float) or math.isfinite(value))
    )


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
    if failures or any(int(item["status"]) not in range(200, 400) for item in requests):
        errors.append("network contains failed requests")
    return errors


def validate_matrix(value: dict[str, object]) -> list[str]:
    items = value.get("scenarios", [])
    errors: list[str] = []
    if not isinstance(items, list):
        return ["browser matrix scenarios must be an array"]
    names = [item.get("scenario") for item in items]
    if names != list(REQUIRED_SCENARIOS):
        errors.append("browser matrix scenario order is invalid")
    for item in items:
        name = str(item.get("scenario"))
        required = (
            "route", "locale", "theme", "viewport", "overflow",
            "brokenImageCount", "decodedImageCount", "totalImageCount",
            "focusableCount", "focusVisible", "reducedMotion",
            "pagesBaseCorrect",
        )
        for field in required:
            if field not in item:
                errors.append(f"{name}: missing {field}")
        for field, expected in SCENARIO_EXPECTATIONS.get(name, {}).items():
            if item.get(field) != expected:
                errors.append(f"{name}: {field} does not match expected value")
        if item.get("overflow") is not False:
            errors.append(f"{name}: overflow is not false")
        if item.get("brokenImageCount") != 0:
            errors.append(f"{name}: brokenImageCount is not zero")
        if item.get("focusVisible") is not True:
            errors.append(f"{name}: keyboard focus is not visible")
        if item.get("pagesBaseCorrect") is not True:
            errors.append(f"{name}: pagesBaseCorrect is not true")
        if not isinstance(item.get("focusableCount"), int) or item["focusableCount"] <= 0:
            errors.append(f"{name}: focusableCount is not positive")
        if name in REDUCED_SCENARIOS:
            if item.get("reducedMotion") is not True:
                errors.append(f"{name}: reducedMotion is not true")
            if item.get("activeAnimationCount") != 0:
                errors.append(f"{name}: activeAnimationCount is not zero")
            if not isinstance(item.get("visibleTextLength"), int) or item["visibleTextLength"] <= 0:
                errors.append(f"{name}: visibleTextLength is not positive")
        if name.startswith("home-"):
            if item.get("totalImageCount") != 4:
                errors.append(f"{name}: homepage image count is not four")
            if item.get("selected") != PROJECT_ORDER:
                errors.append(f"{name}: selected project order is invalid")
            if item.get("other") != OTHER_ORDER:
                errors.append(f"{name}: other project order is invalid")
        if name.startswith("mundus-"):
            preview_required = (
                "previewDefaultMode",
                "previewPointerModes",
                "previewKeyboardModes",
                "previewLinkTargetsCorrect",
                "previewSelectionSynchronized",
                "previewLayout",
                "previewMinTargetHeight",
                "previewTransitionDurationMs",
            )
            for field in preview_required:
                if field not in item:
                    errors.append(f"{name}: missing {field}")
            if item.get("totalImageCount") != 2:
                errors.append(f"{name}: Mundus image count is not two")
            if item.get("productVisualCount") != 1:
                errors.append(f"{name}: productVisualCount is not one")
            if item.get("previewDefaultMode") != "antipodes":
                errors.append(f"{name}: previewDefaultMode is invalid")
            if item.get("previewPointerModes") != [
                "antipodes", "development", "sunline"
            ]:
                errors.append(f"{name}: previewPointerModes is invalid")
            if item.get("previewKeyboardModes") != [
                "antipodes", "development", "sunline"
            ]:
                errors.append(f"{name}: previewKeyboardModes is invalid")
            if item.get("previewLinkTargetsCorrect") is not True:
                errors.append(
                    f"{name}: previewLinkTargetsCorrect is not true"
                )
            if item.get("previewSelectionSynchronized") is not True:
                errors.append(
                    f"{name}: previewSelectionSynchronized is not true"
                )
            viewport = item.get("viewport")
            width = (
                viewport.get("width")
                if isinstance(viewport, dict)
                else None
            )
            if not is_finite_number(width):
                errors.append(f"{name}: viewport width is invalid")
                errors.append(f"{name}: previewLayout is invalid")
            else:
                expected_layout = (
                    "vertical" if width <= 760 else "columns"
                )
                if item.get("previewLayout") != expected_layout:
                    errors.append(f"{name}: previewLayout is invalid")
            min_target_height = item.get("previewMinTargetHeight")
            if not (
                is_finite_number(min_target_height)
                and min_target_height >= 44
            ):
                errors.append(
                    f"{name}: previewMinTargetHeight is below 44"
                )
            if name in REDUCED_SCENARIOS:
                transition_duration = item.get(
                    "previewTransitionDurationMs"
                )
                if not (
                    is_finite_number(transition_duration)
                    and transition_duration in (0, 0.01)
                ):
                    errors.append(
                        f"{name}: previewTransitionDurationMs is not reduced"
                    )
    return errors


def validate_console(value: dict[str, object]) -> list[str]:
    messages = value.get("messages", [])
    errors: list[str] = []
    if not isinstance(messages, list):
        return ["console messages must be an array"]
    for message in messages:
        if not isinstance(message, dict) or message.get("level") not in {
            "debug", "info", "log", "warning", "error"
        } or not isinstance(message.get("text"), str):
            errors.append("console message schema is invalid")
    if messages or value.get("messageCount") != 0 or value.get("errorCount") != 0 or value.get("warningCount") != 0:
        errors.append("console must be empty and failure-free")
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
    scenarios = [str(item.get("scenario")) for item in screenshots]
    expected = list(REQUIRED_SCENARIOS)
    if scenarios != expected:
        errors.append("screenshot scenarios are incomplete")
    for item in screenshots:
        scenario = str(item.get("scenario"))
        raw_path = str(item.get("path", ""))
        if raw_path != SCREENSHOT_FILES.get(scenario):
            errors.append(f"{scenario}: screenshot filename is invalid")
        candidate = Path(raw_path)
        if candidate.is_absolute() or candidate.name != raw_path or ".." in candidate.parts:
            errors.append(f"{scenario}: screenshot path is unsafe")
            continue
        root = assets_root.resolve()
        path = assets_root / candidate
        if path.is_symlink():
            errors.append(f"{scenario}: screenshot symlink is forbidden")
            continue
        resolved = path.resolve()
        if resolved.parent != root:
            errors.append(f"{scenario}: screenshot path escapes assets")
            continue
        path = resolved
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


def validate_dist_html(path: Path, dist_root: Path) -> list[str]:
    if not path.is_file():
        return [f"{path.name}: evidence is missing"]
    manifest = read_json(path)
    items = manifest.get("html")
    if not isinstance(items, list):
        return ["dist HTML entries must be an array"]
    errors: list[str] = []
    if [item.get("path") for item in items] != list(DIST_HTML_FILES):
        errors.append("dist HTML paths are incomplete")
    root = dist_root.resolve()
    for item in items:
        if not isinstance(item, dict):
            errors.append("dist HTML entry schema is invalid")
            continue
        raw_path = str(item.get("path", ""))
        candidate = Path(raw_path)
        if (
            candidate.is_absolute()
            or ".." in candidate.parts
            or candidate.as_posix() != raw_path
        ):
            errors.append(f"{raw_path}: dist HTML path is unsafe")
            continue
        html = dist_root / candidate
        if html.is_symlink():
            errors.append(f"{raw_path}: dist HTML symlink is forbidden")
            continue
        resolved = html.resolve()
        if not resolved.is_relative_to(root):
            errors.append(f"{raw_path}: dist HTML path escapes dist")
            continue
        if not resolved.is_file():
            errors.append(f"{raw_path}: dist HTML is missing")
            continue
        digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
        if digest != item.get("sha256"):
            errors.append(f"{raw_path}: dist HTML digest mismatch")
    return errors


def validate_all(
    evidence_root: Path,
    assets_root: Path,
    dist_root: Path,
) -> list[str]:
    errors = validate_network(evidence_root / "browser-network.json")
    errors.extend(
        validate_dist_html(
            evidence_root / "browser-build.json",
            dist_root,
        )
    )
    matrix = read_json(evidence_root / "browser-matrix.json")
    reduced = read_json(evidence_root / "browser-reduced-motion.json")
    console = read_json(evidence_root / "browser-console.json")
    errors.extend(validate_matrix(matrix))
    scenarios = {
        item.get("scenario"): item for item in matrix.get("scenarios", [])
    }
    reduced_items = {
        item.get("scenario"): item for item in reduced.get("scenarios", [])
    }
    if list(reduced_items) != list(REDUCED_SCENARIOS):
        errors.append("reduced-motion scenarios are incomplete")
    for name, item in reduced_items.items():
        matrix_item = scenarios.get(name, {})
        for key in ("route", "viewport", "reducedMotion", "overflow", "brokenImageCount"):
            expected_key = "matches" if key == "reducedMotion" else key
            if item.get(expected_key) != matrix_item.get(key):
                errors.append(f"{name}: reduced-motion {key} mismatch")
        if item.get("activeAnimationCount") != 0:
            errors.append(f"{name}: active animation remains")
    errors.extend(validate_console(console))
    errors.extend(
        validate_screenshots(
            evidence_root / "browser-screenshots.json",
            assets_root,
        )
    )
    return errors
