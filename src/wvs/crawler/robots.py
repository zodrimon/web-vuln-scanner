from urllib.robotparser import RobotFileParser
from urllib.error import URLError

def is_allowed(url: str, user_agent: str) -> bool:
    """Check if the URL is allowed to be crawled according to robots.txt."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        rp = RobotFileParser()
        rp.set_url(robots_url)
        # In a real tool this might make an HTTP request which could block
        # or timeout, but urllib's read() handles basic fetching.
        # WVS might prefer to use the WvsSession for this in the crawler itself,
        # but this simple wrapper handles the parsing logic.
        rp.read()
        
        return rp.can_fetch(user_agent, url)
    except (URLError, ValueError, Exception):
        # Gracefully allow if robots.txt is missing, unreachable, or unparseable
        return True
