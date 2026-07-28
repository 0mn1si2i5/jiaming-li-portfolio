#!/usr/bin/env python3
"""Verify Task 7 public claims and emit sanitized, deterministic evidence."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Assertion:
    assertion_id: str
    portfolio_source: str
    portfolio_needle: str
    evidence_repository: str
    evidence_source: str
    evidence_needle: str
    claim: str


@dataclass(frozen=True)
class ExpectedRevision:
    sha: str
    branch: str = "main"
    clean: bool = True


EXPECTED_REVISIONS = {
    "Mundus": ExpectedRevision("b7b2d0f9e453efd8be83216a43e642f0ee7350ed"),
    "OmniPet": ExpectedRevision("f08e47c7dcee1bf7d89e1c673c73abb6fa90c20d"),
    "OmniPets": ExpectedRevision("081b7c6f651183987c79c4321ff46e1b082e03b7"),
}

MUNDUS = "src/content/projects/mundus.mdx"
OMNIPET = "src/content/projects/omnipet.mdx"


def paired(
    assertion_id: str,
    portfolio_source: str,
    portfolio_needle: str,
    evidence_repository: str,
    evidence_source: str,
    evidence_needle: str,
    claim: str,
) -> Assertion:
    return Assertion(
        assertion_id,
        portfolio_source,
        portfolio_needle,
        evidence_repository,
        evidence_source,
        evidence_needle,
        claim,
    )


ASSERTIONS = (
    paired("mundus-three-modes", MUNDUS, "three modes—spatial, human, and temporal", "Mundus", "README.md", "three modes:", "Mundus publicly presents three scientific modes."),
    paired("mundus-mode-order", MUNDUS, "three modes—spatial, human, and temporal", "Mundus", "src/features/modes/modeRegistry.ts", "MODE_ORDER = ['antipodes', 'development', 'sunline']", "The three modes have a stable registry order."),
    paired("mundus-mode-version", MUNDUS, "A mode definition names its version", "Mundus", "src/features/modes/modeRegistry.ts", "version: 1;", "Mode definitions are versioned."),
    paired("mundus-mode-categories", MUNDUS, "three modes—spatial, human, and temporal", "Mundus", "src/features/modes/modeRegistry.ts", "category: 'temporal'", "Mode definitions include scientific categories."),
    paired("mundus-development-resources", MUNDUS, "each asks for different state, data, and evidence", "Mundus", "src/features/modes/modeRegistry.ts", "resources: ['natural-earth-countries-110m', 'undp-hdr-2025-development']", "Development declares its Natural Earth and UNDP resources."),
    paired("mundus-data-registry", MUNDUS, "Data manifests separately record sources, licenses, transformations, checksums, missing-value policies, and boundary caveats", "Mundus", "src/data/registry.ts", "missingValuePolicy: z.string().min(1)", "The data registry validates provenance and boundary metadata."),
    paired("mundus-sunline-min-year", MUNDUS, "Inputs are limited to 2000–2099", "Mundus", "src/features/sunline/solar.ts", "Date.UTC(2000, 0, 1)", "Sunline starts at 2000 UTC."),
    paired("mundus-sunline-max-year", MUNDUS, "Inputs are limited to 2000–2099", "Mundus", "src/features/sunline/solar.ts", "Date.UTC(2099, 11, 31, 23, 59)", "Sunline ends at the final minute of 2099 UTC."),
    paired("mundus-sunrise-altitude", MUNDUS, "Sunrise and sunset use an apparent altitude of `-0.833°`", "Mundus", "src/features/sunline/solar.ts", "SUNRISE_ALTITUDE_DEGREES = -0.833", "Sunrise and sunset use an apparent altitude of -0.833 degrees."),
    paired("mundus-civil-twilight", MUNDUS, "`0°` to `-6°` is civil twilight", "Mundus", "src/features/sunline/solar.ts", "'civil-twilight'", "Solar observations expose civil twilight."),
    paired("mundus-polar-day", MUNDUS, "explicit polar-day or polar-night states", "Mundus", "src/features/sunline/solar.ts", "'polar-day'", "Solar events expose polar day."),
    paired("mundus-polar-night", MUNDUS, "explicit polar-day or polar-night states", "Mundus", "src/features/sunline/solar.ts", "'polar-night'", "Solar events expose polar night."),
    paired("mundus-city-count", MUNDUS, "6,944 eligible major-city records", "Mundus", "DATA_SOURCES.md", "6,944 records", "The immutable GeoNames index contains 6,944 records."),
    paired("mundus-undp-years", MUNDUS, "series for 1990–2023", "Mundus", "DATA_SOURCES.md", "covering 1990–2023", "The UNDP series covers 1990 through 2023."),
    paired("mundus-vector-quality", MUNDUS, "Low quality requests 110m geometry; medium and high request 50m", "Mundus", "README.md", "low quality\nloads 110m, while medium/high quality loads 50m", "Vector quality uses 110m for low and 50m for medium/high."),
    paired("mundus-solar-method", MUNDUS, "NOAA/Meeus-style equations", "Mundus", "DATA_SOURCES.md", "NOAA/Meeus-style approximations", "Sunline uses NOAA/Meeus-style approximations."),
    paired("omnipet-open-engine", OMNIPET, "open-source Python engine and CLI for sprite v2 production", "OmniPet", "README.md", "桌宠 sprite v2 的开源引擎", "OmniPet is a public sprite v2 production engine."),
    paired("omnipet-no-auto-retry", OMNIPET, "persists a failed generation instead of retrying automatically", "OmniPet", "docs/architecture.md", "There is no automatic retry", "Provider failures are not retried automatically."),
    paired("omnipet-transactional-repair", OMNIPET, "repair archives that job transactionally", "OmniPet", "docs/architecture.md", "Repair archives the selected completed or failed visual job transactionally", "Repair archives a selected visual job transactionally."),
    paired("omnipet-release-allowlist", OMNIPET, "Export creates a closed, allowlisted bundle", "OmniPet", "docs/architecture.md", "closed allowlist", "Public release export uses a closed allowlist."),
    paired("omnipet-clean-verification", OMNIPET, "requires no generation credential or production project", "OmniPet", "docs/architecture.md", "requires no provider credentials or production project", "Public verification requires neither credentials nor a production project."),
    paired("omnipet-standard-rows", OMNIPET, "including nine standard action rows", "OmniPet", "docs/generation-workflow.md", "nine standard rows", "The atlas contains nine standard action rows."),
    paired("omnipet-atlas-grid", OMNIPET, "eight-column, eleven-row atlas", "OmniPet", "docs/generation-workflow.md", "8x11 atlas", "The final atlas uses an 8 by 11 grid."),
    paired("omnipet-atlas-size", OMNIPET, "`1536 × 2288`", "OmniPet", "docs/generation-workflow.md", "1536x2288", "The final atlas is exactly 1536 by 2288 pixels."),
    paired("omnipet-look-rows", OMNIPET, "two directional rows", "OmniPet", "docs/generation-workflow.md", "nine standard rows plus two look rows", "The final atlas adds two directional rows."),
    paired("omnipet-release-atlas", OMNIPET, "sprite atlas, preview, public documentation", "OmniPet", "src/omnipet/public_release.py", '"spritesheet.webp"', "The release contract requires the sprite atlas."),
    paired("omnipet-release-hash", OMNIPET, "Every declared file is bound by SHA-256", "OmniPet", "src/omnipet/public_release.py", "_HASH = re.compile", "Release file records use SHA-256 hashes."),
    paired("omnipet-release-closed-set", OMNIPET, "rejects extra or unsafe material", "OmniPet", "src/omnipet/public_release.py", 'actual != declared | {"release.json"}', "Verification rejects files outside the declared release set."),
    paired("omnipet-release-commands", OMNIPET, "release export and verification path", "OmniPet", "README.md", "omnipet release verify release-work/my-pet", "The public engine documents release export and verification."),
    paired("omnipets-sushi-version", OMNIPET, "SuShi v1.0.1 is the current installable sprite v2 example", "OmniPets", "README.md", "当前示例：SuShi v1.0.1", "The public catalog documents SuShi v1.0.1."),
    paired("omnipets-sprite-version", OMNIPET, "installable sprite v2 example", "OmniPets", "catalog/index.json", '"spriteVersionNumber": 2', "SuShi uses sprite version 2."),
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


def validate_revision(
    actual: dict[str, object],
    expected: ExpectedRevision,
) -> dict[str, object]:
    failures = []
    if actual["sha"] != expected.sha:
        failures.append("sha")
    if actual["branch"] != expected.branch:
        failures.append("branch")
    actual_clean = not bool(actual["dirty"])
    if actual_clean != expected.clean:
        failures.append("clean")
    return {
        **actual,
        "expectedSha": expected.sha,
        "expectedBranch": expected.branch,
        "expectedClean": expected.clean,
        "failures": failures,
        "passed": not failures,
    }


def evaluate_assertion(
    assertion: Assertion,
    roots: dict[str, Path],
) -> dict[str, object]:
    portfolio_text = (
        roots["Portfolio"] / assertion.portfolio_source
    ).read_text(encoding="utf-8")
    evidence_text = (
        roots[assertion.evidence_repository] / assertion.evidence_source
    ).read_text(encoding="utf-8")
    claim_passed = assertion.portfolio_needle in portfolio_text
    evidence_passed = assertion.evidence_needle in evidence_text
    return {
        "id": assertion.assertion_id,
        "claim": assertion.claim,
        "portfolioSource": assertion.portfolio_source,
        "evidenceRepository": assertion.evidence_repository,
        "evidenceSource": assertion.evidence_source,
        "claimPassed": claim_passed,
        "evidencePassed": evidence_passed,
        "passed": claim_passed and evidence_passed,
    }


def write_json_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        dir=path.parent,
        text=True,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            output.write(
                json.dumps(
                    value,
                    ensure_ascii=True,
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            )
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


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
    revision_results = [
        validate_revision(
            revision(roots[name], name),
            EXPECTED_REVISIONS[name],
        )
        for name in ("Mundus", "OmniPet", "OmniPets")
    ]
    revision_gate_passed = all(
        bool(item["passed"]) for item in revision_results
    )
    if not revision_gate_passed:
        for item in revision_results:
            if not item["passed"]:
                print(
                    f"{item['repository']} revision gate failed: "
                    f"{','.join(item['failures'])}"
                )
        return 1

    results = [evaluate_assertion(assertion, roots) for assertion in ASSERTIONS]

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
        "schemaVersion": 2,
        "gatePassed": revision_gate_passed,
        "repositories": revision_results,
    }
    success = passed_count == len(results) and boundary_hits == 0
    if not success:
        print(
            f"Task 7 facts failed: {passed_count}/{len(results)}; "
            f"private boundary hits: {boundary_hits}"
        )
        return 1

    write_json_atomic(
        args.output_dir / "task7-fact-assertions.json",
        fact_evidence,
    )
    write_json_atomic(
        args.output_dir / "source-revisions.json",
        revisions,
    )

    print(
        f"Task 7 facts: {passed_count}/{len(results)} passed; "
        f"private boundary hits: {boundary_hits}"
    )
    for item in revisions["repositories"]:
        print(
            f"{item['repository']}: {item['sha']} "
            f"(branch={item['branch'] or 'detached'}, dirty={item['dirty']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
