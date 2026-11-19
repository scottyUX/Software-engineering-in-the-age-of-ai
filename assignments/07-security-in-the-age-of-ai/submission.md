# Week 7 — Security in the Age of AI: Scan, Inject, Triage

This submission contains my completed Week 7 Security Assignment, including security scanning, vulnerability remediation, and prompt injection testing.

**Repository:** https://github.com/hacerdilarakivrak/week7-security-assignment

**Writeup:** https://github.com/hacerdilarakivrak/week7-security-assignment/blob/main/writeup.md

## Summary

- **Security Scanning:** Analyzed the vulnerable bookstore application using Semgrep and pip-audit.
- **Vulnerability Remediation:** Fixed SQL injection, insecure CORS configuration, and outdated dependencies.
- **Prompt Injection:** Demonstrated a successful prompt injection attack against the `/summarize-review` endpoint using Ollama (`llama3.1:8b`).
- **Mitigation:** Implemented untrusted-input framing and verified that the tested injection no longer succeeded.
- **Verification:** 3 pytest tests passed, Semgrep reported 0 findings, and pip-audit reported no known vulnerabilities.

The complete source code, security fixes, test files, and detailed findings are available in the repository linked above.