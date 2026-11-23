# Week 7 Submission — Yusuf Irmak

**Repository:** https://github.com/Yusufrmak497/bookstore-security

Semgrep (auto + two custom rules) and pip-audit findings; SQLi, hard-coded secrets and the outdated `requests` fixed with Claude Code (plus CORS and XSS), clean re-scan (0 findings) and 9 tests passing.
Prompt injection on `/summarize-review` succeeded 6/6 against `llama3.1:8b`, and 0/9 after the delimiter/system-prompt mitigation. Details in `writeup.md` and `evidence/`.
