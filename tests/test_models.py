from datetime import datetime, timezone
from wvs.core.models import Endpoint, Finding, ScanResult

def test_models_to_dict():
    endpoint = Endpoint(
        url="http://example.com/login",
        method="POST",
        params={"username": "test", "password": "test"},
        source="crawl"
    )
    
    finding = Finding(
        vuln_type="SQLi-Error",
        severity="high",
        endpoint=endpoint,
        parameter="username",
        payload="' OR '1'='1",
        evidence="SQL syntax error",
        description="SQL Injection found in username parameter.",
        remediation="Use parameterized queries."
    )
    
    started = datetime(2026, 7, 17, 12, 0, 0, tzinfo=timezone.utc)
    finished = datetime(2026, 7, 17, 12, 5, 0, tzinfo=timezone.utc)
    
    result = ScanResult(
        target="http://example.com",
        started_at=started,
        finished_at=finished,
        endpoints_discovered=[endpoint],
        findings=[finding]
    )
    
    # Test Endpoint
    ep_dict = endpoint.to_dict()
    assert ep_dict["url"] == "http://example.com/login"
    assert ep_dict["method"] == "POST"
    assert ep_dict["params"] == {"username": "test", "password": "test"}
    assert ep_dict["source"] == "crawl"
    
    # Test Finding
    f_dict = finding.to_dict()
    assert f_dict["vuln_type"] == "SQLi-Error"
    assert f_dict["severity"] == "high"
    assert f_dict["parameter"] == "username"
    assert f_dict["payload"] == "' OR '1'='1"
    assert f_dict["evidence"] == "SQL syntax error"
    assert f_dict["endpoint"]["url"] == "http://example.com/login"
    
    # Test ScanResult
    res_dict = result.to_dict()
    assert res_dict["target"] == "http://example.com"
    assert res_dict["started_at"] == "2026-07-17T12:00:00+00:00"
    assert res_dict["finished_at"] == "2026-07-17T12:05:00+00:00"
    assert len(res_dict["endpoints_discovered"]) == 1
    assert res_dict["endpoints_discovered"][0]["url"] == "http://example.com/login"
    assert len(res_dict["findings"]) == 1
    assert res_dict["findings"][0]["vuln_type"] == "SQLi-Error"
