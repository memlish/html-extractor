# html-extractor

A small internal API that pulls pieces of text out of HTML. A caller submits an
HTML document together with a CSS selector and gets back the text, or a named
attribute, of each matching element.

## Why

Several services need "give me the text of the elements matching this selector"
without each of them pulling in a parser and re-implementing the glue. This
service centralises that behind a tiny HTTP interface.

## Endpoints

### `GET /health`

Liveness probe. Returns the service name, version and `status: ok`.

### `POST /extract`

Request body:

```json
{
  "html": "<ul><li class=\"item\">First</li><li class=\"item\">Second</li></ul>",
  "selector": "li.item",
  "attribute": null
}
```

Response:

```json
{
  "count": 2,
  "matches": [
    {"text": "First", "attribute": null},
    {"text": "Second", "attribute": null}
  ]
}
```

Set `attribute` to a name (for example `"href"` or `"data-id"`) to return that
attribute of each match instead of its text. A selector the parser cannot
understand yields `400`; an oversized selector or document yields `413`.

### `POST /text`

Returns all visible text of a document as a single whitespace-collapsed string:

```json
{"html": "<p>Hello <b>world</b></p>"}
```

→ `{"text": "Hello world"}`

## Configuration

All settings come from the environment with development defaults:

| Variable | Default | Meaning |
|---|---|---|
| `HTML_EXTRACTOR_SERVICE_NAME` | `html-extractor` | Name reported by `/health`. |
| `HTML_EXTRACTOR_VERSION` | `1.0.0` | Version reported by `/health`. |
| `HTML_EXTRACTOR_MAX_SELECTOR_LENGTH` | `8192` | Longest accepted selector, in characters. |
| `HTML_EXTRACTOR_MAX_DOCUMENT_BYTES` | `2000000` | Largest accepted document, in bytes. |

## Running

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn html_extractor.app:app --reload
```

## Tests

```bash
python -m pytest tests/ -q
```

## Layout

```
src/html_extractor/
  app.py         FastAPI app, request/response models, routes
  config.py      environment-driven settings
  extractor.py   Beautiful Soup parsing helpers
tests/           TestClient-based API tests
```
