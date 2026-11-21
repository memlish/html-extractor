"""HTML Extractor service.

A small internal API that pulls pieces of text out of HTML. A caller sends an
HTML document together with a CSS selector and gets back the text (or a named
attribute) of each matching element. A companion endpoint flattens a whole
document to its visible text.
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from soupsieve import SelectorSyntaxError

from .config import Settings, get_settings
from .extractor import all_text, select_matches

settings: Settings = get_settings()

app = FastAPI(
    title=settings.service_name,
    version=settings.version,
    description="Pull text and attributes out of HTML with CSS selectors.",
)


class ExtractRequest(BaseModel):
    """Body for a selector-based extraction."""

    html: str = Field(..., description="The HTML document to read.")
    selector: str = Field(..., description="A CSS selector to match elements against.")
    attribute: Optional[str] = Field(
        default=None,
        description="When set, return this attribute of each match instead of its text.",
    )


class MatchModel(BaseModel):
    """One matched element in the response."""

    text: str = Field(..., description="The element's collapsed text content.")
    attribute: Optional[str] = Field(
        default=None, description="The requested attribute's value, if one was asked for."
    )


class ExtractResponse(BaseModel):
    """The matches found for a selector."""

    count: int
    matches: List[MatchModel]


class TextRequest(BaseModel):
    """Body for a whole-document text dump."""

    html: str = Field(..., description="The HTML document to flatten.")


class TextResponse(BaseModel):
    """The visible text of a document."""

    text: str


class HealthResponse(BaseModel):
    """Service liveness details."""

    status: str
    service: str
    version: str


def _guard_document(html: str) -> None:
    """Reject documents that exceed the configured byte ceiling."""
    if len(html.encode("utf-8")) > settings.max_document_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Document exceeds {settings.max_document_bytes} bytes.",
        )


def _guard_selector(selector: str) -> None:
    """Reject selectors longer than the configured ceiling."""
    if len(selector) > settings.max_selector_length:
        raise HTTPException(
            status_code=413,
            detail=f"Selector exceeds {settings.max_selector_length} characters.",
        )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness probe used by the platform's health checks."""
    return HealthResponse(
        status="ok", service=settings.service_name, version=settings.version
    )


@app.post("/extract", response_model=ExtractResponse)
def extract(request: ExtractRequest) -> ExtractResponse:
    """Return the text (or an attribute) of each element matching the selector."""
    _guard_document(request.html)
    _guard_selector(request.selector)
    try:
        matches = select_matches(request.html, request.selector, request.attribute)
    except SelectorSyntaxError as exc:
        # A caller typo in the selector is a client error, not a server fault.
        raise HTTPException(status_code=400, detail=f"Invalid selector: {exc}") from exc
    return ExtractResponse(
        count=len(matches),
        matches=[MatchModel(text=m.text, attribute=m.attribute) for m in matches],
    )


@app.post("/text", response_model=TextResponse)
def text(request: TextRequest) -> TextResponse:
    """Return all visible text of a document as one whitespace-collapsed string."""
    _guard_document(request.html)
    return TextResponse(text=all_text(request.html))
