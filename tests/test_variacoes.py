import pytest

from analyzer.engine import AnalyzerEngine
from analyzer.models import Attitude, TelemetrySample


def _sample(altitude_m: float) -> TelemetrySample:
    return TelemetrySample(
        ts="2026-06-07T12:00:00Z",
        firmware_version="batch-fw",
        mission_id="mission-batch",
        scenario="hover-grid",
        altitude_m=altitude_m,
        velocity_ms=2.0,
        battery_pct=88.0,
        gps_fix=3,
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
    )


@pytest.mark.parametrize("altitude_m", [5.0, 6.5, 8.0, 9.5, 11.0, 12.5, 14.0, 15.5])
def test_batch_nominal_altitudes_pass(altitude_m: float) -> None:
    result = AnalyzerEngine().analyze([_sample(altitude_m)])
    assert result.verdict == "PASS"


@pytest.mark.parametrize("velocity_ms", [1.0, 2.5, 4.0, 5.5, 7.0, 8.5, 10.0])
def test_batch_velocity_within_limit(velocity_ms: float) -> None:
    sample = TelemetrySample(
        ts="2026-06-07T12:00:01Z",
        firmware_version="batch-fw",
        mission_id="mission-batch",
        scenario="hover-grid",
        altitude_m=10.0,
        velocity_ms=velocity_ms,
        battery_pct=80.0,
        gps_fix=3,
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
    )
    result = AnalyzerEngine().analyze([sample])
    assert result.verdict == "PASS"
