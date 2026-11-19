# Week 4 Submission — Thalia Eischeid

Repository: https://github.com/teischei/week4-mcp-data-explorer

Writeup: https://github.com/teischei/week4-mcp-data-explorer/blob/main/writeup.md

This submission contains a completed Data Explorer MCP server with two STDIO tools:

- `search_countries` returns compact country summaries.
- `get_country_details` returns currencies, languages, border codes, and a flag URL.
- Both tools return structured error messages for invalid input, timeouts, HTTP errors, no results, and ambiguous searches.
- The README includes setup, MCP registration instructions, and a tool reference.
- Six offline tests pass for successful tool calls and error-handling behavior.

The original REST Countries v3.1 endpoint has been retired, so the project uses the maintained v5 API.
