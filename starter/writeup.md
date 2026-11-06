# Data Explorer MCP Server Writeup
**Author:** Mohammad Poorahmadi

## 1. Execution Transcripts

### Standard Tool Usage
**Prompt:** *"Use search_countries to search for 'Japan', then use get_country_details to get the currencies, languages, borders, and flag for 'Japan'."*

**Agent Execution Output:**
> **Search Results:**
> - Japan (Capital: Tokyo, Region: Asia, Population: 125836021)
>
> **Country Details for Japan:**
> - Currencies: Japanese yen (¥)
> - Languages: Japanese
> - Borders: None (island nation or no land borders)
> - Flag URL: https://flagcdn.com/w320/jp.png

### Error Handling & Edge Cases
**Prompt:** *"Try searching with search_countries using an empty string '', and try getting details with get_country_details for 'NonExistentLand123'."*

**Agent Execution Output:**
> **Results**
> | Tool | Input | Outcome | Error Message |
> |------|-------|---------|---------------|
> | `search_countries` | `""` (empty) | ❌ Validation Error | `"Query cannot be empty."` |
> | `get_country_details` | `"NonExistentLand123"` | ❌ API Error | `"Unexpected data format. The API may be unavailable or moved."` |
>
> **Observations**
> - **`search_countries` with `""`:** The server explicitly rejects empty queries with a user-friendly error. The tool handles bad input gracefully at the server level.
> - **`get_country_details` with `"NonExistentLand123"`:** The tool executes the network request and safely catches the upstream API format error rather than throwing an indexing crash.

## 2. Error Handling Approach
To ensure the MCP server remained resilient against network failures and upstream API changes (such as the deprecation of the v3.1 endpoint), multiple layers of hardening were implemented in `server.py`:
* **Redirect Resolution:** Added `follow_redirects=True` to the `httpx.get()` calls to gracefully handle `301 Moved Permanently` responses without throwing connection exceptions.
* **Schema Validation:** Implemented an `isinstance(data, dict)` check before processing the JSON response. This prevented fatal `TypeError` (slicing errors) and `KeyError` (indexing errors) when the deprecated API returned an error dictionary instead of the expected JSON list.
* **Input Sanitization:** Intercepted empty strings (`""` or `"   "`) using `.strip()` at the start of each tool, returning a clear validation message to the agent before any network request was attempted.
* **Exception Catching:** Wrapped API calls in `try/except` blocks handling `httpx.TimeoutException` (enforcing a 10-second timeout) and generic `httpx.HTTPError`s to prevent the entire MCP process from crashing.

## 3. What I Learned (Context Control)
Controlling what context an AI agent can reach is crucial for ensuring predictable, secure, and accurate outcomes. By exposing only strictly defined MCP tools rather than open-ended environments, we constrain the LLM's reasoning to verified data sources and minimize hallucinations. Furthermore, cleanly handling errors at the tool level prevents the agent from processing raw tracebacks, keeping its context window focused on actionable information. Ultimately, tightly scoped context empowers the agent to act deterministically and safely within its designated boundaries.