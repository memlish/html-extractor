"""Regression test: deeply nested CSS selectors must be parsed safely.

A caller can send a selector with many nested pseudo-classes. The parser must
handle that depth and return a normal response rather than overflow the call
stack. This test fails on a parser that cannot, and passes once it can.

It is self-contained: it puts the package source on ``sys.path`` itself, so it
works whether run from the repository root or from inside ``tests/``.
"""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from fastapi.testclient import TestClient

from html_extractor.app import app


def test_deeply_nested_selector_is_handled():
    client = TestClient(app)
    depth = 330
    selector = ":is(" * depth + "p" + ")" * depth
    response = client.post(
        "/extract",
        json={"html": "<p>hi</p>", "selector": selector, "attribute": None},
    )
    assert response.status_code == 200
