"""Runtime configuration, read from environment variables.

Every setting has a development-friendly default so the service runs out of
the box, while deployments can override values through the environment.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

# Default ceiling on the length of an incoming selector string. Kept generous
# so ordinary selectors are never rejected; deployments may tune it per tenant.
DEFAULT_MAX_SELECTOR_LENGTH = 8192

# Default ceiling on the size of an incoming HTML document, in bytes.
DEFAULT_MAX_DOCUMENT_BYTES = 2_000_000


@dataclass(frozen=True)
class Settings:
    """Immutable view of the service configuration."""

    service_name: str
    version: str
    max_selector_length: int
    max_document_bytes: int


def _int_env(name: str, default: int) -> int:
    """Read an integer environment variable, falling back to ``default``."""
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@lru_cache
def get_settings() -> Settings:
    """Build (and cache) the settings from the current environment."""
    return Settings(
        service_name=os.getenv("HTML_EXTRACTOR_SERVICE_NAME", "html-extractor"),
        version=os.getenv("HTML_EXTRACTOR_VERSION", "1.0.0"),
        max_selector_length=_int_env(
            "HTML_EXTRACTOR_MAX_SELECTOR_LENGTH", DEFAULT_MAX_SELECTOR_LENGTH
        ),
        max_document_bytes=_int_env(
            "HTML_EXTRACTOR_MAX_DOCUMENT_BYTES", DEFAULT_MAX_DOCUMENT_BYTES
        ),
    )
