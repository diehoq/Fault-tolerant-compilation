"""Tests for level-by-level suppression analysis helpers."""

from pathlib import Path

import pytest

from concatenated_steane.analysis.suppression import (
    LevelScanPoint,
    plot_level_scan,
    run_level_scan,
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

    assert output_path.read_text().splitlines() == [
        (
            "physical_error_probability,shots,level0_x_failure_rate,"
            "level0_z_failure_rate,level1_x_logical_failure_rate,"
            "level1_z_logical_failure_rate,level1_joint_logical_failure_rate"
        ),
        "0.01,10,0.1,0.2,0.03,0.04,0.01",
    ]


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
