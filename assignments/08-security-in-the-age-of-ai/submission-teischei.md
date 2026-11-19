# Week 8 Submission - Thalia Eischeid

Week 8 repository: https://github.com/teischei/week8-security-bookstore

Writeup: https://github.com/teischei/week8-security-bookstore/blob/main/writeup.md

This submission completes the Vulnerable Bookstore security assignment.

The repository includes Semgrep scanning, a local secret rule, and a dependency audit. I fixed the SQL injection, moved hardcoded values to environment variables, and upgraded the vulnerable requests dependency.

I also restricted the CORS policy and replaced the frontend innerHTML sink with safe text rendering.

For the prompt injection task, I demonstrated a real successful injection against the local model, then added input framing, output validation, and a direct instruction guard. The same payload was blocked after the mitigation.

The repository includes scan evidence, prompt-injection evidence, regression tests, and the writeup.
