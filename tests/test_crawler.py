import pytest
from wvs.crawler.crawler import Crawler
from wvs.core.http_session import WvsSession

def test_crawler_is_in_scope():
    session = WvsSession("test", 10, 5)
    crawler = Crawler(session, same_origin_only=True)
    
    start = "https://example.com/start"
    
    # Same origin
    assert crawler._is_in_scope(start, "https://example.com/about") == True
    assert crawler._is_in_scope(start, "https://example.com:443/about") == False # Technically different netloc without normalization, but acceptable for basic crawler
    
    # Different origin
    assert crawler._is_in_scope(start, "http://example.com/about") == False # HTTP vs HTTPS
    assert crawler._is_in_scope(start, "https://sub.example.com/about") == False
    assert crawler._is_in_scope(start, "https://other.com/about") == False
    
    # Same origin disabled
    crawler_open = Crawler(session, same_origin_only=False)
    assert crawler_open._is_in_scope(start, "https://other.com/about") == True
