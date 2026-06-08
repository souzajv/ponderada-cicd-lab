from __future__ import annotations

import os
from dataclasses import dataclass
from time import perf_counter

from analyzer.ml import RiskModel
from analyzer.models import (
    AnalysisResult,
    Anomaly,
    TelemetrySample,
    verdict_from_severity,
    worst_severity,
)

DEFAULT_MIN_ALTITUDE_M = -0.5
DEFAULT_MAX_ALTITUDE_M = 120.0
DEFAULT_MAX_ALTITUDE_DROP_M = 8.0
DEFAULT_MAX_VELOCITY_MS = 18.0
DEFAULT_MIN_BATTERY_PCT = 20.0
DEFAULT_MIN_GPS_FIX = 3
DEFAULT_DISPERSION_MEAN_PAIRWISE_THRESHOLD = 1.25
DEFAULT_DISPERSION_MAX_PAIRWISE_THRESHOLD = 2.25
DEFAULT_DISPERSION_BAD_RATIO_THRESHOLD = 0.25


@dataclass(frozen=True)
class AnalyzerConfig:
    min_altitude_m: float = DEFAULT_MIN_ALTITUDE_M
    max_altitude_m: float = DEFAULT_MAX_ALTITUDE_M
    max_altitude_drop_m: float = DEFAULT_MAX_ALTITUDE_DROP_M
    max_velocity_ms: float = DEFAULT_MAX_VELOCITY_MS
    min_battery_pct: float = DEFAULT_MIN_BATTERY_PCT
    min_gps_fix: int = DEFAULT_MIN_GPS_FIX
    dispersion_mean_pairwise_threshold: float = DEFAULT_DISPERSION_MEAN_PAIRWISE_THRESHOLD
    dispersion_max_pairwise_threshold: float = DEFAULT_DISPERSION_MAX_PAIRWISE_THRESHOLD
    dispersion_bad_ratio_threshold: float = DEFAULT_DISPERSION_BAD_RATIO_THRESHOLD

    @classmethod
    def from_env(cls) -> AnalyzerConfig:
        return cls(
            min_altitude_m=_env_float("ANALYZER_MIN_ALTITUDE_M", DEFAULT_MIN_ALTITUDE_M),
            max_altitude_m=_env_float("ANALYZER_MAX_ALTITUDE_M", DEFAULT_MAX_ALTITUDE_M),
            max_altitude_drop_m=_env_float(
                "ANALYZER_MAX_ALTITUDE_DROP_M",
                DEFAULT_MAX_ALTITUDE_DROP_M,
            ),
            max_velocity_ms=_env_float("ANALYZER_MAX_VELOCITY_MS", DEFAULT_MAX_VELOCITY_MS),
            min_battery_pct=_env_float("ANALYZER_MIN_BATTERY_PCT", DEFAULT_MIN_BATTERY_PCT),
            min_gps_fix=_env_int("ANALYZER_MIN_GPS_FIX", DEFAULT_MIN_GPS_FIX),
            dispersion_mean_pairwise_threshold=_env_float(
                "ANALYZER_DISPERSION_MEAN_PAIRWISE_THRESHOLD",
                DEFAULT_DISPERSION_MEAN_PAIRWISE_THRESHOLD,
            ),
            dispersion_max_pairwise_threshold=_env_float(
                "ANALYZER_DISPERSION_MAX_PAIRWISE_THRESHOLD",
                DEFAULT_DISPERSION_MAX_PAIRWISE_THRESHOLD,
            ),
            dispersion_bad_ratio_threshold=_env_float(
                "ANALYZER_DISPERSION_BAD_RATIO_THRESHOLD",
                DEFAULT_DISPERSION_BAD_RATIO_THRESHOLD,
            ),
        )


