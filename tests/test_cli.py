import pytest
import os
import re
from unittest.mock import patch
from wvs.cli import main
from wvs.core.logger import set_log_file

def test_e2e_scan(requests_mock, tmp_path):
    report_path = tmp_path / "report.html"
    wordlist_path = tmp_path / "wordlist.txt"
    wordlist_path.write_text("admin\nhidden")
    
    # Mock crawler responses
    # Homepage with a form (reflected XSS) and a link to search (SQLi)
    homepage_html = """
    <html>
        <body>
                <a href="/search?q=test">Search</a>
            <form action="/login" method="POST">
                <input name="user">
            </form>
        </body>
    </html>
    """
    requests_mock.get("http://test.local/", text=homepage_html)
    
    # Search page with error-based SQLi
    def search_handler(request, context):
        q = request.qs.get("q", [""])[0]
        if "'" in q or "SQL" in q:
            return "Warning: mysql_fetch_array() expects parameter 1"
        return "Search results for: " + q
        
    requests_mock.get(re.compile(".*search.*"), text=search_handler)
    
    # Login page with reflected XSS
    def login_handler(request, context):
        user = ""
        if request.text and "user=" in request.text:
            user = request.text.split("user=")[1]
        if "wvs" in user:
            return f"<html>{user}</html>" # reflected unescaped
        return "Login failed"
        
    requests_mock.post("http://test.local/login", text=login_handler)
    
    # Brute-force directory simulation
    def dir_handler(request, context):
        if "/admin.php" in request.url:
            return "Admin panel"
        context.status_code = 404
        return "Not found"
        
    requests_mock.get("http://test.local/admin", status_code=404)
    requests_mock.get("http://test.local/admin.php", text=dir_handler)
    requests_mock.get("http://test.local/admin.html", status_code=404)
    requests_mock.get("http://test.local/hidden", status_code=404)
    requests_mock.get("http://test.local/hidden.php", status_code=404)
    requests_mock.get("http://test.local/hidden.html", status_code=404)
    
    # Run the CLI
    test_args = [
        "wvs",
        "scan",
        "http://test.local/",
        "--i-have-authorization",
        "--wordlist", str(wordlist_path),
        "--output", str(report_path),
        "--format", "html"
    ]
    
    with patch("sys.argv", test_args):
        ret = main()
        assert ret == 0
        
    print(report_path.read_text(encoding="utf-8"))
        
    assert report_path.exists()
    report_html = report_path.read_text(encoding="utf-8")
    
    assert "SQL Injection (Error Based)" in report_html
    assert "Reflected XSS" in report_html
    assert "Exposed-Path" in report_html
    assert "Total Vulnerabilities" not in report_html # not in HTML, it's just rendered in console. But the types are.
    assert "http://test.local/admin.php" in report_html
