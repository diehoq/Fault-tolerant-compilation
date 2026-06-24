"""Run a level-0 versus ideal level-1 Steane memory scan."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(REPO_ROOT / "results" / ".matplotlib"))

from concatenated_steane.analysis import (
    estimate_level1_pseudo_thresholds,
    plot_level_scan,
    run_level_scan,
    write_level1_pseudo_threshold_csv,
    write_level_scan_csv,
)

DEFAULT_PHYSICAL_ERROR_PROBABILITIES = [
    0.001,
    0.0015,
    0.0022,
    0.0032,
    0.0046,
    0.0068,
    0.01,
    0.015,
    0.022,
    0.032,
    0.046,
    0.068,
    0.1,
    0.15,
    0.22,
    0.32,
]


def main() -> None:
    """Parse arguments, run the scan, and write CSV and plot outputs."""

    parser = argparse.ArgumentParser(
        description="Compare level-0 physical memory and ideal level-1 Steane memory."
    )
    parser.add_argument(
        "--shots",
        type=int,
        default=20_000,
        help="Monte Carlo shots per physical error probability.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20260624,
        help="Base random seed.",
    )
    parser.add_argument(
        "--probabilities",
        type=float,
        nargs="+",
        default=DEFAULT_PHYSICAL_ERROR_PROBABILITIES,
        help="Physical depolarizing error probabilities to scan.",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=REPO_ROOT / "results" / "level_scan.csv",
        help="CSV output path.",
    )
    parser.add_argument(
        "--plot",
        type=Path,
        default=REPO_ROOT / "results" / "level_scan.png",
        help="Plot output path.",
    )
    parser.add_argument(
        "--thresholds",
        type=Path,
        default=REPO_ROOT / "results" / "level1_pseudo_thresholds.csv",
        help="Level-1 pseudo-threshold CSV output path.",
    )
    args = parser.parse_args()

    points = run_level_scan(args.probabilities, shots=args.shots, seed=args.seed)
    thresholds = estimate_level1_pseudo_thresholds(points)
    write_level_scan_csv(points, args.csv)
    write_level1_pseudo_threshold_csv(thresholds, args.thresholds)
    plot_level_scan(points, args.plot)

    print(f"Wrote CSV: {args.csv}")
    print(f"Wrote thresholds: {args.thresholds}")
    print(f"Wrote plot: {args.plot}")
    print(f"Estimated X pseudo-threshold: {_format_threshold(thresholds.x_pseudo_threshold)}")
    print(f"Estimated Z pseudo-threshold: {_format_threshold(thresholds.z_pseudo_threshold)}")

def _format_threshold(value: float | None) -> str:
    """Format an optional threshold estimate for terminal output."""

    if value is None:
        return "not bracketed by this scan"
    return f"{value:.6g}"


if __name__ == "__main__":
    main()
