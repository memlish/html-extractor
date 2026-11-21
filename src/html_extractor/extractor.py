"""HTML parsing helpers built on Beautiful Soup.

The HTTP layer stays thin: it validates the request and formats the response,
while the actual document work lives here. Keeping the Beautiful Soup calls in
one module makes the parsing behaviour easy to test in isolation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from bs4 import BeautifulSoup

# Beautiful Soup's pure-Python parser. It ships with the standard library, so
# the service has no system-level parser dependency to install.
_PARSER = "html.parser"


@dataclass
class Match:
    """A single matched element, reduced to the fields callers care about."""

    text: str
    attribute: Optional[str]


def _document(html: str) -> BeautifulSoup:
    """Parse an HTML string into a Beautiful Soup document."""
    return BeautifulSoup(html, _PARSER)


def select_matches(
    html: str, selector: str, attribute: Optional[str] = None
) -> List[Match]:
    """Return one :class:`Match` per element that matches ``selector``.

    When ``attribute`` is given, each match also carries that attribute's value
    (``None`` if the element does not set it); otherwise only the element's
    collapsed text is returned.
    """
    soup = _document(html)
    elements = soup.select(selector)

    matches: List[Match] = []
    for element in elements:
        text = element.get_text(strip=True)
        if attribute is None:
            matches.append(Match(text=text, attribute=None))
        else:
            value = element.get(attribute)
            matches.append(Match(text=text, attribute=_as_str(value)))
    return matches


def all_text(html: str) -> str:
    """Return the visible text of a document, collapsed to a single string."""
    soup = _document(html)
    return soup.get_text(separator=" ", strip=True)


def _as_str(value: object) -> Optional[str]:
    """Normalise an attribute value to a string.

    Beautiful Soup returns multi-valued attributes (such as ``class``) as a
    list; join those with spaces so callers always receive a plain string.
    """
    if value is None:
        return None
    if isinstance(value, list):
        return " ".join(str(part) for part in value)
    return str(value)
