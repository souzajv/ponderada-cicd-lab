from __future__ import annotations

from dataclasses import dataclass

from analyzer.models import MlResult, TelemetrySample


@dataclass(frozen=True)
class RiskModel:
    enabled: bool = False
    model_name: str | None = None

    @classmethod
    def disabled(cls) -> RiskModel:
        return cls(enabled=False)

    def evaluate(self, samples: list[TelemetrySample]) -> MlResult:
        if not self.enabled:
            return MlResult()
        return MlResult(
            enabled=True,
            model_name=self.model_name,
            risk_score=None,
            notes="ML hook enabled without pretrained model.",
        )
