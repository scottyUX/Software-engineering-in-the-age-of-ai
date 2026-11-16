# Week 5 Submission — Data Explorer MCP Server

Repository: https://github.com/berfinaksoyy/mcp-data-explorer-week5

- `server.py`: `search_countries` (hardened) and the new `get_country_details` (currencies, languages, borders, flag URL).
- Both tools return structured errors for empty/invalid input, timeouts, HTTP errors, bad data, unknown and ambiguous names; the server never crashes (44 offline tests).
- Registered in Antigravity CLI (`agy mcp add`) and driven by the agent; transcript in `writeup.md`.
- `README.md` has install/run/register steps and a tool reference.
