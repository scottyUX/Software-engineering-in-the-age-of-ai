# Data Explorer — MCP Server

A `FastMCP` server that gives an agent two tools over the open, no-key
**[mledoze/countries](https://github.com/mledoze/countries)** dataset (the data REST
Countries was built on): `search_countries` and `get_country_details`. It speaks MCP over
**STDIO**.

> REST Countries' free v3.1 API was retired in October 2026 and its replacement needs an
> API key, so the server downloads the dataset directly from GitHub. It is still an HTTPS
> call with real failure modes (timeouts, HTTP errors), and both tools handle them.

## Install

Python 3.10+.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # mcp<2, httpx
pip install -r requirements-dev.txt      # + pytest, only needed for the tests
```

## Run

```bash
python server.py
```

It prints nothing and waits for an MCP client on stdin/stdout; that is normal. The
dataset (~1.3 MB) is downloaded on the first tool call and cached in memory. A failed
download is not cached, so the next call retries.

## Register in an MCP client

### Gemini CLI (used for the transcripts in `docs/`)

This folder already contains `.gemini/settings.json`:

```json
{
  "mcpServers": {
    "data-explorer": {
      "command": "python",
      "args": ["server.py"],
      "timeout": 30000
    }
  }
}
```

Then:
1. Activate `.venv`.
2. Run `gemini` from this folder.
3. Answer **Yes** to "Trust this folder?". Gemini CLI refuses to start STDIO MCP servers
   in untrusted folders.
4. Type `/mcp` to confirm that `data-explorer` is connected with 2 tools.

Gemini exposes the tools to the model as `mcp_data-explorer_search_countries` and
`mcp_data-explorer_get_country_details`, and asks for approval before each call.

### Claude Desktop or any other MCP client

Use absolute paths, because the client does not start in this folder:

```json
{
  "mcpServers": {
    "data-explorer": {
      "command": "/absolute/path/to/starter/.venv/bin/python",
      "args": ["/absolute/path/to/starter/server.py"]
    }
  }
}
```

## Tool reference

Both tools always return data and never raise. Errors come back as
`{"error": "<human-readable message>", "error_type": "<stable code>"}`. For
`search_countries` the error object is the single item of the returned list.

Arguments of the wrong type (`"name": 42`, `"limit": "five"`) also reach the tool and get
`invalid_input`. The parameters accept any JSON value internally, while the schema the
model sees still says `string` / `integer` with its limits. The one exception is a call
that omits a required argument (`name` or `query`): the MCP layer rejects it against the
schema before the tool runs.

### `search_countries(query, limit=5)`

Find countries whose common name, official name, or an alternative spelling contains
`query` (case-insensitive).

| Parameter | Type | Rules |
|-----------|------|-------|
| `query` | string | Required, 1–100 characters after trimming |
| `limit` | integer | Optional, 1–50, default 5 |

**Returns** a list of `{name, capital, region, subregion}`. `capital` is `null` when a
territory has none. An **empty list** means no match.

```text
search_countries(query="guinea", limit=2)
```
```json
[
  {"name": "Guinea", "capital": "Conakry", "region": "Africa", "subregion": "Western Africa"},
  {"name": "Guinea-Bissau", "capital": "Bissau", "region": "Africa", "subregion": "Western Africa"}
]
```

### `get_country_details(name)`

Currencies, languages, bordering countries, and the flag URL for **one** country.

| Parameter | Type | Rules |
|-----------|------|-------|
| `name` | string | Required, 1–100 characters. Accepts a common or official name (`Germany`, `Federal Republic of Germany`), a 2- or 3-letter code (`DE`, `DEU`), an alternative spelling (`Turkey` → Türkiye), or an unambiguous part of a name. |

Exact matches win over partial ones, so `Niger` returns Niger, not Nigeria.

**Returns** `{name, official_name, cca3, currencies, languages, borders, flag_url}`:
- `currencies` is a list of `{code, name, symbol}`.
- `languages` is a list of language names.
- `borders` is a list of `{code, name}`.

The lists are empty when a country has none (e.g. Antarctica has no currency, island
nations have no borders).

```text
get_country_details(name="Germany")
```
```json
{
  "name": "Germany",
  "official_name": "Federal Republic of Germany",
  "cca3": "DEU",
  "currencies": [{"code": "EUR", "name": "Euro", "symbol": "€"}],
  "languages": ["German"],
  "borders": [
    {"code": "AUT", "name": "Austria"}, {"code": "BEL", "name": "Belgium"},
    {"code": "CZE", "name": "Czechia"}, {"code": "DNK", "name": "Denmark"},
    {"code": "FRA", "name": "France"}, {"code": "LUX", "name": "Luxembourg"},
    {"code": "NLD", "name": "Netherlands"}, {"code": "POL", "name": "Poland"},
    {"code": "CHE", "name": "Switzerland"}
  ],
  "flag_url": "https://raw.githubusercontent.com/mledoze/countries/master/data/deu.svg"
}
```

```text
get_country_details(name="Korea")
```
```json
{
  "error": "'Korea' matches 2 countries. Call again with a more specific name.",
  "error_type": "ambiguous",
  "candidates": ["North Korea", "South Korea"],
  "match_count": 2
}
```

### Error types

| `error_type` | When | Tools |
|--------------|------|-------|
| `invalid_input` | Empty or whitespace-only text, text over 100 characters, a non-string name or query, `limit` that is not an integer from 1–50 | both |
| `not_found` | No country matches `name` | `get_country_details` |
| `ambiguous` | Several countries match; adds `candidates` (max 10) and `match_count` | `get_country_details` |
| `upstream_timeout` | The dataset did not answer within 10 seconds | both |
| `upstream_http_error` | The dataset answered with a non-2xx status (message includes the code) | both |
| `upstream_unavailable` | Network failure (DNS, connection refused, …) | both |
| `bad_upstream_data` | The response was not JSON, not a list of country objects, or a record has a malformed field (the message names the record and field). Nothing is cached, so the next call retries. | both |

## Test

```bash
pytest -q
```

57 offline tests. `httpx.get` is replaced, so no network is needed. They cover:
- the return shapes and name matching;
- every error type above, including malformed records;
- that a failed or malformed download is not cached;
- the real MCP protocol through an in-memory client session: the advertised schema,
  successful calls, and wrong-typed arguments.

To try the error path with a real client, point the server at a missing file:

```bash
COUNTRIES_DATA_URL=https://raw.githubusercontent.com/mledoze/countries/master/missing.json gemini
```

Both tools then return `upstream_http_error` ("HTTP 404"); see
`docs/agent-transcript-upstream-error.md`.

## Files

| Path | What it is |
|------|------------|
| `server.py` | The MCP server and both tools |
| `tests/test_server.py` | Offline pytest suite |
| `.gemini/settings.json` | Gemini CLI registration for this folder |
| `docs/agent-transcript*.md` | Gemini CLI sessions calling both tools |
| `writeup.md` | Transcript summary, error-handling notes, reflection |
