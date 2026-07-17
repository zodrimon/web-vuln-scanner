import time
import requests
import requests_mock
from wvs.core.http_session import WvsSession

def test_session_headers_and_timeout(requests_mock):
    session = WvsSession(user_agent="WVS-Test/1.0", rate_limit_per_second=10, timeout_seconds=5)
    
    requests_mock.get("http://example.com", text="ok")
    
    resp = session.get("http://example.com")
    
    assert resp.status_code == 200
    assert resp.request.headers["User-Agent"] == "WVS-Test/1.0"
    
def test_session_rate_limit(requests_mock):
    # Set limit to 2 per second, so 3 requests should take at least 1 second
    session = WvsSession(user_agent="WVS-Test", rate_limit_per_second=2, timeout_seconds=5)
    
    requests_mock.get("http://example.com", text="ok")
    
    start = time.time()
    session.get("http://example.com")
    session.get("http://example.com")
    session.get("http://example.com")
    elapsed = time.time() - start
    
    # First request is instant, second is delayed 0.5s, third is delayed 0.5s
    # Total delay should be at least ~1.0s
    assert elapsed >= 1.0

def test_session_retry_setup():
    session = WvsSession(user_agent="WVS-Test", rate_limit_per_second=100, timeout_seconds=2)
    # Just verify that the Retry object was correctly mounted for http and https adapters
    adapter = session.session.get_adapter("http://")
    assert adapter.max_retries.total == 3
    assert frozenset(adapter.max_retries.status_forcelist) == frozenset([500, 502, 503, 504])
    assert adapter.max_retries.backoff_factor == 0.1
