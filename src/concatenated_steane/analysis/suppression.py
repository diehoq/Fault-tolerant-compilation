"""Level-by-level memory-error suppression scans.

The first scan compares:

- level 0: one unencoded physical qubit sampled with real Stim circuits,
- level 1: one Steane block with ideal syndrome extraction and ideal recovery.

The output is intentionally plain: a list of rows that can be written to CSV and
plotted on log-log axes.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt

from ..noise import IndependentPauliMemoryNoise
from ..simulation.direct_stim import sample_level0_memory_failures
from ..simulation.ideal_memory import sample_level1_ideal_memory_failures


@dataclass(frozen=True)
class LevelScanPoint:
    """One physical-noise point in a level-0 versus level-1 scan."""

    physical_error_probability: float
    shots: int
    level0_x_failure_rate: float
    level0_z_failure_rate: float
    level1_x_logical_failure_rate: float
    level1_z_logical_failure_rate: float
    level1_joint_logical_failure_rate: float

    def as_csv_row(self) -> dict[str, float | int]:
        """Return this scan point in a stable CSV-friendly shape."""

        return {
            "physical_error_probability": self.physical_error_probability,
            "shots": self.shots,
            "level0_x_failure_rate": self.level0_x_failure_rate,
            "level0_z_failure_rate": self.level0_z_failure_rate,
            "level1_x_logical_failure_rate": self.level1_x_logical_failure_rate,
            "level1_z_logical_failure_rate": self.level1_z_logical_failure_rate,
            "level1_joint_logical_failure_rate": self.level1_joint_logical_failure_rate,
        }


def run_level_scan(
    physical_error_probabilities: Iterable[float],
    *,
    shots: int,
    seed: int = 0,
) -> list[LevelScanPoint]:
    """Sample level-0 and ideal level-1 memory failure rates for each noise value."""

    if shots <= 0:
        raise ValueError(f"shots must be positive, received {shots}.")

    points: list[LevelScanPoint] = []
    for index, probability in enumerate(physical_error_probabilities):
        noise = IndependentPauliMemoryNoise.depolarizing(probability)
        base_seed = seed + 10_000 * index
        level0_x = sample_level0_memory_failures(
            noise,
            basis="Z",
            shots=shots,
            seed=base_seed + 1,
        )
        level0_z = sample_level0_memory_failures(
            noise,
            basis="X",
            shots=shots,
            seed=base_seed + 2,
        )
        level1 = sample_level1_ideal_memory_failures(
            noise,
            shots=shots,
            seed=base_seed + 3,
        )
        points.append(
            LevelScanPoint(
                physical_error_probability=float(probability),
                shots=shots,
                level0_x_failure_rate=level0_x.failure_rate,
                level0_z_failure_rate=level0_z.failure_rate,
                level1_x_logical_failure_rate=level1.x_logical_failure_rate,
                level1_z_logical_failure_rate=level1.z_logical_failure_rate,
                level1_joint_logical_failure_rate=level1.joint_logical_failure_rate,
            )
        )
    return points


def write_level_scan_csv(points: Iterable[LevelScanPoint], output_path: Path) -> None:
    """Write scan points to a CSV file."""

    rows = [point.as_csv_row() for point in points]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=[
                "physical_error_probability",
                "shots",
                "level0_x_failure_rate",
                "level0_z_failure_rate",
                "level1_x_logical_failure_rate",
                "level1_z_logical_failure_rate",
                "level1_joint_logical_failure_rate",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def plot_level_scan(points: Iterable[LevelScanPoint], output_path: Path) -> None:
    """Create a log-log plot comparing physical and logical failure rates."""

    point_list = list(points)
    if not point_list:
        raise ValueError("At least one scan point is required to create a plot.")

    physical_probabilities = [point.physical_error_probability for point in point_list]
    level0_x_rates = [_positive_for_log_plot(point.level0_x_failure_rate) for point in point_list]
    level0_z_rates = [_positive_for_log_plot(point.level0_z_failure_rate) for point in point_list]
    level1_x_rates = [
        _positive_for_log_plot(point.level1_x_logical_failure_rate) for point in point_list
    ]
    level1_z_rates = [
        _positive_for_log_plot(point.level1_z_logical_failure_rate) for point in point_list
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(7, 5), constrained_layout=True)
    axis.loglog(physical_probabilities, level0_x_rates, "o-", label="Level 0 X failures")
    axis.loglog(physical_probabilities, level0_z_rates, "o-", label="Level 0 Z failures")
    axis.loglog(physical_probabilities, level1_x_rates, "s-", label="Level 1 logical X")
    axis.loglog(physical_probabilities, level1_z_rates, "s-", label="Level 1 logical Z")
    axis.set_xlabel("Physical depolarizing error probability per memory interval")
    axis.set_ylabel("Failure probability per memory interval")
    axis.set_title("Ideal Steane Level-1 Memory Suppression")
    axis.grid(True, which="both", alpha=0.3)
    axis.legend()
    figure.savefig(output_path, dpi=200)
    plt.close(figure)


def _positive_for_log_plot(value: float) -> float:
    """Replace zero Monte Carlo estimates by a small positive plotting floor."""

    if value > 0.0:
        return value
    return 1e-12
