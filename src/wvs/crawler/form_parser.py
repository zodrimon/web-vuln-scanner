from urllib.parse import urljoin
from bs4 import BeautifulSoup
from wvs.core.models import Endpoint


def extract_forms(html: str, base_url: str) -> list[Endpoint]:
    """Extract forms, their method, action, and input parameters."""
    endpoints = []
    soup = BeautifulSoup(html, "lxml")

    for form in soup.find_all("form"):
        method = form.get("method", "GET").upper()
        if method not in ["GET", "POST"]:
            method = "GET"

        action = form.get("action", "")
        url = urljoin(base_url, action)

        params = {}
        # Find input, select, and textarea fields
        for field in form.find_all(["input", "select", "textarea"]):
            name = field.get("name")
            if not name:
                continue

            value = field.get("value", "")
            # If multiple inputs share a name (like radio buttons), keep the first seen value
            # or empty if none. This is simplified for the scanner's purpose.
            if name not in params:
                params[name] = value

        endpoints.append(
            Endpoint(url=url, method=method, params=params, source="crawl")
        )

    return endpoints
