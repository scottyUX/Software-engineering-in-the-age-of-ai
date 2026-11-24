# Week 7 Submission: Efeblk

- **Repository:** https://github.com/Efeblk/week7-bookstore-security
- **Writeup:** https://github.com/Efeblk/week7-bookstore-security/blob/main/writeup.md
- **AI coding agent used:** Antigravity (Gemini 4 Neon)
- **Scanners used:** Semgrep `1.186.0` (`semgrep scan --config auto`) and `pip-audit 2.10.1`
- **LLM used for prompt-injection demo:** Ollama `llama3.1:8b`

## Summary
- **Part 1 — Scan:** Ran `semgrep scan --config auto` (3 blocking SAST findings: wildcard CORS at `main.py:41` and raw formatted SQL at `main.py:102`) and `pip-audit -r requirements.txt` (24 known SCA vulnerabilities across `requests==2.25.1`, `idna==2.10`, and `urllib3==1.26.20`), plus triaged hardcoded secrets (`main.py:33-34`) and `innerHTML` stored XSS (`static/index.html:16`).
- **Part 2 — Fixes (`cb97d4c`):**
  1. **SAST (SQL Injection):** Replaced f-string SQL concatenation in `GET /books` with parameterized `?` binding (also restricted `CORSMiddleware` origins and replaced `innerHTML` with `textContent` in `static/index.html`).
  2. **Secrets:** Replaced hardcoded `API_KEY` and `SECRET_TOKEN` with `os.getenv(...)` and added `.env.example` + `.gitignore`.
  3. **SCA:** Upgraded `requirements.txt` to `requests>=2.33.0`, `urllib3>=2.8.0`, and `idna>=3.15`.
- **Part 3 — Prompt Injection (`eace4d8`):** Demonstrated live prompt injection on `POST /summarize-review` with Ollama `llama3.1:8b` (returning `{"summary": "HACKED"}`), then mitigated using `/api/chat` `system`/`user` role separation, escaped `<untrusted_review>` delimiters, `temperature: 0`, and bounded single-line output normalization; verified all three attack payloads are now blocked while normal reviews summarize properly.
- **Verification:** `semgrep scan --config auto` → `0 findings` (304 rules), `pip-audit -r requirements.txt` → `No known vulnerabilities found`, `pytest` → `8 passed`.