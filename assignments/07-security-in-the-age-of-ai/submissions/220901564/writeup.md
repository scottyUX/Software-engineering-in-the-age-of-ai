# Week 7 — Security in the Age of AI

**Kaan Erk Toraman · 220901564**

The [bookstore submission](starter/) is based on the [course starter](../../starter/). I used OpenAI Codex for remediation, test changes, and verification.

## Findings overview

| Category | Baseline finding | Result after remediation |
| --- | --- | --- |
| SAST | Semgrep `python.lang.security.audit.formatted-sql-query.formatted-sql-query` at `main.py:102` | No matches for the SQL rule |
| Secrets | Targeted Semgrep rule `bookstore.literal-demo-credential` at `main.py:33–34`. Bandit `B105` also flagged the token at line 34. | No matches for either check |
| SCA | `pip-audit` reported 24 advisory records across `requests`, `idna`, and `urllib3` after resolving the starter requirements. The advisory count includes duplicate records. | A fresh resolve and audit reported zero known vulnerabilities |

The Windows Semgrep `scan --config auto` command stopped in `semgrep-core` with a `socketpair` error. I used the Semgrep JavaScript engine (`@semgrep/engine` 1.18.1, Python parser 0.0.4) for the before-and-after Python scans. I ran the same two Semgrep Registry rules for SQL and CORS on both versions, plus a local Python rule matching literal assignments to `API_KEY` or `SECRET_TOKEN`. I used `pip-audit` 2.10.1 for dependency advisories.

The CORS rule still flags the wildcard origin. Manual review of the inline JavaScript in `static/index.html:16` found an `innerHTML` assignment that renders stored review text as HTML. Both are open findings outside the three selected fixes.

## Three fixes

### 1. Bind the search parameter (SAST)

Original `main.py:99–102` → [submission `main.py:103–108`](starter/main.py#L103-L108). SQLite now compiles the SQL with a placeholder and receives the search pattern as a separate value. Existing substring matching still works, and the regression test confirms a search term containing an apostrophe returns a normal response. The same Semgrep SQL rule went from one match to zero.

```diff
-    query = f"SELECT id, title, author FROM books WHERE title LIKE '%{q}%'"
-        rows = conn.execute(query).fetchall()
+        rows = conn.execute(
+            "SELECT id, title, author FROM books WHERE title LIKE ?", (f"%{q}%",)
+        ).fetchall()
```

### 2. Remove unused demo credentials (Secrets)

Original `main.py:32–34` → [submission `main.py`](starter/main.py). Neither constant had a reader, so the application needed no replacement credential or startup configuration. Removing both keeps their values out of the submission's source. The targeted Semgrep rule went from two matches to zero and Bandit stopped reporting `B105`. The diff below redacts the literals. A real credential exposed in a commit would also need revocation or rotation.

```diff
-API_KEY = "[redacted]"
-SECRET_TOKEN = "[redacted]"
```

### 3. Upgrade Requests (SCA)

Original `requirements.txt:7` → [submission `requirements.txt:5`](starter/requirements.txt#L5). The old Requests pin matched advisories including `PYSEC-2023-74`. The updated pin also allows the resolver to install newer transitive dependencies, including `idna` 3.20 and `urllib3` 2.8.0 in the verification environment. Running `pip-audit -r requirements.txt` after the change reported `No known vulnerabilities found`.

```diff
-requests==2.25.1
+requests==2.34.2
```

## Prompt-injection mitigation and verification

The original endpoint inserted the review into its instruction and returned the model's free-form response verbatim. In the submission, the server splits the review into candidate sentences and sends them as JSON data with a separate system instruction. The model selects a sentence by returning a JSON object with a single integer index. Pydantic enforces the response schema, the route checks the index bounds, and a valid response comes from the original review text. The model cannot supply arbitrary new summary text through this response path. The selection itself can still be influenced by the review contents.

| Verification | Observed result |
| --- | --- |
| TestClient with a stubbed model returning a valid index | HTTP 200 and the corresponding original sentence |
| TestClient with a stubbed model returning free-form text, an out-of-range index, a boolean index, or an extra field | HTTP 502 with `Invalid summary selection` in every case |
| TestClient with the local Ollama model `qwen3:8b` on an ordinary review | HTTP 200 with `The examples made the database chapters easy to follow.` |
| `python -m pytest -q` | 3 passed on the starter and 9 passed on the submission |

The negative cases exercise the application's response boundary with stubbed model outputs. There is no live before-fix prompt-injection result in this report. The local Ollama smoke test used the installed `qwen3:8b` model. The application defaults to the course's `llama3.1:8b` model.

## What I learned

An AI coding agent can connect scanner findings to specific code changes and help turn each fix into a regression check. The scanner's coverage matters because code patterns, credential literals, and dependency advisories each need different checks. Adding a model also creates a path for untrusted input to influence the application's response. A server-side output contract gives that path a limit that can be tested independently of the model.
