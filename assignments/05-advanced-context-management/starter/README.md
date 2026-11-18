# Starter — Data Explorer MCP Server

A `FastMCP` server over the open, no-key **[mledoze/countries](https://github.com/mledoze/countries)**
dataset (the data REST Countries was built on). `search_countries` is a worked example;
you implement a second tool and harden both.

> REST Countries' free v3.1 API was retired in October 2026 and its replacement needs an
> API key, so this starter fetches the dataset directly from GitHub instead. It is still
> an HTTPS call with real failure modes (timeouts, HTTP errors) to handle.

## Setup
```bash
pip install -r requirements.txt
```

## Run (STDIO)
```bash
python server.py
```
This speaks MCP over STDIO. It prints nothing and waits for a client; that is normal.
Register the command in an MCP client (Claude Desktop or an MCP-aware IDE), then invoke
the tools from the client's chat.

## Register in Claude Desktop (example)
Find the interpreter you installed the requirements into (activate your virtual
environment first, if you use one):
```bash
python -c "import sys; print(sys.executable)"
```
Add to your client's MCP config, using that absolute path as `command`:
```json
{
  "mcpServers": {
    "data-explorer": { "command": "/absolute/path/to/python", "args": ["/absolute/path/to/server.py"] }
  }
}
```

> **Common mistake:** setting `"command": "python"`. The client starts the server itself
> and may not see your terminal's `PATH` or active environment, so it can fail with
> `No such file or directory` or `ModuleNotFoundError: No module named 'httpx'`, which
> the client may only report as a closed connection.

## Your job
- Implement `get_country_details(name)` (currencies, languages, borders, flag URL).
- Make both tools handle empty/invalid input, HTTP errors, timeouts, and no results.
