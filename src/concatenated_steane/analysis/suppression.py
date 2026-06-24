"""Level-by-level memory-error suppression scans.

The first scan compares:

- level 0: one unencoded physical qubit sampled with real Stim circuits,
- level 1: one Steane block with ideal syndrome extraction and ideal recovery.

The output is intentionally plain: a list of rows that can be written to CSV and
plotted on log-log axes.
"""

from __future__ import annotations

import csv
import math
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

    @property
    def level0_x_standard_error(self) -> float:
        """Return the binomial standard error for level-0 X failures."""

        return binomial_standard_error(self.level0_x_failure_rate, self.shots)

    @property
    def level0_z_standard_error(self) -> float:
        """Return the binomial standard error for level-0 Z failures."""

        return binomial_standard_error(self.level0_z_failure_rate, self.shots)

    @property
    def level1_x_logical_standard_error(self) -> float:
        """Return the binomial standard error for level-1 logical-X failures."""

        return binomial_standard_error(self.level1_x_logical_failure_rate, self.shots)

    @property
    def level1_z_logical_standard_error(self) -> float:
        """Return the binomial standard error for level-1 logical-Z failures."""

        return binomial_standard_error(self.level1_z_logical_failure_rate, self.shots)

    def as_csv_row(self) -> dict[str, float | int]:
        """Return this scan point in a stable CSV-friendly shape."""

        return {
            "physical_error_probability": self.physical_error_probability,
            "shots": self.shots,
            "level0_x_failure_rate": self.level0_x_failure_rate,
            "level0_x_standard_error": self.level0_x_standard_error,
            "level0_z_failure_rate": self.level0_z_failure_rate,
            "level0_z_standard_error": self.level0_z_standard_error,
            "level1_x_logical_failure_rate": self.level1_x_logical_failure_rate,
            "level1_x_logical_standard_error": self.level1_x_logical_standard_error,
            "level1_z_logical_failure_rate": self.level1_z_logical_failure_rate,
            "level1_z_logical_standard_error": self.level1_z_logical_standard_error,
            "level1_joint_logical_failure_rate": self.level1_joint_logical_failure_rate,
        }


@dataclass(frozen=True)
class Level1PseudoThresholdEstimate:
    """Pseudo-threshold estimates from level-0 and level-1 crossings."""

    x_pseudo_threshold: float | None
    z_pseudo_threshold: float | None

    def as_csv_rows(self) -> list[dict[str, str | float]]:
        """Return one CSV row per logical component."""

        return [
            {
                "logical_component": "X",
                "pseudo_threshold": _blank_if_none(self.x_pseudo_threshold),
            },
            {
                "logical_component": "Z",
                "pseudo_threshold": _blank_if_none(self.z_pseudo_threshold),
            },
        ]


def binomial_standard_error(rate: float, shots: int) -> float:
    """Return the standard error of a sampled binomial failure rate."""

    if shots <= 0:
        raise ValueError(f"shots must be positive, received {shots}.")
    return math.sqrt(rate * (1.0 - rate) / shots)


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
                "level0_x_standard_error",
                "level0_z_failure_rate",
                "level0_z_standard_error",
                "level1_x_logical_failure_rate",
                "level1_x_logical_standard_error",
                "level1_z_logical_failure_rate",
                "level1_z_logical_standard_error",
                "level1_joint_logical_failure_rate",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def estimate_level1_pseudo_thresholds(
    points: Iterable[LevelScanPoint],
) -> Level1PseudoThresholdEstimate:
    """Estimate level-1 pseudo-thresholds from sampled crossing points."""

    point_list = sorted(points, key=lambda point: point.physical_error_probability)
    return Level1PseudoThresholdEstimate(
        x_pseudo_threshold=_estimate_crossing(
            point_list,
            physical_rate_name="level0_x_failure_rate",
            logical_rate_name="level1_x_logical_failure_rate",
        ),
        z_pseudo_threshold=_estimate_crossing(
            point_list,
            physical_rate_name="level0_z_failure_rate",
            logical_rate_name="level1_z_logical_failure_rate",
        ),
    )


def write_level1_pseudo_threshold_csv(
    estimate: Level1PseudoThresholdEstimate,
    output_path: Path,
) -> None:
    """Write level-1 pseudo-threshold estimates to a CSV file."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=["logical_component", "pseudo_threshold"],
        )
        writer.writeheader()
        writer.writerows(estimate.as_csv_rows())


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


def _estimate_crossing(
    points: list[LevelScanPoint],
    *,
    physical_rate_name: str,
    logical_rate_name: str,
) -> float | None:
    """Return the first sampled physical-error rate where level 1 crosses level 0."""

    if len(points) < 2:
        return None

    previous_point = points[0]
    previous_difference = _rate_difference(
        previous_point,
        physical_rate_name=physical_rate_name,
        logical_rate_name=logical_rate_name,
    )
    if previous_difference == 0.0:
        return previous_point.physical_error_probability

    for current_point in points[1:]:
        current_difference = _rate_difference(
            current_point,
            physical_rate_name=physical_rate_name,
            logical_rate_name=logical_rate_name,
        )
        if current_difference == 0.0:
            return current_point.physical_error_probability
        if previous_difference * current_difference < 0.0:
            return _interpolate_crossing(
                previous_point,
                current_point,
                physical_rate_name=physical_rate_name,
                logical_rate_name=logical_rate_name,
            )
        previous_point = current_point
        previous_difference = current_difference
    return None


def _rate_difference(
    point: LevelScanPoint,
    *,
    physical_rate_name: str,
    logical_rate_name: str,
) -> float:
    """Return logical rate minus physical rate for one scan point."""

    return float(getattr(point, logical_rate_name)) - float(getattr(point, physical_rate_name))


def _interpolate_crossing(
    left: LevelScanPoint,
    right: LevelScanPoint,
    *,
    physical_rate_name: str,
    logical_rate_name: str,
) -> float:
    """Interpolate the crossing between two adjacent sampled scan points."""

    left_physical_rate = float(getattr(left, physical_rate_name))
    left_logical_rate = float(getattr(left, logical_rate_name))
    right_physical_rate = float(getattr(right, physical_rate_name))
    right_logical_rate = float(getattr(right, logical_rate_name))

    if min(left_physical_rate, left_logical_rate, right_physical_rate, right_logical_rate) > 0.0:
        left_height = math.log(left_logical_rate / left_physical_rate)
        right_height = math.log(right_logical_rate / right_physical_rate)
        log_left_probability = math.log(left.physical_error_probability)
        log_right_probability = math.log(right.physical_error_probability)
        fraction = -left_height / (right_height - left_height)
        return math.exp(
            log_left_probability + fraction * (log_right_probability - log_left_probability)
        )

    left_difference = left_logical_rate - left_physical_rate
    right_difference = right_logical_rate - right_physical_rate
    fraction = -left_difference / (right_difference - left_difference)
    return left.physical_error_probability + fraction * (
        right.physical_error_probability - left.physical_error_probability
    )


def _blank_if_none(value: float | None) -> str | float:
    """Represent missing threshold estimates as blank CSV cells."""

    if value is None:
        return ""
    return value
