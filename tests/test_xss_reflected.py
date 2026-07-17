import pytest
import re
import html
from wvs.core.models import Endpoint
from wvs.core.http_session import WvsSession
from wvs.scanners.xss.reflected import ReflectedXssScanner, generate_marker, is_reflected_unescaped

def test_generate_marker():
    marker1 = generate_marker()
    marker2 = generate_marker()
    assert len(marker1) == 8
    assert marker1 != marker2
    
def test_is_reflected_unescaped():
    payload = "<wvs123>alert(1)</wvs123>"
    assert is_reflected_unescaped(f"Hello {payload}", payload) == True
    assert is_reflected_unescaped(f"Hello {html.escape(payload)}", payload) == False

def test_reflected_xss_scanner(requests_mock):
    session = WvsSession("test", 10, 5)
    endpoint = Endpoint(url="http://example.com/search", method="GET", params={"q": "test"})
    scanner = ReflectedXssScanner()
    
    def dynamic_response(request, context):
        q_param = request.qs.get("q", [""])[0]
        # Simulate vulnerability: reflect it exactly if it has the marker
        if "wvs" in q_param:
            return f"<html><body>You searched for: {q_param}</body></html>"
        return "<html><body>You searched for: test</body></html>"
        
    requests_mock.get(re.compile(".*search.*"), text=dynamic_response)
    
    findings = scanner.scan(endpoint, session)
    
    assert len(findings) == 1
    assert findings[0].vuln_type == "Reflected XSS"
    assert findings[0].parameter == "q"
    assert "wvs" in findings[0].payload
    assert "searched for:" in findings[0].evidence
    
def test_reflected_xss_escaped(requests_mock):
    session = WvsSession("test", 10, 5)
    endpoint = Endpoint(url="http://example.com/search", method="GET", params={"q": "test"})
    scanner = ReflectedXssScanner()
    
    def escaped_response(request, context):
        q_param = request.qs.get("q", [""])[0]
        # Simulate safe application: encode
        escaped_q = html.escape(q_param)
        return f"<html><body>You searched for: {escaped_q}</body></html>"
        
    requests_mock.get(re.compile(".*search.*"), text=escaped_response)
    
    findings = scanner.scan(endpoint, session)
    assert len(findings) == 0
