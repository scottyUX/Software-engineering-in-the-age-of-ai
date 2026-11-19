# Week 7 — Bookstore submission

This copy contains the Week 7 fixes. The lab still contains the original CORS
configuration and frontend `innerHTML` assignment. Run it locally. The
[writeup](../writeup.md) records the fixes and verification.

## Setup
```bash
pip install -r requirements.txt
pytest                      # 9 tests, including mocked model responses
uvicorn main:app --reload   # http://localhost:8000  (docs at /docs)
```

## Scan
```bash
semgrep scan --config auto
```
Scan the backend code, `static/index.html`, `requirements.txt`, and config for secrets.

## Endpoints
- `GET /books?q=...`, `GET /books/{id}`
- `POST /reviews` `{ "book_id": 1, "text": ... }`, `GET /reviews/{id}`
- `POST /summarize-review` `{ "text": ... }` selects one sentence from the review.
  It needs Ollama with `llama3.1:8b` or a compatible installed model selected via
  `OLLAMA_MODEL`.

## Files
- `main.py` — FastAPI routes and the original planted-issue list
- `static/index.html` — frontend with an XSS sink
- `test_main.py` — pytest suite for the bookstore and model-response validation
