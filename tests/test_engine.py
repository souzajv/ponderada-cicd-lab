import os

import pytest

from analyzer.engine import AnalyzerConfig, AnalyzerEngine, dispersion_between_three_series
from analyzer.models import Attitude, TelemetrySample


def sample(
    ts: str,
    altitude_m: float = 10.0,
    velocity_ms: float = 4.0,
    battery_pct: float = 90.0,
    gps_fix: int = 3,
    attitude: Attitude | None = None,
) -> TelemetrySample:
    return TelemetrySample(
        ts=ts,
        firmware_version="test-fw",
        mission_id="mission-1",
        scenario="takeoff-hover-land",
        altitude_m=altitude_m,
        velocity_ms=velocity_ms,
        battery_pct=battery_pct,
        gps_fix=gps_fix,
        attitude=attitude or Attitude(roll=0.01, pitch=0.02, yaw=0.03),
    )


def test_nominal_samples_pass() -> None:
    samples = [sample(f"2026-05-28T12:00:0{index}Z", altitude_m=5 + index) for index in range(5)]

    result = AnalyzerEngine().analyze(samples)

    assert result.verdict == "PASS"
    assert result.severity == "none"
    assert result.anomalies == []


def test_sudden_altitude_drop_fails() -> None:
    samples = [
        sample("2026-05-28T12:00:00Z", altitude_m=30),
        sample("2026-05-28T12:00:01Z", altitude_m=20),
    ]

    result = AnalyzerEngine().analyze(samples)

    assert result.verdict == "FAIL"
    assert any(anomaly.rule_id == "altitude.sudden_drop" for anomaly in result.anomalies)


def test_velocity_above_limit_fails() -> None:
    samples = [
        sample("2026-05-28T12:00:00Z"),
        sample("2026-05-28T12:00:01Z", velocity_ms=25),
    ]

    result = AnalyzerEngine().analyze(samples)

    assert result.verdict == "FAIL"
    assert any(anomaly.rule_id == "velocity.above_max" for anomaly in result.anomalies)


def test_high_dispersion_needs_review_when_no_high_severity_rule() -> None:
    samples = [
        sample(
            "2026-05-28T12:00:00Z",
            attitude=Attitude(roll=2.0, pitch=-2.0, yaw=2.5),
        ),
        sample(
            "2026-05-28T12:00:01Z",
            attitude=Attitude(roll=2.1, pitch=-2.2, yaw=2.7),
        ),
        sample(
            "2026-05-28T12:00:02Z",
            attitude=Attitude(roll=2.0, pitch=-2.3, yaw=2.8),
        ),
    ]

    result = AnalyzerEngine().analyze(samples)

    assert result.verdict == "NEEDS_REVIEW"
    assert any(anomaly.rule_id == "attitude.dispersion.high" for anomaly in result.anomalies)


def test_dispersion_metrics_are_stable() -> None:
    metrics = dispersion_between_three_series(
        [0.0, 0.0],
        [1.0, 1.0],
        [2.0, 2.0],
        bad_distance_threshold=1.5,
    )

    assert metrics["series_count"] == 3
    assert metrics["sample_count"] == 2
    assert metrics["mean_pairwise_distance"] == 1.333333
    assert metrics["max_pairwise_distance"] == 2.0
    assert metrics["bad_ratio"] == 1.0


def test_gps_instability_can_require_review() -> None:
    config = AnalyzerConfig(min_gps_fix=3)
    samples = [
        sample("2026-05-28T12:00:00Z", gps_fix=3),
        sample("2026-05-28T12:00:01Z", gps_fix=2),
        sample("2026-05-28T12:00:02Z", gps_fix=3),
    ]

    result = AnalyzerEngine(config=config).analyze(samples)

    assert result.verdict == "FAIL"
    assert any(anomaly.rule_id == "gps.fix_unstable" for anomaly in result.anomalies)


def test_forced_failure_flag() -> None:
    if os.environ.get("FORCE_TEST_FAILURE") != "1":
        pytest.skip("FORCE_TEST_FAILURE desligado")
    raise AssertionError("falha intencional para variacao de pipeline")
