import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from threading import Lock

class WvsSession:
    """Wrapper around requests.Session with rate limiting, timeouts, and retries."""
    
    def __init__(self, user_agent: str, rate_limit_per_second: int, timeout_seconds: int):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self.timeout = timeout_seconds
        
        # Setup retries for 5xx errors and connection issues
        # Note: requests_mock does not fully support urllib3 Retry integration natively
        # so we have to manually simulate retry loop in tests, or we just configure it here
        # and test standard request mocking.
        retries = Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "HEAD", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Token bucket rate limiter
        self.rate_limit = rate_limit_per_second
        self._min_interval = 1.0 / rate_limit_per_second if rate_limit_per_second > 0 else 0
        self._last_request_time = 0.0
        self._lock = Lock()
        
    def _wait_for_rate_limit(self):
        """Thread-safe rate limiting wait."""
        if self._min_interval <= 0:
            return
            
        with self._lock:
            now = time.time()
            elapsed = now - self._last_request_time
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)
            self._last_request_time = time.time()

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Internal method routing all requests through the rate limiter and applying timeout."""
        self._wait_for_rate_limit()
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, url, **kwargs)

    def get(self, url: str, **kwargs) -> requests.Response:
        return self._request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        return self._request("POST", url, **kwargs)
