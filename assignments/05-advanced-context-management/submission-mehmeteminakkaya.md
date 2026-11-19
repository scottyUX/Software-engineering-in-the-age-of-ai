# Week 5 Advanced Context Management Submission: Mehmet Emin Akkaya

Repository: https://github.com/mehmeteminakkaya/week5-mcp-data-explorer
Writeup: https://github.com/mehmeteminakkaya/week5-mcp-data-explorer/blob/main/writeup.md

- `server.py`: a FastMCP server over the `mledoze/countries` dataset with **two tools**.
  `search_countries(query, limit)` returns compact `{name, capital, region, subregion, cca3}`
  rows (limit validated to 1–25); `get_country_details(name)` returns currencies, languages,
  borders (code **and** name) and the flag URL, and accepts a common name, an official name
  or a `cca3` code.
- Error handling: every failure returns a structured payload instead of raising — empty or
  wrong-type input, out-of-range limit, 15 s timeout, HTTP status errors, transport errors
  (DNS/refused), malformed or wrong-shaped JSON, records that are not objects, no result, and
  ambiguous names (which return `candidates` plus a hint). The dataset is fetched once and
  cached in memory.
- Registration/transcript: `scripts/mcp_client_demo.py` drives the server over the same
  STDIO protocol a desktop client uses and prints a reproducible transcript of both tools
  plus the bad-input and ambiguous cases; a second mode points the server at a dead port to
  show the transport-failure path. Both transcripts are pasted into `writeup.md`.
- README documents install, run, the Claude Desktop/IDE registration snippet, a full tool
  reference with example input/output, and the error-behaviour table.
- 36 offline tests (`pytest`), covering both tools, every error branch, non-object records,
  and the cache.
- CodeRabbit reviewed this submission and raised three findings. Two were real defects: flag
  URLs used an uppercase `cca3` (`data/TUR.svg` returns HTTP 404 — the dataset serves
  lowercase filenames) and a `[null]` payload passed the non-empty check, poisoned the cache
  and crashed both tools. Both are fixed in commit `bc46812`, with tests, and the no-match
  hint now offers a recovery path that actually works.

One finding worth flagging: the upstream dataset now says **"Türkiye"**, so
`get_country_details("Turkey")` returns a clean no-match error whose hint points at a
different spelling (the dataset uses local names) or the `cca3` code (`TUR`). Details are in
[writeup.md](https://github.com/mehmeteminakkaya/week5-mcp-data-explorer/blob/main/writeup.md).
