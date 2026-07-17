import os
from jinja2 import Environment, FileSystemLoader
from wvs.core.models import ScanResult
from wvs.report.report_builder import summarize


def render_html(result: ScanResult) -> str:
    # Sort findings by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    sorted_findings = sorted(
        result.findings, key=lambda f: severity_order.get(f.severity.lower(), 99)
    )

    # Create a copy with sorted findings
    result_copy = ScanResult(
        target=result.target,
        started_at=result.started_at,
        finished_at=result.finished_at,
        endpoints_discovered=result.endpoints_discovered,
        findings=sorted_findings,
    )

    summary = summarize(result_copy.findings)

    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("report.html.j2")

    return template.render(result=result_copy, summary=summary)
