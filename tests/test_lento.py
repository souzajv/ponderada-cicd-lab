import time

import pytest

from analyzer.engine import AnalyzerEngine
from analyzer.models import Attitude, TelemetrySample


@pytest.mark.slow
def test_slow_hover_analysis() -> None:
    time.sleep(3)
    sample = TelemetrySample(
        ts="2026-06-07T12:00:00Z",
        firmware_version="slow-fw",
        mission_id="mission-slow",
        scenario="hover-long",
        altitude_m=9.5,
        velocity_ms=0.2,
        battery_pct=75.0,
        gps_fix=3,
        attitude=Attitude(roll=0.01, pitch=0.01, yaw=0.01),
    )
    result = AnalyzerEngine().analyze([sample])
    assert result.verdict == "PASS"
