import pytest
from wvs.crawler.link_parser import extract_links

def test_extract_links():
    html = """
    <html>
        <body>
            <a href="/about">About</a>
            <a href="https://external.com">External</a>
            <script src="/js/app.js"></script>
            <img src="logo.png" />
            <a href="#section">Fragment</a>
        </body>
    </html>
    """
    
    base_url = "http://example.com/path/"
    
    links = extract_links(html, base_url)
    
    expected = {
        "http://example.com/about",
        "https://external.com",
        "http://example.com/js/app.js",
        "http://example.com/path/logo.png",
        "http://example.com/path/#section"
    }
    
    assert links == expected
