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
        """BFS crawler using link and form parsers."""
        endpoints = []
        queue = [(start_url, 0)]  # (url, depth)
        
        # Add the starting URL as an endpoint itself, assuming it's a GET
        endpoints.append(Endpoint(
            url=start_url,
            method="GET",
            params={},
            source="crawl"
        ))
        
        self._mark_visited(start_url)
        
        user_agent = self.session.session.headers.get("User-Agent", "WVS-Bot")

        with ThreadPoolExecutor(max_workers=self.session.rate_limit or 10) as executor:
            while queue:
                current_batch = queue[:]
                queue.clear()
                
                # Fetch all in current batch concurrently
                futures = []
                for url, depth in current_batch:
                    if depth >= self.max_depth:
                        continue
                        
                    if self.respect_robots_txt and not is_allowed(url, user_agent):
                        continue
                        
                    futures.append((executor.submit(self.session.get, url), url, depth))
                
                # Process results and extract new links/forms
                for future, url, depth in futures:
                    try:
                        resp = future.result()
                        if resp.status_code != 200:
                            continue
                            
                        # Extract forms
                        forms = extract_forms(resp.text, resp.url)
                        for form_endpoint in forms:
                            if self._is_in_scope(start_url, form_endpoint.url):
                                endpoints.append(form_endpoint)
                                
                        # Extract links
                        links = extract_links(resp.text, resp.url)
                        for link in links:
                            if self._is_in_scope(start_url, link):
                                if self._mark_visited(link):
                                    # Parse query params
                                    parsed_link = urllib.parse.urlparse(link)
                                    query_params = {}
                                    if parsed_link.query:
                                        query_params = dict(urllib.parse.parse_qsl(parsed_link.query))
                                        
                                    base_url = urllib.parse.urlunparse((parsed_link.scheme, parsed_link.netloc, parsed_link.path, parsed_link.params, '', ''))
                                    endpoints.append(Endpoint(
                                        url=base_url,
                                        method="GET",
                                        params=query_params,
                                        source="crawl"
                                    ))
                                    queue.append((link, depth + 1))
                                    
                    except Exception as e:
                        # Log or ignore fetch errors during crawling
                        pass
                        
        return endpoints
