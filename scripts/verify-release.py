#!/usr/bin/env python3
"""Run every release gate used locally and by deployment CI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from verification import browser, facts, privacy


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--portfolio-root", type=Path, default=Path.cwd())
    parser.add_argument("--mundus-root", type=Path)
    parser.add_argument("--omnipet-root", type=Path)
    parser.add_argument("--omnipets-root", type=Path)
    parser.add_argument("--dist-root", type=Path)
    args = parser.parse_args()

    portfolio = args.portfolio_root.resolve()
    workspace = (
        portfolio.parent.parent.parent
        if portfolio.parent.name == ".worktrees"
        else portfolio.parent
    )
    repositories = {
        "Mundus": (args.mundus_root or workspace / "Mundus").resolve(),
        "OmniPet": (args.omnipet_root or workspace / "OmniPet").resolve(),
        "OmniPets": (args.omnipets_root or workspace / "OmniPets").resolve(),
    }
    errors = facts.verify(
        portfolio,
        repositories,
        portfolio / "scripts/verification/facts.json",
    )
    errors.extend(
        browser.validate_all(
            portfolio / "docs/verification/evidence",
            portfolio / "docs/verification/assets",
        )
    )
    errors.extend(privacy.scan_dist(args.dist_root or portfolio / "dist"))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    fact_count = len(
        facts.load_rules(portfolio / "scripts/verification/facts.json")
    )
    print(
        f"release verification: facts={fact_count}/{fact_count} "
        "browser=pass privacy=pass"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
