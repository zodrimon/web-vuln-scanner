import pytest
from datetime import datetime
from wvs.core.models import Endpoint, Finding, ScanResult
from wvs.report.report_builder import build_report, summarize
from wvs.report.markdown_report import render_markdown
from wvs.report.html_report import render_html

def test_report_builder():
    endpoints = [Endpoint("http://test.com", "GET")]
    findings = [
        Finding("XSS", "medium", endpoints[0], "q", "<script>", "alert", "XSS found", "Fix it"),
        Finding("SQLi", "high", endpoints[0], "id", "'", "error", "SQLi found", "Fix it")
    ]
    
    res = build_report("http://test.com", datetime(2023, 1, 1), datetime(2023, 1, 1), endpoints, findings)
    assert res.target == "http://test.com"
    assert len(res.findings) == 2

def test_summarize():
    findings = [
        Finding("XSS", "medium", Endpoint("http://test.com", "GET"), None, None, "", "", ""),
        Finding("SQLi", "high", Endpoint("http://test.com", "GET"), None, None, "", "", ""),
        Finding("Test", "unknown", Endpoint("http://test.com", "GET"), None, None, "", "", "") # Unknown should go to info
    ]
    
    summary = summarize(findings)
    assert summary["high"] == 1
    assert summary["medium"] == 1
    assert summary["critical"] == 0
    assert summary["info"] == 1

def test_render_markdown():
    res = ScanResult(
        target="http://test.com",
        started_at=datetime(2023, 1, 1),
        finished_at=datetime(2023, 1, 1),
        endpoints_discovered=[],
        findings=[
            Finding("XSS", "medium", Endpoint("http://test.com", "GET"), "q", "<script>", "ev", "desc", "rem")
        ]
    )
    
    md = render_markdown(res)
    assert "# Web Vulnerability Scan Report" in md
    assert "**Target:** `http://test.com`" in md
    assert "[MEDIUM] XSS" in md
    assert "desc" in md

def test_render_html():
    res = ScanResult(
        target="http://test.com",
        started_at=datetime(2023, 1, 1),
        finished_at=datetime(2023, 1, 1),
        endpoints_discovered=[],
        findings=[
            Finding("XSS", "medium", Endpoint("http://test.com", "GET"), "q", "<script>", "ev", "desc", "rem")
        ]
    )
    
    html = render_html(res)
    assert "<title>WVS Report: http://test.com</title>" in html
    assert "Medium<br>1" in html
    assert "XSS" in html
    assert "desc" in html
