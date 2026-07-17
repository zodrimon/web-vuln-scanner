import pytest
import re
from wvs.core.models import Endpoint
from wvs.core.http_session import WvsSession
from wvs.scanners.sqli.error_based import ErrorBasedSqliScanner, detect_error_signature

def test_detect_error_signature():
    assert detect_error_signature("Something went wrong with mysql_fetch_assoc()") == "MySQL"
    assert detect_error_signature("SQL syntax error") == "MySQL"
    assert detect_error_signature("postgresql query failed: ERROR:") == "PostgreSQL"
    assert detect_error_signature("ORA-12154: TNS:could not resolve") == "Oracle"
    assert detect_error_signature("SQLite3::SQLException: no such table") == "SQLite"
    assert detect_error_signature("Just a regular 500 internal server error") is None

def test_check_error_based_get(requests_mock):
    session = WvsSession("test", 10, 5)
    endpoint = Endpoint(url="http://example.com/search", method="GET", params={"q": "test"}, source="crawl")
    scanner = ErrorBasedSqliScanner()
    
    def custom_matcher(request):
        return "test'" in request.url or "test%27" in request.url
        
    requests_mock.get(re.compile(".*search.*"), text="normal page")
    requests_mock.get(re.compile(".*search.*"), text="Warning: mysql_fetch_array() expects parameter 1", additional_matcher=custom_matcher)
    
    findings = scanner.scan(endpoint, session)
    
    assert len(findings) == 1
    assert findings[0].vuln_type == "SQL Injection (Error Based)"
    assert findings[0].parameter == "q"
    assert findings[0].payload == "'"
    assert findings[0].severity == "high"
    assert "MySQL" in findings[0].evidence

def test_check_error_based_post(requests_mock):
    session = WvsSession("test", 10, 5)
    endpoint = Endpoint(url="http://example.com/login", method="POST", params={"user": "admin"}, source="crawl")
    scanner = ErrorBasedSqliScanner()
    
    def post_matcher(request):
        return request.text and ("admin'" in request.text or "admin%27" in request.text)
        
    requests_mock.post(re.compile(".*login.*"), text="normal login failed")
    requests_mock.post(re.compile(".*login.*"), text="SQL syntax error near ...", additional_matcher=post_matcher)
    
    findings = scanner.scan(endpoint, session)
    
    assert len(findings) == 1
    assert findings[0].parameter == "user"
    assert "MySQL" in findings[0].evidence
