# Week 7 Submission: Mohamad Abdullah Abd

**Project repository:** https://github.com/mohamad-abdullah-710/week7-security

This public repository contains the Week 7 vulnerable bookstore, scanned with Semgrep (Code, custom rules and Supply Chain) in GitHub Actions because Smart App Control blocks Semgrep on my Windows machine. I fixed three findings across categories with Claude Code — SQL injection (SAST), hardcoded secrets (Secrets) and the outdated `requests` 2.25.1 (SCA) — each verified by its own re-scan with `pytest` green, and demonstrated a prompt injection on `/summarize-review` (5/5 obeyed) that input framing with delimiters blocked (0/5). `writeup.md` and `docs/` hold the findings overview, before/after diffs, scan links, attack transcripts and what I learned.
