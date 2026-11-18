# Data Explorer MCP Server

An MCP server over the open, no-key **[mledoze/countries](https://github.com/mledoze/countries)**
dataset (the data REST Countries was built on). It exposes two tools to an agent over STDIO.

> REST Countries' free v3.1 API was retired in October 2026 and its replacement needs an
> API key, so this server fetches the dataset directly from GitHub instead. It is still
> an HTTPS call with real failure modes (timeouts, HTTP errors) that the tools handle.

## Install

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run (STDIO)

```bash
python server.py
```

The server prints nothing and waits for an MCP client on stdin/stdout; that is normal. Press
`Ctrl+C` to stop it.

## Register in an MCP client

Use the **absolute path of the virtual environment's Python**, not a bare `python`. The client
starts the server itself and may not see your terminal's `PATH` or active environment. To print
the path, run this with the environment active:

```bash
python -c "import sys; print(sys.executable)"
```

**Claude Desktop** (`claude_desktop_config.json`):

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

**Claude Code:**

```bash
claude mcp add data-explorer -- /absolute/path/to/starter/.venv/bin/python /absolute/path/to/starter/server.py
```

## Tool reference

Every tool returns structured data. Failures come back as an `error` field instead of crashing
the server: bad input, upstream HTTP errors, timeouts, network errors, and invalid JSON.

### `search_countries(query, limit=5)`

Searches countries by common or official name (case-insensitive substring).

| Parameter | Type | Rules |
|---|---|---|
| `query` | string | Required, not blank |
| `limit` | integer | 1–50, default 5 |

```json
// search_countries("guinea", limit=2)
[
  {"name": "Guinea", "capital": "Conakry", "region": "Africa", "subregion": "Western Africa"},
  {"name": "Guinea-Bissau", "capital": "Bissau", "region": "Africa", "subregion": "Western Africa"}
]
```

No matches returns `[]`. Errors return a one-item list, for example
`[{"error": "limit must be an integer from 1 to 50"}]`.

### `get_country_details(name)`

Returns one country's currencies, languages, neighbours, and flag URL.

| Parameter | Type | Rules |
|---|---|---|
| `name` | string | Required. A common or official name, or a 2- or 3-letter ISO code (`Germany`, `DE`, `DEU`) |

An exact name or code wins over partial matches, so `Guinea` returns Guinea, not Guinea-Bissau.
A partial name that matches one country is accepted.

```json
// get_country_details("Germany")
{
  "name": "Germany",
  "official_name": "Federal Republic of Germany",
  "cca3": "DEU",
  "currencies": [{"code": "EUR", "name": "Euro", "symbol": "€"}],
  "languages": ["German"],
  "borders": [{"code": "AUT", "name": "Austria"}, {"code": "BEL", "name": "Belgium"}, "..."],
  "flag_url": "https://raw.githubusercontent.com/mledoze/countries/master/data/deu.svg"
}
```

| Situation | Response |
|---|---|
| Blank or non-string name | `{"error": "name must be a non-empty string"}` |
| No match | `{"error": "no country matches 'Atlantis'"}` |
| Several partial matches | `{"error": "'guin' matches several countries; use an exact name", "candidates": ["Equatorial Guinea", "Guinea", "Guinea-Bissau", "Papua New Guinea"]}` |
| Upstream timeout | `{"error": "upstream request timed out; try again shortly"}` |
| Upstream HTTP error | `{"error": "upstream returned HTTP 503"}` |

Territories without currencies or land borders (for example, Antarctica) return empty lists.

## Tests

```bash
pip install pytest
pytest
```

`test_server.py` fakes the network with `httpx.MockTransport`, so it covers timeouts, HTTP
errors, and invalid JSON without going online.
