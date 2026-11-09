# Week 5 Write-up — Data Explorer MCP Server

**MCP client / agent:** Gemini CLI 0.64.0 with `gemini-3.5-flash-lite`, server registered
in `.gemini/settings.json` (STDIO). Full sessions are exported in `docs/`.

## 1. Transcript: the agent calling both tools

**Session 1** (`docs/agent-transcript.md`). Prompt: search "guinea"; get details for
Germany; get details for "Korea" and follow up if it is ambiguous; get details for
"Atlantis"; call `get_country_details` with an empty name.

Gemini sent the first five calls in one turn, then reacted to the ambiguous result:

| # | Tool call (as Gemini names it) | Result (abridged) |
|---|-------------------------------|-------------------|
| 1 | `mcp_data-explorer_search_countries {"query": "guinea"}` | 4 countries: Guinea (Conakry), Guinea-Bissau, Equatorial Guinea, Papua New Guinea |
| 2 | `mcp_data-explorer_get_country_details {"name": "Germany"}` | `currencies: [{EUR, Euro, €}]`, `languages: [German]`, 9 borders (Austria … Switzerland), `flag_url: …/data/deu.svg` |
| 3 | `… get_country_details {"name": "Korea"}` | `error_type: "ambiguous"`, `candidates: ["North Korea", "South Korea"]` |
| 4 | `… get_country_details {"name": "Atlantis"}` | `error_type: "not_found"`, "Use search_countries to find the right name." |
| 5 | `… get_country_details {"name": ""}` | `error_type: "invalid_input"`, "name must be a non-empty string." |
| 6 | `… get_country_details {"name": "South Korea"}` | `KRW (₩)`, `Korean`, borders `North Korea`, `…/data/kor.svg` |

Call 6 shows the structured error at work. The `ambiguous` result told the agent why
call 3 failed and listed the valid names, so it could make the follow-up my prompt asked
for in the next turn without another search.

**Session 2** (`docs/agent-transcript-upstream-error.md`). The server was started with
`COUNTRIES_DATA_URL` pointing at a missing file. Both tools returned
`error_type: "upstream_http_error"`, "The country dataset returned HTTP 404. Try again
later." The agent reported the error instead of inventing country data.

## 2. How errors are handled

- **Never raise, always return data.** Every failure is
  `{"error": <message>, "error_type": <stable code>}`, following the worked example's
  pattern. That is why all calls in both sessions came back as normal results, not MCP
  errors. The message is for the model to read; the `error_type` lets it branch.
- **Input:** empty, whitespace-only, over 100 characters, or a non-string → `invalid_input`.
  `limit` must be 1–50. Wrong-typed arguments sent over MCP (`"name": 42`) also reach
  this check. The parameters accept any value internally, but the schema still tells the
  model `string` / `integer`.
- **Upstream:** `load_countries()` turns every failure into one exception with a code:
  - a timeout (now 10 s, was 30 s) → `upstream_timeout`;
  - a non-2xx status, with the code in the message → `upstream_http_error`;
  - a network error → `upstream_unavailable`;
  - non-JSON, a non-list body, or a record with a malformed field → `bad_upstream_data`.

  The starter did not handle the last case: `resp.json()` raises `ValueError`, which
  escaped the tool as an unhandled exception. Records are validated *before* caching, and
  failed fetches are not cached, so the next call retries.
- **No result vs. too many:** `search_countries` returns `[]` for no match, as the example
  does. `get_country_details` must pick one country, so it returns `not_found` (pointing
  at `search_countries`) or `ambiguous` with at most 10 `candidates` plus `match_count`.
  "republic" matches 134 countries, and listing them all would only flood the model's
  context.
- **Matching:** exact matches (names, `DE`/`DEU` codes, alternative spellings) beat
  substrings, so "Niger" is not resolved to Nigeria. Alternative spellings also make
  "Turkey" find Türkiye, whose common name in the dataset is "Türkiye".
- **A starter bug I fixed:** the starter's comment says to build the flag URL with
  `FLAG_URL.format(cca3=...)`. `cca3` is upper case (`DEU`), but the files are named in
  lower case, so `…/data/DEU.svg` returns **404** and `…/data/deu.svg` returns 200. I
  lower-case the code.
- **Review:** CodeRabbit's automatic review on the PR found two real gaps, and I
  reproduced both before fixing them:
  - wrong-typed MCP arguments got a raw validation error instead of `invalid_input`;
  - a malformed record raised `AttributeError` and stayed cached until a restart.
- **Verification:**
  - 57 offline tests cover every error type, malformed records, the return shapes, and
    the MCP protocol (schema, calls, wrong-typed arguments) through an in-memory session.
  - A manual run with the official MCP STDIO client checked the real server against the
    live dataset.

## 3. What I learned

An MCP server is a context boundary: the agent can only see what my tools choose to
return, so the return shape matters as much as the data. Returning errors as structured
data instead of exceptions turned failures into usable context: the `ambiguous` result
told the agent which names would work, and it reported the HTTP 404 honestly instead of
guessing. Limits are part of that control.
Capping candidates at 10, defaulting `limit` to 5, and resolving neighbour codes to names
keep each result small and immediately useful instead of forcing extra calls or wasting
tokens. Gemini also wrapped every tool result in `<untrusted_context>`, a reminder that
whatever a server returns is data the client should not blindly obey.
