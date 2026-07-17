from urllib.parse import urljoin
from bs4 import BeautifulSoup


def extract_links(html: str, base_url: str) -> set[str]:
    """Extract and resolve links from a href, script src, and img src."""
    links = set()
    soup = BeautifulSoup(html, "lxml")

    for a_tag in soup.find_all("a", href=True):
        links.add(urljoin(base_url, a_tag["href"]))

    for script_tag in soup.find_all("script", src=True):
        links.add(urljoin(base_url, script_tag["src"]))

    for img_tag in soup.find_all("img", src=True):
        links.add(urljoin(base_url, img_tag["src"]))

    return links
