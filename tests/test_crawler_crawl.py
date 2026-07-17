import pytest
from wvs.crawler.crawler import Crawler
from wvs.core.http_session import WvsSession

def test_crawler_crawl(requests_mock):
    session = WvsSession("test", 10, 5)
    crawler = Crawler(session, max_depth=2, respect_robots_txt=False)
    
    start_url = "http://example.com/"
    
    html_1 = """
    <html>
        <body>
            <a href="/page1">Page 1</a>
            <a href="/page2">Page 2</a>
        </body>
    </html>
    """
    
    html_2 = """
    <html>
        <body>
            <form action="/submit" method="POST">
                <input type="text" name="data" />
            </form>
            <a href="/page3">Page 3 (Depth 2)</a>
        </body>
    </html>
    """
    
    html_3 = "<html><body></body></html>"
    
    requests_mock.get("http://example.com/", text=html_1)
    requests_mock.get("http://example.com/page1", text=html_2)
    requests_mock.get("http://example.com/page2", text=html_3)
    
    # Page 3 won't be fetched if max_depth is 2 and we only go from 0 -> 1
    # Actually, depth 0 is root, depth 1 is page1/2, depth 2 is page3 (if fetched).
    # Since depth check is `depth >= self.max_depth` (2 >= 2 is True, so skips fetching).
    requests_mock.get("http://example.com/page3", text="should not fetch")
    
    endpoints = crawler.crawl(start_url)
    
    # Endpoints should include:
    # 1. root (GET)
    # 2. page1 (GET)
    # 3. page2 (GET)
    # 4. /submit (POST from page1)
    # 5. page3 (GET from page1 - it's added to endpoints list even if not fetched yet)
    
    urls = [e.url for e in endpoints]
    assert "http://example.com/" in urls
    assert "http://example.com/page1" in urls
    assert "http://example.com/page2" in urls
    assert "http://example.com/submit" in urls
    assert "http://example.com/page3" in urls
    
    submit_ep = next(e for e in endpoints if e.url == "http://example.com/submit")
    assert submit_ep.method == "POST"
    assert submit_ep.params == {"data": ""}
    
    # Assert page3 was NOT fetched
    assert not any(r.url == "http://example.com/page3" for r in requests_mock.request_history)
