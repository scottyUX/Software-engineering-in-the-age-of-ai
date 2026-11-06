# Starter — Data Explorer MCP Server

A `FastMCP` server over the free, no-key **REST Countries** API. `search_countries` is a
worked example; you implement a second tool and harden both.

## Setup
```bash
pip install -r requirements.txt
```

## Run (STDIO)
```bash
python server.py
```
This speaks MCP over STDIO. Register the command in an MCP client (Claude Desktop or an
MCP-aware IDE), then invoke the tools from the client's chat.

## Register in Claude Desktop (example)
Add to your client's MCP config:
```json
{
  "mcpServers": {
    "data-explorer": { "command": "python", "args": ["/absolute/path/to/server.py"] }
  }
}
```

## Tool Reference

### `search_countries`
- **Description:** Searches for countries by name and returns a list of matches with high-level statistics.
- **Parameters:**
  - `query` (string): The name of the country to search for.
  - `limit` (integer, optional): Maximum number of results to return (default: 5).
- **Example Input:** `{ "query": "Japan", "limit": 1 }`
- **Example Output:** 
  `- Japan (Capital: Tokyo, Region: Asia, Population: 125836021)`

### `get_country_details`
- **Description:** Retrieves detailed geographic and economic information about a specific country.
- **Parameters:**
  - `name` (string): The exact common name of the country.
- **Example Input:** `{ "name": "Japan" }`
- **Example Output:** 
  ```text
  Details for Japan:
  - Currencies: Japanese yen (¥)
  - Languages: Japanese
  - Borders: None (island nation or no land borders)
  - Flag URL: https://flagcdn.com/w320/jp.png
  ```
