import pytest
import re
from pathlib import Path
from wvs.bruteforce.fuzzer import load_wordlist, build_candidate_urls, DirectoryFuzzer
from wvs.core.http_session import WvsSession

def test_load_wordlist(tmp_path):
    p = tmp_path / "test_wordlist.txt"
    p.write_text("# Comment\nadmin\n\n.env\n")
    
    words = load_wordlist(p)
    assert words == ["admin", ".env"]

def test_build_candidate_urls():
    urls = build_candidate_urls("http://example.com", ["admin", "test/"], ["php"])
    assert urls == [
        "http://example.com/admin",
        "http://example.com/admin.php",
        "http://example.com/test/" # Should not append .php to test/
    ]
    
    urls2 = build_candidate_urls("http://example.com/subdir", ["admin"], ["php"])
    assert urls2 == [
        "http://example.com/subdir/admin",
        "http://example.com/subdir/admin.php"
    ]

def test_fuzzer_soft_404(requests_mock):
    session = WvsSession("test", 10, 5)
    fuzzer = DirectoryFuzzer(session, threads=1)
    
    # Simulate a soft 404 (always returns 200 with "Not found" page of 100 bytes)
    def soft_404_response(request, context):
        if "wvs-bogus" in request.url:
            return "X" * 100 # Baseline size is 100
            
        if "admin.php" in request.url:
            return "Y" * 500 # Real page size is 500
            
        # Other random paths return soft 404
        return "X" * 100
        
    requests_mock.get(re.compile(".*"), text=soft_404_response)
    
    findings = fuzzer.fuzz("http://example.com", ["admin", "backup"], ["php"])
    
    assert len(findings) == 1
    assert "admin.php" in findings[0].endpoint.url
    assert findings[0].severity == "medium"
    
def test_fuzzer_hard_404(requests_mock):
    session = WvsSession("test", 10, 5)
    fuzzer = DirectoryFuzzer(session, threads=1)
    
    requests_mock.get(re.compile(".*"), status_code=404)
    requests_mock.get("http://example.com/.env", text="DB_PASS=123")
    
    findings = fuzzer.fuzz("http://example.com", ["admin", ".env"], [])
    
    assert len(findings) == 1
    assert ".env" in findings[0].endpoint.url
    assert findings[0].severity == "high"
