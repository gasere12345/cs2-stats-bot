import re

_FACEIT_PATTERN = re.compile(
    r"^https?://(?:www\.)?faceit\.com(?:/[^/]+)?/cs2/room/([a-zA-Z0-9_-]+)"
)


def parse_faceit_url(url: str) -> str | None:
    if not url:
        return None
    stripped = url.strip().rstrip("/")
    if "faceit.com" in stripped:
        m = _FACEIT_PATTERN.match(stripped)
        if m:
            return m.group(1)
        return None
    if re.match(r"^[a-zA-Z0-9_-]+$", stripped):
        return stripped
    return None
