"""CheckResult 数据模型。"""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class CheckResult:
    rule_id: str
    verdict: str
    location: str
    evidence: str
    reason: str
    severity: str
    confidence: float = 1.0
    def to_dict(self) -> dict:
        return {"rule_id": self.rule_id, "verdict": self.verdict,
                "severity": self.severity, "confidence": self.confidence,
                "location": self.location, "evidence": self.evidence,
                "reason": self.reason}
