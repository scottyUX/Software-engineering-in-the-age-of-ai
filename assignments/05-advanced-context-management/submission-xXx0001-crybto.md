# Week 5 Submission (Build a Custom MCP Server): Riza Arslan

**Repository:** https://github.com/xXx0001-crybto/week5-data-explorer

- Agent / MCP client: Claude Code (VS Code extension), connected to `server.py` over STDIO through the project's `.mcp.json`.
- FastMCP server `data-explorer` with two tools: `search_countries` (name, capital, region, subregion; `limit` 1–50) and `get_country_details` (official name, `cca3`, currencies, languages, borders resolved to names, flag URL). Lookups accept names, alternate spellings and 2/3-letter codes, so "Turkey" finds "Türkiye".
- Data source: the open [mledoze/countries](https://github.com/mledoze/countries) dataset, and `mcp` is pinned below 2.
- Errors come back as `{"error": ...}` and never crash the server: input validation, not-found names (with a `hint`), ambiguous names (with `matches`), timeouts, HTTP and connection errors, invalid JSON, and unexpected data. Failed downloads are not cached.
- Tests: 36 offline pytest tests pass, using mocked HTTP.
- [writeup.md](https://github.com/xXx0001-crybto/week5-data-explorer/blob/main/writeup.md) has a transcript of Claude Code calling both tools (including the error cases), the MCP client test run from `scripts/demo_client.py`, how I handled errors, and what I learned.
