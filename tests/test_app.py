"""End-to-end tests for the html-extractor API via FastAPI's TestClient."""

from fastapi.testclient import TestClient

from html_extractor.app import app

client = TestClient(app)

SAMPLE = """
<html>
  <body>
    <h1 class="title">Release notes</h1>
    <ul id="items">
      <li class="item" data-id="1">First</li>
      <li class="item" data-id="2">Second</li>
    </ul>
    <a href="https://example.test/docs">Docs</a>
  </body>
</html>
"""


def test_health_reports_ok():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "html-extractor"


def test_extract_returns_text_of_matches():
    response = client.post(
        "/extract", json={"html": SAMPLE, "selector": "li.item", "attribute": None}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 2
    assert [m["text"] for m in body["matches"]] == ["First", "Second"]


def test_extract_returns_requested_attribute():
    response = client.post(
        "/extract", json={"html": SAMPLE, "selector": "li.item", "attribute": "data-id"}
    )
    assert response.status_code == 200
    body = response.json()
    assert [m["attribute"] for m in body["matches"]] == ["1", "2"]


def test_extract_with_no_matches_returns_empty():
    response = client.post(
        "/extract", json={"html": SAMPLE, "selector": "p.missing", "attribute": None}
    )
    assert response.status_code == 200
    assert response.json() == {"count": 0, "matches": []}


def test_extract_with_descendant_selector():
    response = client.post(
        "/extract", json={"html": SAMPLE, "selector": "ul#items li", "attribute": None}
    )
    assert response.status_code == 200
    assert response.json()["count"] == 2


def test_extract_rejects_bad_selector():
    response = client.post(
        "/extract", json={"html": SAMPLE, "selector": "li[", "attribute": None}
    )
    assert response.status_code == 400


def test_extract_rejects_overlong_selector():
    long_selector = "a" * 9000
    response = client.post(
        "/extract", json={"html": SAMPLE, "selector": long_selector, "attribute": None}
    )
    assert response.status_code == 413


def test_text_endpoint_flattens_document():
    response = client.post("/text", json={"html": "<p>Hello <b>world</b></p>"})
    assert response.status_code == 200
    assert response.json()["text"] == "Hello world"
