# Week 7 Security in the Age of AI Submission: Mehmet Emin Akkaya

Repository: https://github.com/mehmeteminakkaya/week7-security-bookstore
Writeup: https://github.com/mehmeteminakkaya/week7-security-bookstore/blob/main/writeup.md

- **Scan.** `semgrep scan --config auto` reported 3 findings (SQL injection twice, wildcard
  CORS) and missed the hardcoded key and the `innerHTML` sink. I added two project rules in
  `.semgrep/bookstore-rules.yml` (CWE-798 secrets, CWE-79 DOM XSS) and used `pip-audit` for
  SCA, since Semgrep Supply Chain needs a platform login. Raw before/after output is in `scans/`.
- **Three fixes, one commit each, each with a test that fails on the starter:**
  - SAST, `main.py` `GET /books`: f-string query → bound parameter with escaped `LIKE`
    wildcards (`4d70a0d`). `q=' UNION SELECT id, text, text FROM reviews --` used to leak
    review text as book titles; now returns `[]`.
  - Secrets, `main.py:33-34`: `API_KEY` / `SECRET_TOKEN` moved to environment variables with
    `.env.example` (`4c90320`). Writeup notes the old values stay in history and must be rotated.
  - SCA, `requirements.txt`: `requests` 2.25.1 → 2.34.2, floors on `urllib3`/`idna`
    (`e12cfcc`). `pip-audit`: 24 advisories → none.
- **Also fixed:** CORS limited to configured origins, reviews rendered with `textContent`,
  and the LLM error no longer leaks the internal Ollama URL.
- **Re-scan:** `--config auto`, the project rules and `p/secrets`/`p/xss`/`p/owasp-top-ten`
  all 0 findings; `pip-audit` clean; 16 tests pass (3 original + 13 security regressions).
- **Prompt injection (llama3.1:8b on Ollama).** Starter and fixed app run side by side, 4
  attack payloads × 3 runs: the starter replied `HACKED` in **9/12** runs, the fixed app in
  **0/12**. Mitigation: instructions in the system prompt, the review between delimiters that
  are stripped from the input, a reminder after the data, and the output treated as untrusted
  (`format: json`, schema check, HTML stripped, length cap). Run tables in `docs/`.
