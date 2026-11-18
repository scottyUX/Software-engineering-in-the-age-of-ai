# Week 5 Writeup — Data Explorer MCP Server

**MCP client:** Claude Code 2.1.316 (headless), model `claude-opus-5-5` · **Transport:** STDIO

## Agent transcript

I registered the server with Claude Code through an MCP config file, using the virtual
environment's absolute Python path. The agent was given **only** the server's two tools, with no
file, shell, or web tools, so every answer had to come through MCP. The init event reported
`data-explorer` as `connected`, with tools `mcp__data-explorer__get_country_details` and
`mcp__data-explorer__search_countries`.

**Prompt:**
> Use the data-explorer tools to answer: (1) Which countries have 'guinea' in their name? Use
> search_countries with limit 10. (2) For Germany, what currencies and languages does it use, which
> countries border it, and what is its flag URL? Use get_country_details. (3) Call
> get_country_details with the name 'guin' and with an empty string, and tell me how the tool
> responded. Answer briefly.

**Tool calls and results** (from the session's JSON stream; long results shortened with `…`):

```text
→ search_countries {"query": "guinea", "limit": 10}
← [{"name":"Guinea","capital":"Conakry","region":"Africa","subregion":"Western Africa"},
   {"name":"Guinea-Bissau","capital":"Bissau",…},{"name":"Equatorial Guinea",…},
   {"name":"Papua New Guinea","capital":"Port Moresby","region":"Oceania",…}]

→ get_country_details {"name": "Germany"}
← {"name":"Germany","official_name":"Federal Republic of Germany","cca3":"DEU",
   "currencies":[{"code":"EUR","name":"Euro","symbol":"€"}],"languages":["German"],
   "borders":[{"code":"AUT","name":"Austria"},{"code":"BEL","name":"Belgium"},…],
   "flag_url":"https://raw.githubusercontent.com/mledoze/countries/master/data/deu.svg"}

→ get_country_details {"name": "guin"}
← {"error":"'guin' matches several countries; use an exact name",
   "candidates":["Equatorial Guinea","Guinea","Guinea-Bissau","Papua New Guinea"]}

→ get_country_details {"name": ""}
← {"error":"name must be a non-empty string"}
```

**Agent's final answer** (summarized): it listed the 4 Guinea countries with their capitals. For
Germany it gave the Euro, German, all 9 neighbours, and the flag URL. It then explained that `guin`
was rejected as ambiguous with a candidate list, and that the empty string got a validation error.
The session took 5 turns, with no errors.

## How I handled errors

- **One upstream handler for both tools.** `fetch_countries()` turns each failure into a short,
  specific message: a timeout says to retry, an HTTP error gives its status code, network errors
  and invalid JSON are reported separately. Each tool returns that message as an `error` field
  instead of raising, so the server never crashes. A failed download isn't cached, so the next
  call retries.
- **Input validation before any network call.** Blank or non-string `name`/`query` and a `limit`
  outside 1–50 are rejected with a clear message.
- **No-result vs. ambiguous vs. error.** A search with no matches returns `[]`, which is an
  answer, not an error. An ambiguous name returns `candidates`, so the agent can choose and retry
  instead of getting the wrong country. An exact name or ISO code always wins, which is why
  `Guinea` doesn't collide with Guinea-Bissau.
- **Validated with bad input.** `test_server.py` (28 tests) fakes the network with
  `httpx.MockTransport` to cover timeouts, HTTP 503, connection errors, invalid JSON, and caching.
  The transcript above shows the bad-input paths from a real agent.
- **One bug found while checking real data.** The starter suggests
  `FLAG_URL.format(cca3="DEU")`, but `…/data/DEU.svg` returns 404 and only `deu.svg` exists. The
  tool lowercases the code, so the flag URL it returns works.

## What I learned

An MCP server decides exactly what context an agent can reach: in this session the agent could
see only two functions and the fields I chose to return, so its answers were limited to what the
tools exposed. That makes the tool's return shape part of the prompt; names instead of bare border
codes, and a `candidates` list instead of a generic failure, let the agent answer and recover
without guessing. Structured errors matter as much as data, because an agent can only work around
a failure it can read. Narrow, validated tools also act as a safety boundary: the agent can't
reach anything the server doesn't expose.
