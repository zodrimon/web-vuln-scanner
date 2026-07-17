def should_report(
    status_code: int,
    response_size: int,
    ignore_codes: set[int],
    baseline_404_size: int | None = None,
) -> bool:
    """
    Determines if a brute-forced path should be reported as a finding.

    Args:
        status_code: The HTTP status code of the response.
        response_size: The length of the response body in bytes.
        ignore_codes: A set of status codes to ignore (typically 404, optionally others like 400, 401, 403, 500).
        baseline_404_size: The measured response size of a known non-existent page to detect soft-404s.

    Returns:
        True if the path appears to exist and is interesting, False otherwise.
    """
    if status_code in ignore_codes:
        return False

    # Check for soft-404s
    # A soft-404 is when the server returns 200 OK for a non-existent page,
    # but the page content is essentially a "Not Found" error page.
    # We compare the size against a known baseline.
    # If the size is within a small margin of error (e.g. +/- 5%), we consider it a soft 404.
    if baseline_404_size is not None and status_code == 200:
        # Calculate a 5% margin
        margin = max(10, int(baseline_404_size * 0.05))
        if abs(response_size - baseline_404_size) <= margin:
            return False

    # Generally, any remaining 2xx, 3xx (if not ignored) are interesting
    return True
