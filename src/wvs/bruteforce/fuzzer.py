import uuid
from pathlib import Path
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from wvs.core.models import Endpoint, Finding
from wvs.core.http_session import WvsSession
from wvs.bruteforce.status_filter import should_report
from wvs.core.logger import get_logger

logger = get_logger(__name__)

def load_wordlist(path: Path) -> list[str]:
    """Reads a wordlist file, strips blank lines/comments."""
    words = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                words.append(line)
    return words

def build_candidate_urls(base_url: str, words: list[str], extensions: list[str]) -> list[str]:
    """Cartesian product of words x extensions, joined onto base_url."""
    # Ensure base_url ends with a slash so urljoin treats words as relative to it
    if not base_url.endswith('/'):
        base_url += '/'
        
    urls = []
    # Always include the raw word (without extension) if it has a slash, or just as a directory/file
    for word in words:
        urls.append(urljoin(base_url, word))
        # Don't append extensions to paths that are explicitly directories
        if not word.endswith('/'):
            for ext in extensions:
                urls.append(urljoin(base_url, f"{word}.{ext}"))
                
    # Remove duplicates while preserving order (in Python 3.7+ dict maintains order)
    return list(dict.fromkeys(urls))

class DirectoryFuzzer:
    def __init__(self, session: WvsSession, ignore_codes: set[int] = frozenset({404}), threads: int = 10):
        self.session = session
        self.ignore_codes = ignore_codes
        self.threads = threads
        self.baseline_404_size: int | None = None
        
    def _measure_baseline_404(self, base_url: str) -> None:
        """Measures the response size of a guaranteed non-existent URL for soft-404 detection."""
        bogus_path = f"wvs-bogus-{uuid.uuid4().hex}.txt"
        test_url = urljoin(base_url if base_url.endswith('/') else base_url + '/', bogus_path)
        
        try:
            resp = self.session.get(test_url)
            if resp.status_code == 200:
                self.baseline_404_size = len(resp.content)
                logger.debug(f"Measured soft-404 baseline size: {self.baseline_404_size} bytes")
        except Exception as e:
            logger.debug(f"Failed to measure baseline 404: {e}")

    def get_path_severity(self, path: str) -> str:
        path_lower = path.lower()
        if '.git' in path_lower or '.env' in path_lower or '.sql' in path_lower:
            return "high"
        if 'admin' in path_lower or 'config' in path_lower or 'db' in path_lower:
            return "medium"
        return "info"

    def fuzz(self, base_url: str, words: list[str], extensions: list[str]) -> list[Finding]:
        self._measure_baseline_404(base_url)
        candidate_urls = build_candidate_urls(base_url, words, extensions)
        
        findings = []
        
        def check_url(url: str) -> Finding | None:
            try:
                resp = self.session.get(url)
                if should_report(resp.status_code, len(resp.content), self.ignore_codes, self.baseline_404_size):
                    severity = self.get_path_severity(url)
                    return Finding(
                        vuln_type="Exposed-Path",
                        severity=severity,
                        endpoint=Endpoint(url=url, method="GET", source="bruteforce"),
                        parameter=None,
                        payload=None,
                        evidence=f"Status: {resp.status_code}, Size: {len(resp.content)} bytes",
                        description=f"Found exposed path: {url}",
                        remediation="Ensure sensitive files/directories are not publicly accessible."
                    )
            except Exception:
                pass
            return None

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            future_to_url = {executor.submit(check_url, url): url for url in candidate_urls}
            for future in as_completed(future_to_url):
                result = future.result()
                if result:
                    findings.append(result)
                    
        return findings
