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

from concatenated_steane.analysis import plot_level_scan, run_level_scan, write_level_scan_csv


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
        default=[0.001, 0.003, 0.01, 0.03, 0.1],
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
    args = parser.parse_args()

    points = run_level_scan(args.probabilities, shots=args.shots, seed=args.seed)
    write_level_scan_csv(points, args.csv)
    plot_level_scan(points, args.plot)

    print(f"Wrote CSV: {args.csv}")
    print(f"Wrote plot: {args.plot}")


if __name__ == "__main__":
    main()
