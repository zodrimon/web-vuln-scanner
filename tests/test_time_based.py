import pytest
import time
import re
from wvs.core.models import Endpoint
from wvs.core.http_session import WvsSession
from wvs.scanners.sqli.time_based import TimeBasedSqliScanner, measure_baseline_latency

def test_measure_baseline(requests_mock):
    session = WvsSession("test", 10, 5)
    endpoint = Endpoint(url="http://example.com/", method="GET")
    
    def slow_response(request, context):
        time.sleep(0.1)
        return "ok"
        
    requests_mock.get("http://example.com/", text=slow_response)
    
    baseline = measure_baseline_latency(session, endpoint)
    assert baseline is not None
    assert 0.1 <= baseline < 0.5 # Basic sanity check, should take ~0.1s twice (each)

def test_time_based_sqli(requests_mock):
    session = WvsSession("test", 10, 5)
    endpoint = Endpoint(url="http://example.com/search", method="GET", params={"q": "test"})
    scanner = TimeBasedSqliScanner(delay=1) # 1 second delay for faster test
    
    def dynamic_response(request, context):
        # If payload contains SLEEP(1) (URL-encoded or not)
        if "SLEEP%281%29" in request.url or "SLEEP(1)" in request.url:
            time.sleep(1.0)
        else:
            time.sleep(0.01) # Baseline
        return "result"
        
    requests_mock.get(re.compile(".*search.*"), text=dynamic_response)
    
    findings = scanner.scan(endpoint, session)
    
    assert len(findings) == 1
    assert findings[0].vuln_type == "SQL Injection (Time Based)"
    assert findings[0].parameter == "q"
    assert "SLEEP(1)" in findings[0].payload
    assert "mysql" in findings[0].description.lower()
    
def test_time_based_sqli_false_positive(requests_mock):
    session = WvsSession("test", 10, 5)
    endpoint = Endpoint(url="http://example.com/search", method="GET", params={"q": "test"})
    scanner = TimeBasedSqliScanner(delay=1)
    
    call_count = [0]
    
    def jitter_response(request, context):
        call_count[0] += 1
        # Simulating jitter: only ONE request is slow, the confirmation request is fast
        if ("SLEEP%281%29" in request.url or "SLEEP(1)" in request.url) and call_count[0] == 3: # 2 baseline + 1st payload
            time.sleep(1.0)
        else:
            time.sleep(0.01)
        return "result"
        
    requests_mock.get(re.compile(".*search.*"), text=jitter_response)
    
    findings = scanner.scan(endpoint, session)
    
    # Should not report finding because the second request was fast
    assert len(findings) == 0
