"""Utilities for URL normalization and manipulation."""

from urllib.parse import urlparse, urlunparse


def normalize_url(url: str) -> str:
    """
    Normalize a URL by removing trailing slashes and ensuring consistent formatting.

    This is used for URL comparisons, especially when matching URLs from different sources
    (e.g., configuration files, API responses) that may have inconsistent trailing slashes.

    Args:
        url: The URL to normalize

    Returns:
        str: The normalized URL without trailing slashes

    Example:
        >>> normalize_url("http://localhost:8080/bfabric/")
        'http://localhost:8080/bfabric'
        >>> normalize_url("http://localhost:8080/bfabric")
        'http://localhost:8080/bfabric'
    """
    if not url:
        return url

    # Parse the URL into components
    parsed = urlparse(url)

    # Remove trailing slashes from the path
    normalized_path = parsed.path.rstrip('/')

    # Reconstruct the URL with normalized path
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc,
        normalized_path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))

    return normalized