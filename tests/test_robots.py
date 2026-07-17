import pytest
import urllib.request
from io import BytesIO
from wvs.crawler.robots import is_allowed

def test_robots_allowed(monkeypatch):
    # Mock urllib.request.urlopen used internally by RobotFileParser.read()
    def mock_urlopen(url):
        content = b"User-agent: *\nDisallow: /admin\nAllow: /\n"
        return BytesIO(content)
        
    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)
    
    assert is_allowed("http://example.com/public", "WVS-Bot") == True
    assert is_allowed("http://example.com/admin/login", "WVS-Bot") == False

def test_robots_unreachable(monkeypatch):
    def mock_urlopen_fail(url):
        raise urllib.error.URLError("Connection refused")
        
    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen_fail)
    
    # Should default to True if robots.txt is unreachable
    assert is_allowed("http://example.com/public", "WVS-Bot") == True
