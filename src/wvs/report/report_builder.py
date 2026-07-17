from datetime import datetime
from wvs.core.models import Endpoint, Finding, ScanResult

def build_report(target: str, started_at: datetime, finished_at: datetime, endpoints: list[Endpoint], findings: list[Finding]) -> ScanResult:
    return ScanResult(
        target=target,
        started_at=started_at,
        finished_at=finished_at,
        endpoints_discovered=endpoints,
        findings=findings
    )

def summarize(findings: list[Finding]) -> dict[str, int]:
    """Counts findings by severity."""
    summary = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for finding in findings:
        sev = finding.severity.lower()
        if sev in summary:
            summary[sev] += 1
        else:
            summary["info"] += 1
    return summary
