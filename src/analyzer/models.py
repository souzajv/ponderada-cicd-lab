from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

SEVERITY_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class Attitude:
    roll: float
    pitch: float
    yaw: float


@dataclass(frozen=True)
class TelemetrySample:
    ts: str
    firmware_version: str
    mission_id: str
    scenario: str
    altitude_m: float
    velocity_ms: float
    battery_pct: float
    gps_fix: int
    attitude: Attitude


@dataclass(frozen=True)
class Anomaly:
    rule_id: str
    severity: str
    message: str
    sample_ts: str | None = None
    observed_value: float | str | bool | None = None
    threshold: float | str | bool | None = None


@dataclass(frozen=True)
class MlResult:
    enabled: bool = False
    model_name: str | None = None
    risk_score: float | None = None
    notes: str = "ML risk model disabled."

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "model_name": self.model_name,
            "risk_score": self.risk_score,
            "notes": self.notes,
        }


@dataclass
class AnalysisResult:
    mission_id: str
    firmware_version: str
    verdict: str
    severity: str
    confidence: float
    processing_time_ms: float
    metrics: dict[str, Any]
    anomalies: list[Anomaly] = field(default_factory=list)
    analysis_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now_iso)
    ml: MlResult = field(default_factory=MlResult)


def worst_severity(anomalies: list[Anomaly]) -> str:
    if not anomalies:
        return "none"
    return max(anomalies, key=lambda item: SEVERITY_ORDER[item.severity]).severity


def verdict_from_severity(severity: str) -> str:
    if severity in {"high", "critical"}:
        return "FAIL"
    if severity in {"low", "medium"}:
        return "NEEDS_REVIEW"
    return "PASS"
