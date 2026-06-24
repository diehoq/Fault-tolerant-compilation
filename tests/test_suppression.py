"""Tests for level-by-level suppression analysis helpers."""

import csv
from pathlib import Path

import pytest

from concatenated_steane.analysis.suppression import (
    LevelScanPoint,
    binomial_standard_error,
    estimate_level1_pseudo_thresholds,
    plot_level_scan,
    run_level_scan,
    write_level1_pseudo_threshold_csv,
    write_level_scan_csv,
)


def test_level_scan_has_zero_failures_when_noise_is_zero() -> None:
    points = run_level_scan([0.0], shots=5, seed=123)

    assert points == [
        LevelScanPoint(
            physical_error_probability=0.0,
            shots=5,
            level0_x_failure_rate=0.0,
            level0_z_failure_rate=0.0,
            level1_x_logical_failure_rate=0.0,
            level1_z_logical_failure_rate=0.0,
            level1_joint_logical_failure_rate=0.0,
        )
    ]


def test_level_scan_requires_positive_shots() -> None:
    with pytest.raises(ValueError, match="positive"):
        run_level_scan([0.01], shots=0)


def test_level_scan_csv_has_stable_header(tmp_path: Path) -> None:
    output_path = tmp_path / "scan.csv"
    points = [
        LevelScanPoint(
            physical_error_probability=0.01,
            shots=10,
            level0_x_failure_rate=0.1,
            level0_z_failure_rate=0.2,
            level1_x_logical_failure_rate=0.03,
            level1_z_logical_failure_rate=0.04,
            level1_joint_logical_failure_rate=0.01,
        )
    ]

    write_level_scan_csv(points, output_path)

    with output_path.open(newline="") as input_file:
        rows = list(csv.DictReader(input_file))

    assert rows[0].keys() == {
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
    }
    assert float(rows[0]["physical_error_probability"]) == 0.01
    assert int(rows[0]["shots"]) == 10
    assert float(rows[0]["level0_x_standard_error"]) == pytest.approx(
        binomial_standard_error(0.1, 10)
    )
    assert float(rows[0]["level1_z_logical_standard_error"]) == pytest.approx(
        binomial_standard_error(0.04, 10)
    )


def test_binomial_standard_error_matches_textbook_formula() -> None:
    assert binomial_standard_error(0.25, 100) == pytest.approx(0.04330127018922193)


def test_binomial_standard_error_requires_positive_shots() -> None:
    with pytest.raises(ValueError, match="positive"):
        binomial_standard_error(0.25, 0)


def test_level1_pseudo_thresholds_interpolate_crossings() -> None:
    points = [
        LevelScanPoint(
            physical_error_probability=0.01,
            shots=100,
            level0_x_failure_rate=0.1,
            level0_z_failure_rate=0.1,
            level1_x_logical_failure_rate=0.01,
            level1_z_logical_failure_rate=0.01,
            level1_joint_logical_failure_rate=0.0,
        ),
        LevelScanPoint(
            physical_error_probability=0.1,
            shots=100,
            level0_x_failure_rate=0.1,
            level0_z_failure_rate=0.1,
            level1_x_logical_failure_rate=1.0,
            level1_z_logical_failure_rate=1.0,
            level1_joint_logical_failure_rate=1.0,
        ),
    ]

    estimate = estimate_level1_pseudo_thresholds(points)

    assert estimate.x_pseudo_threshold == pytest.approx(0.03162277660168379)
    assert estimate.z_pseudo_threshold == pytest.approx(0.03162277660168379)


def test_level1_pseudo_thresholds_report_missing_crossing() -> None:
    points = [
        LevelScanPoint(
            physical_error_probability=0.01,
            shots=100,
            level0_x_failure_rate=0.1,
            level0_z_failure_rate=0.1,
            level1_x_logical_failure_rate=0.01,
            level1_z_logical_failure_rate=0.01,
            level1_joint_logical_failure_rate=0.0,
        ),
        LevelScanPoint(
            physical_error_probability=0.1,
            shots=100,
            level0_x_failure_rate=0.2,
            level0_z_failure_rate=0.2,
            level1_x_logical_failure_rate=0.02,
            level1_z_logical_failure_rate=0.02,
            level1_joint_logical_failure_rate=0.0,
        ),
    ]

    estimate = estimate_level1_pseudo_thresholds(points)

    assert estimate.x_pseudo_threshold is None
    assert estimate.z_pseudo_threshold is None


def test_level1_pseudo_threshold_csv_has_one_row_per_component(tmp_path: Path) -> None:
    output_path = tmp_path / "thresholds.csv"
    estimate = estimate_level1_pseudo_thresholds(
        [
            LevelScanPoint(
                physical_error_probability=0.01,
                shots=100,
                level0_x_failure_rate=0.1,
                level0_z_failure_rate=0.1,
                level1_x_logical_failure_rate=0.01,
                level1_z_logical_failure_rate=0.01,
                level1_joint_logical_failure_rate=0.0,
            ),
            LevelScanPoint(
                physical_error_probability=0.1,
                shots=100,
                level0_x_failure_rate=0.1,
                level0_z_failure_rate=0.1,
                level1_x_logical_failure_rate=1.0,
                level1_z_logical_failure_rate=1.0,
                level1_joint_logical_failure_rate=1.0,
            ),
        ]
    )

    write_level1_pseudo_threshold_csv(estimate, output_path)

    with output_path.open(newline="") as input_file:
        rows = list(csv.DictReader(input_file))

    assert rows[0]["logical_component"] == "X"
    assert float(rows[0]["pseudo_threshold"]) == pytest.approx(0.03162277660168379)
    assert rows[1]["logical_component"] == "Z"
    assert float(rows[1]["pseudo_threshold"]) == pytest.approx(0.03162277660168379)


def test_level_scan_plot_writes_png(tmp_path: Path) -> None:
    output_path = tmp_path / "scan.png"
    points = [
        LevelScanPoint(
            physical_error_probability=0.01,
            shots=10,
            level0_x_failure_rate=0.1,
            level0_z_failure_rate=0.1,
            level1_x_logical_failure_rate=0.01,
            level1_z_logical_failure_rate=0.01,
            level1_joint_logical_failure_rate=0.0,
        )
    ]

    plot_level_scan(points, output_path)

    assert output_path.read_bytes().startswith(b"\x89PNG")


def test_level_scan_plot_requires_points(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="At least one"):
        plot_level_scan([], tmp_path / "scan.png")
