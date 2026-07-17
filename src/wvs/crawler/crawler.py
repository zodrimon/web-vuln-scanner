import threading
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from wvs.core.http_session import WvsSession
from wvs.core.models import Endpoint
from wvs.crawler.link_parser import extract_links
from wvs.crawler.form_parser import extract_forms
from wvs.crawler.robots import is_allowed

class Crawler:
    def __init__(self, session: WvsSession, max_depth: int = 3, same_origin_only: bool = True, respect_robots_txt: bool = True):
        self.session = session
        self.max_depth = max_depth
        self.same_origin_only = same_origin_only
        self.respect_robots_txt = respect_robots_txt
        
        self._visited: set[str] = set()
        self._lock = threading.Lock()
        
    def _is_in_scope(self, start_url: str, target_url: str) -> bool:
        """Check if target_url is in scope based on start_url."""
        if not self.same_origin_only:
            return True
            
        start_parsed = urllib.parse.urlparse(start_url)
        target_parsed = urllib.parse.urlparse(target_url)
        
        return (start_parsed.scheme == target_parsed.scheme and
                start_parsed.netloc == target_parsed.netloc)
                
    def _mark_visited(self, url: str) -> bool:
        """Returns True if this is the first time visiting this URL."""
        # Normalize URL to remove fragments for deduplication
        parsed = urllib.parse.urlparse(url)
        normalized = urllib.parse.urlunparse(
            (parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, "")
        )
        with self._lock:
            if normalized in self._visited:
                return False
            self._visited.add(normalized)
            return True

    def crawl(self, start_url: str) -> list[Endpoint]:
        pass # To be implemented in part C
