import pytest
import re
from wvs.core.models import Endpoint
from wvs.core.http_session import WvsSession
from wvs.scanners.sqli.error_based import check_error_based

def test_check_error_based_get(requests_mock):
    session = WvsSession("test", 10, 5)
    endpoint = Endpoint(url="http://example.com/search", method="GET", params={"q": "test"}, source="crawl")
    
    def custom_matcher(request):
        return "test'" in request.url or "test%27" in request.url
        
    requests_mock.get(re.compile(".*search.*"), text="normal page")
    requests_mock.get(re.compile(".*search.*"), text="Warning: mysql_fetch_array() expects parameter 1", additional_matcher=custom_matcher)
    
    findings = check_error_based(endpoint, session)
    
    assert len(findings) == 1
    assert findings[0].vuln_type == "SQL Injection (Error Based)"
    assert findings[0].parameter == "q"
    assert findings[0].payload == "'"
    assert findings[0].severity == "high"
    assert "mysql_fetch" in findings[0].evidence.lower()

def test_check_error_based_post(requests_mock):
    session = WvsSession("test", 10, 5)
    endpoint = Endpoint(url="http://example.com/login", method="POST", params={"user": "admin"}, source="crawl")
    
    def post_matcher(request):
        return request.text and ("admin'" in request.text or "admin%27" in request.text)
        
    requests_mock.post(re.compile(".*login.*"), text="normal login failed")
    requests_mock.post(re.compile(".*login.*"), text="SQL syntax error near ...", additional_matcher=post_matcher)
    
    findings = check_error_based(endpoint, session)
    
    assert len(findings) == 1
    assert findings[0].parameter == "user"
    assert "sql syntax" in findings[0].evidence.lower()
