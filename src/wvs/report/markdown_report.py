from wvs.core.models import ScanResult
from wvs.report.report_builder import summarize


def render_markdown(result: ScanResult) -> str:
    summary = summarize(result.findings)

    lines = []
    lines.append("# Web Vulnerability Scan Report")
    lines.append("")
    lines.append(f"**Target:** `{result.target}`")
    lines.append(f"**Started At:** `{result.started_at}`")
    lines.append(f"**Finished At:** `{result.finished_at}`")
    lines.append(f"**Endpoints Discovered:** `{len(result.endpoints_discovered)}`")
    lines.append(f"**Total Findings:** `{len(result.findings)}`")
    lines.append("")

    lines.append("## Summary")
    lines.append("| Severity | Count |")
    lines.append("|---|---|")
    for sev in ["critical", "high", "medium", "low", "info"]:
        lines.append(f"| {sev.capitalize()} | {summary[sev]} |")
    lines.append("")

    if not result.findings:
        lines.append("## Findings")
        lines.append("No vulnerabilities found.")
        return "\n".join(lines)

    lines.append("## Findings details")

    # Sort findings by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    sorted_findings = sorted(
        result.findings, key=lambda f: severity_order.get(f.severity.lower(), 99)
    )

    for i, finding in enumerate(sorted_findings, 1):
        lines.append(f"### {i}. [{finding.severity.upper()}] {finding.vuln_type}")
        lines.append(f"- **URL:** `{finding.endpoint.url}`")
        if finding.parameter:
            lines.append(f"- **Parameter:** `{finding.parameter}`")
        if finding.payload:
            lines.append(f"- **Payload:** `{finding.payload}`")
        lines.append(f"- **Description:** {finding.description}")
        lines.append(f"- **Evidence:**\n  ```\n  {finding.evidence}\n  ```")
        lines.append(f"- **Remediation:** {finding.remediation}")
        lines.append("")

    return "\n".join(lines)
