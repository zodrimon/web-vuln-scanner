from dataclasses import dataclass, field, asdict
from datetime import datetime

@dataclass
class Endpoint:
    url: str
    method: str
    params: dict[str, str] = field(default_factory=dict)
    source: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class Finding:
    vuln_type: str
    severity: str
    endpoint: Endpoint
    parameter: str | None
    payload: str | None
    evidence: str
    description: str
    remediation: str

    def to_dict(self) -> dict:
        d = asdict(self)
        d["endpoint"] = self.endpoint.to_dict()
        return d

@dataclass
class ScanResult:
    target: str
    started_at: datetime
    finished_at: datetime
    endpoints_discovered: list[Endpoint] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["started_at"] = self.started_at.isoformat() if self.started_at else None
        d["finished_at"] = self.finished_at.isoformat() if self.finished_at else None
        d["endpoints_discovered"] = [e.to_dict() for e in self.endpoints_discovered]
        d["findings"] = [f.to_dict() for f in self.findings]
        return d
