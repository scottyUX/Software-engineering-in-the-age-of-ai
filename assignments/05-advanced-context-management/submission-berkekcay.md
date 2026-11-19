# Advanced Context Management (MCP) submission: Berke Eren Akçay

Repository: https://github.com/berkekcay/country-explorer-mcp

`server.py` has two working tools: the hardened `search_countries` and `get_country_details`
(currencies, languages, borders with names, flag URLs). Both return
`{"error": {"code", "message"}}` for bad input, HTTP errors, timeouts and no results instead
of crashing, and 49 tests cover those cases, one of them over real STDIO.

The starter needed two fixes first: REST Countries retired the no-key `/v3.1` API (the server
now uses `/v5` with a free key), and the unpinned `mcp` package installs 2.x, where `FastMCP`
was renamed, so I pinned `mcp==1.30.0`. The README has the install, run and registration steps
and a tool reference; [writeup.md](https://github.com/berkekcay/country-explorer-mcp/blob/main/writeup.md)
has the agent transcript calling both tools, including a real timeout the agent recovered from.
