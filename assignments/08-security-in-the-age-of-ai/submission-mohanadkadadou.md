# Week 8 Submission (Security in the Age of AI): Mohanad Kadadou (2309115218)

Repository: https://github.com/mohanadkadadou/week8-secure-bookstore

- **Scan:** Semgrep 1.182.1 (registry rulesets, because `--config auto` refuses to run with metrics off), plus two local Semgrep rules and pip-audit for the issues Semgrep OSS missed (hardcoded secrets, the `innerHTML` sink, outdated `requests`). Before: 6 code findings and 24 dependency advisories. After: 0 findings, no known vulnerabilities.
- **Fixes (AI-assisted with Claude Code):** SQL injection (parameterised query), hardcoded secrets (environment variables), outdated `requests` 2.25.1 to 2.34.2; bonus: CORS allow-list and the XSS sink. Tests: 9 pass.
- **Prompt injection:** `POST /summarize-review` attack succeeded 20/20 before; after input framing, an output-format constraint and untrusted-output handling it succeeds 0/20, benign reviews still summarised; limits and residual risk are stated.
- [writeup.md](https://github.com/mohanadkadadou/week8-secure-bookstore/blob/main/writeup.md).
