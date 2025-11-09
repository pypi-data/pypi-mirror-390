from urllib.parse import urljoin, urlparse, urlunparse


def canonicalize_url(href: str, base_url: str) -> str | None:
    """
    Convert a possibly relative URL into an absolute canonical form.
    Removes URL fragments. Returns None if invalid.
    """
    try:
        # Join with base (relative → absolute)
        absolute = urljoin(base_url, href)

        # Parse and remove fragment (#...)
        parsed = urlparse(absolute)
        cleaned = parsed._replace(fragment="")

        return urlunparse(cleaned)
    except Exception:
        return None
