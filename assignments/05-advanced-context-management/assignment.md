# Week 5 — Build a Custom MCP Server: The Data Explorer

**Estimated time: ~3 hours.**

## Overview
Agents are only as good as the context they can reach. You'll extend that reach by
building a **Model Context Protocol (MCP) server** that wraps a real API and exposes it
as agent tools. A working server skeleton is provided — you finish the second tool and
harden it, then use it from an MCP client.

## Learning goals
- Understand MCP building blocks: **tools** and **transport**.
- Implement a typed tool with real error handling.
- Register and drive an MCP server from an agent/client.

---

## Setup
The starter is in [`starter/`](starter/) — a `FastMCP` server over the open, no-key
**[mledoze/countries](https://github.com/mledoze/countries)** dataset (the data REST
Countries was built on), with `search_countries` implemented as a worked example.

> REST Countries' free v3.1 API was retired in October 2026 and its replacement needs an
> API key, so the starter fetches the dataset directly from GitHub. It is still an HTTPS
> call with real failure modes (timeouts, HTTP errors) that your tools must handle.
```bash
cd starter && pip install -r requirements.txt
python server.py   # runs over STDIO
```

> **Heads-up — REST Countries v3.1 has been retired.** Every `restcountries.com/v3.1/...`
> URL now answers `301` → a JSON error: *"This API version has been deprecated … migrate to
> our new version (v5)"*. Because `httpx` doesn't follow redirects by default, the starter's
> `search_countries` gets a `301` and `raise_for_status()` turns it into
> `{"error": "upstream request failed: ..."}` for **every** query. The new API,
> `https://api.restcountries.com/countries/v5?q=<name>`, needs a free key
> (`Authorization: Bearer <key>`, sign up at https://restcountries.com/sign-up; free plan
> 1,000 requests/month). Its fields changed too, e.g. `names.common`, `capitals[].name`,
> `currencies` is a list, `flag.url_png`. Read the key from an environment variable (e.g.
> `RESTCOUNTRIES_API_KEY`) and never commit it. If you don't want an account, the open
> [`mledoze/countries`](https://github.com/mledoze/countries) dataset that REST Countries was
> built on has the same v3-style fields (download once, search locally).
>
> **Common mistake — `No module named 'mcp.server.fastmcp'`:** `requirements.txt` installs
> the latest `mcp`, and **mcp 2.x renamed `FastMCP` to `MCPServer`**, so the starter's
> `from mcp.server.fastmcp import FastMCP` fails on a fresh install. Pin the 1.x SDK with
> `pip install "mcp>=1.2,<2" httpx` (or change the `mcp` line in `requirements.txt` to
> `mcp>=1.2,<2`), and check with `python -c "from mcp.server.fastmcp import FastMCP"`.
>
> **Tip:** `python server.py` prints nothing and waits — that's normal; it is waiting for an
> MCP client on STDIN. Use `npx @modelcontextprotocol/inspector python server.py` to try the
> tools in a browser before registering the server in your client, and use **absolute
> paths** (including your venv's `python`) in the client config.

## What to do
1. **Study** the provided `search_countries` tool: input validation, the data fetch,
   error handling, and the model-friendly return shape.
2. **Implement a second tool**, `get_country_details(name)`, returning currencies,
   languages, borders, and the flag URL — reusing the same error-handling pattern.
3. **Harden** both tools: empty/invalid input, HTTP errors, timeouts, and no-result cases
   should all return clean, structured messages (never crash the server).
4. **Register the server** in an MCP client (Claude Desktop or an MCP-aware IDE) and run
   each tool at least once.

> Scope note: **STDIO transport only** this week. No remote hosting or auth required.

## Deliverables
**Submit the GitHub repository link** for `starter/`, containing:
- Your finished `server.py` with **two working tools**.
- A `README.md`: how to install, run, and register the server, plus a **tool reference**
  (names, parameters, example input/output).
- A `writeup.md`: a transcript of an agent calling both tools, how you handled errors,
  and **what you learned** (3–5 sentences on controlling what context an agent can reach).

## Evaluation (100 pts)
- 40 — Second tool implemented correctly with the right return shape.
- 25 — Robust error handling on both tools (validated with bad input).
- 20 — Server registered and driven from an MCP client (transcript shown).
- 15 — Clear README tool reference + `writeup.md` reflection.

## References
- MCP server quickstart: https://modelcontextprotocol.io/quickstart/server
- Country dataset: https://github.com/mledoze/countries