class AnalyzerEngine:
    def __init__(self, config: AnalyzerConfig | None = None, risk_model: RiskModel | None = None):
        self.config = config or AnalyzerConfig.from_env()
        self.risk_model = risk_model or RiskModel.disabled()

    def analyze(self, samples: list[TelemetrySample]) -> AnalysisResult:
        started_at = perf_counter()
        if not samples:
            raise ValueError("cannot analyze an empty telemetry sample set")

        ordered = sorted(samples, key=lambda sample: sample.ts)
        anomalies: list[Anomaly] = []
        anomalies.extend(self._altitude_anomalies(ordered))
        anomalies.extend(self._velocity_anomalies(ordered))
        anomalies.extend(self._battery_anomalies(ordered))
        anomalies.extend(self._gps_anomalies(ordered))

        dispersion = dispersion_between_three_series(
            [sample.attitude.roll for sample in ordered],
            [sample.attitude.pitch for sample in ordered],
            [sample.attitude.yaw for sample in ordered],
            self.config.dispersion_mean_pairwise_threshold,
        )
        if (
            dispersion["mean_pairwise_distance"] > self.config.dispersion_mean_pairwise_threshold
            or dispersion["max_pairwise_distance"] > self.config.dispersion_max_pairwise_threshold
            or dispersion["bad_ratio"] > self.config.dispersion_bad_ratio_threshold
        ):
            anomalies.append(
                Anomaly(
                    rule_id="attitude.dispersion.high",
                    severity="medium",
                    message="High dispersion between roll, pitch and yaw proxy series.",
                    sample_ts=None,
                    observed_value=round(dispersion["mean_pairwise_distance"], 4),
                    threshold=self.config.dispersion_mean_pairwise_threshold,
                )
            )

        ml_result = self.risk_model.evaluate(ordered)
        severity = worst_severity(anomalies)
        verdict = verdict_from_severity(severity)
        metrics = self._summary_metrics(ordered)
        metrics["attitude_dispersion"] = dispersion
        processing_time_ms = (perf_counter() - started_at) * 1000

        return AnalysisResult(
            mission_id=ordered[0].mission_id,
            firmware_version=ordered[0].firmware_version,
            verdict=verdict,
            severity=severity,
            confidence=self._confidence(anomalies, len(ordered)),
            processing_time_ms=round(processing_time_ms, 3),
            metrics=metrics,
            anomalies=anomalies,
            ml=ml_result,
        )

    def _altitude_anomalies(self, samples: list[TelemetrySample]) -> list[Anomaly]:
        anomalies: list[Anomaly] = []
        previous: TelemetrySample | None = None
        for sample in samples:
            if sample.altitude_m < self.config.min_altitude_m:
                anomalies.append(
                    Anomaly(
                        rule_id="altitude.below_min",
                        severity="high",
                        message="Altitude dropped below the expected minimum.",
                        sample_ts=sample.ts,
                        observed_value=sample.altitude_m,
                        threshold=self.config.min_altitude_m,
                    )
                )
            if sample.altitude_m > self.config.max_altitude_m:
                anomalies.append(
                    Anomaly(
                        rule_id="altitude.above_max",
                        severity="high",
                        message="Altitude exceeded the expected ceiling.",
                        sample_ts=sample.ts,
                        observed_value=sample.altitude_m,
                        threshold=self.config.max_altitude_m,
                    )
                )
            if previous is not None:
                drop = previous.altitude_m - sample.altitude_m
                if drop > self.config.max_altitude_drop_m:
                    anomalies.append(
                        Anomaly(
                            rule_id="altitude.sudden_drop",
                            severity="critical",
                            message="Altitude dropped too quickly between consecutive samples.",
                            sample_ts=sample.ts,
                            observed_value=round(drop, 4),
                            threshold=self.config.max_altitude_drop_m,
                        )
                    )
            previous = sample
        return anomalies

    def _velocity_anomalies(self, samples: list[TelemetrySample]) -> list[Anomaly]:
        return [
            Anomaly(
                rule_id="velocity.above_max",
                severity="high",
                message="Velocity exceeded the configured safe limit.",
                sample_ts=sample.ts,
                observed_value=sample.velocity_ms,
                threshold=self.config.max_velocity_ms,
            )
            for sample in samples
            if sample.velocity_ms > self.config.max_velocity_ms
        ]

    def _battery_anomalies(self, samples: list[TelemetrySample]) -> list[Anomaly]:
        low_battery_samples = [
            sample for sample in samples if sample.battery_pct < self.config.min_battery_pct
        ]
        if not low_battery_samples:
            return []
        first = low_battery_samples[0]
        return [
            Anomaly(
                rule_id="battery.below_min",
                severity="medium",
                message="Battery went below the configured minimum during the mission.",
                sample_ts=first.ts,
                observed_value=first.battery_pct,
                threshold=self.config.min_battery_pct,
            )
        ]

    def _gps_anomalies(self, samples: list[TelemetrySample]) -> list[Anomaly]:
        bad_samples = [sample for sample in samples if sample.gps_fix < self.config.min_gps_fix]
        if not bad_samples:
            return []
        bad_ratio = len(bad_samples) / len(samples)
        severity = "high" if bad_ratio > 0.2 else "medium"
        return [
            Anomaly(
                rule_id="gps.fix_unstable",
                severity=severity,
                message="GPS fix was below the configured minimum.",
                sample_ts=bad_samples[0].ts,
                observed_value=round(bad_ratio, 4),
                threshold=self.config.min_gps_fix,
            )
        ]

    @staticmethod
    def _summary_metrics(samples: list[TelemetrySample]) -> dict[str, float | int]:
        altitudes = [sample.altitude_m for sample in samples]
        velocities = [sample.velocity_ms for sample in samples]
        batteries = [sample.battery_pct for sample in samples]
        return {
            "sample_count": len(samples),
            "altitude_min_m": min(altitudes),
            "altitude_max_m": max(altitudes),
            "velocity_max_ms": max(velocities),
            "battery_min_pct": min(batteries),
        }

    @staticmethod
    def _confidence(anomalies: list[Anomaly], sample_count: int) -> float:
        if sample_count < 5:
            return 0.55
        penalty = min(0.45, len(anomalies) * 0.05)
        return round(0.95 - penalty, 2)


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw in (None, ""):
        return default
    return float(raw)


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw in (None, ""):
        return default
    return int(raw)


def dispersion_between_three_series(
    first: list[float],
    second: list[float],
    third: list[float],
    bad_distance_threshold: float,
) -> dict[str, float | int]:
    if not (len(first) == len(second) == len(third)):
        raise ValueError("dispersion series must have the same length")
    if not first:
        raise ValueError("dispersion series must not be empty")

    pairwise_distances: list[float] = []
    squared_error_sum = 0.0
    bad_points = 0

    for a, b, c in zip(first, second, third, strict=True):
        distances = [abs(a - b), abs(a - c), abs(b - c)]
        pairwise_distances.extend(distances)
        point_mean = (a + b + c) / 3
        squared_error_sum += (a - point_mean) ** 2
        squared_error_sum += (b - point_mean) ** 2
        squared_error_sum += (c - point_mean) ** 2
        if max(distances) > bad_distance_threshold:
            bad_points += 1

    sample_count = len(first)
    return {
        "series_count": 3,
        "sample_count": sample_count,
        "mean_pairwise_distance": round(sum(pairwise_distances) / len(pairwise_distances), 6),
        "max_pairwise_distance": round(max(pairwise_distances), 6),
        "rmse_to_mean": round((squared_error_sum / (sample_count * 3)) ** 0.5, 6),
        "bad_ratio": round(bad_points / sample_count, 6),
    }
