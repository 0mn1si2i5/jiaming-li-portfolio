#!/usr/bin/env python3
"""Verify Task 7 public claims and emit sanitized, deterministic evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Assertion:
    assertion_id: str
    repository: str
    source: str
    needle: str
    claim: str


ASSERTIONS = (
    Assertion("mundus-mode-order", "Mundus", "src/features/modes/modeRegistry.ts", "MODE_ORDER = ['antipodes', 'development', 'sunline']", "Three modes are registered in a stable order."),
    Assertion("mundus-mode-spatial", "Mundus", "src/features/modes/modeRegistry.ts", "category: 'spatial'", "Other Side is a spatial mode."),
    Assertion("mundus-mode-human", "Mundus", "src/features/modes/modeRegistry.ts", "category: 'human'", "Development is a human mode."),
    Assertion("mundus-mode-temporal", "Mundus", "src/features/modes/modeRegistry.ts", "category: 'temporal'", "Sunline is a temporal mode."),
    Assertion("mundus-development-resources", "Mundus", "src/features/modes/modeRegistry.ts", "resources: ['natural-earth-countries-110m', 'undp-hdr-2025-development']", "Development declares Natural Earth and UNDP resources."),
    Assertion("mundus-sunline-min-year", "Mundus", "src/features/sunline/solar.ts", "Date.UTC(2000, 0, 1)", "Sunline starts at 2000 UTC."),
    Assertion("mundus-sunline-max-year", "Mundus", "src/features/sunline/solar.ts", "Date.UTC(2099, 11, 31, 23, 59)", "Sunline ends at the final minute of 2099 UTC."),
    Assertion("mundus-sunrise-altitude", "Mundus", "src/features/sunline/solar.ts", "SUNRISE_ALTITUDE_DEGREES = -0.833", "Sunrise and sunset use an apparent altitude of -0.833 degrees."),
    Assertion("mundus-civil-twilight", "Mundus", "src/features/sunline/solar.ts", "'civil-twilight'", "Solar observations expose civil twilight."),
    Assertion("mundus-polar-day", "Mundus", "src/features/sunline/solar.ts", "'polar-day'", "Solar events expose polar day."),
    Assertion("mundus-polar-night", "Mundus", "src/features/sunline/solar.ts", "'polar-night'", "Solar events expose polar night."),
    Assertion("mundus-city-count", "Mundus", "DATA_SOURCES.md", "6,944 records", "The immutable GeoNames index contains 6,944 records."),
    Assertion("mundus-undp-years", "Mundus", "DATA_SOURCES.md", "covering 1990–2023", "The UNDP series covers 1990 through 2023."),
    Assertion("mundus-vector-quality", "Mundus", "DATA_SOURCES.md", "low quality lazily requests 110m; medium and high quality", "Vector quality uses 110m for low and 50m for medium/high."),
    Assertion("mundus-solar-method", "Mundus", "DATA_SOURCES.md", "NOAA/Meeus-style approximations", "Sunline uses NOAA/Meeus-style approximations."),
    Assertion("omnipet-no-auto-retry", "OmniPet", "docs/architecture.md", "There is no automatic retry", "Provider failures are not retried automatically."),
    Assertion("omnipet-transactional-repair", "OmniPet", "docs/architecture.md", "Repair archives the selected completed or failed visual job transactionally", "Repair archives a selected visual job transactionally."),
    Assertion("omnipet-release-allowlist", "OmniPet", "docs/architecture.md", "closed allowlist", "Public release export uses a closed allowlist."),
    Assertion("omnipet-clean-verification", "OmniPet", "docs/architecture.md", "requires no provider credentials or production project", "Public verification requires neither provider credentials nor a production project."),
    Assertion("omnipet-standard-rows", "OmniPet", "docs/generation-workflow.md", "nine standard rows", "The atlas contains nine standard action rows."),
    Assertion("omnipet-atlas-grid", "OmniPet", "docs/generation-workflow.md", "8x11 atlas", "The final atlas uses an 8 by 11 grid."),
    Assertion("omnipet-atlas-size", "OmniPet", "docs/generation-workflow.md", "1536x2288", "The final atlas is exactly 1536 by 2288 pixels."),
    Assertion("omnipet-look-rows", "OmniPet", "docs/generation-workflow.md", "nine standard rows plus two look rows", "The final atlas adds two look rows to nine standard rows."),
    Assertion("omnipet-release-atlas", "OmniPet", "src/omnipet/public_release.py", '"spritesheet.webp"', "The release contract requires the sprite atlas."),
    Assertion("omnipet-release-preview", "OmniPet", "src/omnipet/public_release.py", '"preview.webp"', "The release contract requires a preview."),
    Assertion("omnipet-release-hash", "OmniPet", "src/omnipet/public_release.py", "_HASH = re.compile", "Release file records use SHA-256 hashes."),
    Assertion("omnipet-release-closed-set", "OmniPet", "src/omnipet/public_release.py", 'actual != declared | {"release.json"}', "Verification rejects files outside the declared release set."),
    Assertion("omnipet-release-private-scan", "OmniPet", "src/omnipet/public_release.py", "contains_prohibited_release_text", "Verification scans public text for prohibited private material."),
    Assertion("omnipets-sushi-name", "OmniPets", "catalog/index.json", '"displayName": "SuShi"', "The public catalog contains SuShi."),
    Assertion("omnipets-sprite-version", "OmniPets", "catalog/index.json", '"spriteVersionNumber": 2', "SuShi uses sprite version 2."),
    Assertion("omnipets-sushi-version", "OmniPets", "catalog/index.json", '"version": "1.0.1"', "The public SuShi release is version 1.0.1."),
)

PRIVATE_BOUNDARY_TERMS = (
    "OmniPet-Production",
    "OmniPet-Program",
    "/Users/bytedance",
    "OPENAI_API_KEY",
)


def run_git(repository: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repository), *args],
        text=True,
    ).strip()


def repository_roots(portfolio: Path) -> dict[str, Path]:
    common_dir = Path(run_git(portfolio, "rev-parse", "--git-common-dir"))
    if not common_dir.is_absolute():
        common_dir = portfolio / common_dir
    workspace = common_dir.resolve().parent.parent
    return {
        "Portfolio": portfolio,
        "Mundus": workspace / "Mundus",
        "OmniPet": workspace / "OmniPet",
        "OmniPets": workspace / "OmniPets",
    }


def revision(repository: Path, name: str) -> dict[str, object]:
    return {
        "repository": name,
        "sha": run_git(repository, "rev-parse", "HEAD"),
        "branch": run_git(repository, "branch", "--show-current") or None,
        "dirty": bool(run_git(repository, "status", "--porcelain")),
    }


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs/verification/evidence"),
    )
    args = parser.parse_args()

    portfolio = Path(run_git(Path.cwd(), "rev-parse", "--show-toplevel")).resolve()
    roots = repository_roots(portfolio)
    results = []
    for assertion in ASSERTIONS:
        source = roots[assertion.repository] / assertion.source
        passed = assertion.needle in source.read_text(encoding="utf-8")
        results.append(
            {
                "id": assertion.assertion_id,
                "repository": assertion.repository,
                "source": assertion.source,
                "claim": assertion.claim,
                "passed": passed,
            }
        )

    prose = "\n".join(
        (portfolio / path).read_text(encoding="utf-8")
        for path in (
            "src/content/projects/mundus.mdx",
            "src/content/projects/omnipet.mdx",
        )
    )
    boundary_hits = sum(term in prose for term in PRIVATE_BOUNDARY_TERMS)
    passed_count = sum(bool(result["passed"]) for result in results)
    fact_evidence = {
        "schemaVersion": 1,
        "summary": {
            "assertionCount": len(results),
            "passedCount": passed_count,
            "failedCount": len(results) - passed_count,
            "privateBoundaryHitCount": boundary_hits,
        },
        "assertions": results,
    }
    revisions = {
        "schemaVersion": 1,
        "repositories": [
            revision(roots[name], name)
            for name in ("Mundus", "OmniPet", "OmniPets")
        ],
    }
    write_json(args.output_dir / "task7-fact-assertions.json", fact_evidence)
    write_json(args.output_dir / "source-revisions.json", revisions)

    print(
        f"Task 7 facts: {passed_count}/{len(results)} passed; "
        f"private boundary hits: {boundary_hits}"
    )
    for item in revisions["repositories"]:
        print(
            f"{item['repository']}: {item['sha']} "
            f"(branch={item['branch'] or 'detached'}, dirty={item['dirty']})"
        )
    return 0 if passed_count == len(results) and boundary_hits == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
