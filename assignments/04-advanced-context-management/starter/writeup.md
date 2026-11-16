# MCP Server Implementation Writeup

## Agent Interaction Transcript

### Call 1: `search_countries`
- **Agent Input:**
  ```json
  { "query": "canada" }
  ```
- **Tool Response:**
  ```json
  [
    {
      "name": "Canada",
      "official_name": "Canada",
      "cca2": "CA",
      "capital": "Ottawa",
      "region": "Americas",
      "population": 38005238
    }
  ]
  ```

---

### Call 2: `get_country_details`
- **Agent Input:**
  ```json
  { "name": "Japan" }
  ```
- **Tool Response:**
  ```json
  {
    "name": "Japan",
    "official_name": "Japan",
    "capital": "Tokyo",
    "currencies": ["Japanese yen (¥)"],
    "languages": ["Japanese"],
    "borders": [],
    "flag_url": "https://flagcdn.com/w320/jp.png"
  }
  ```

---

### Call 3: Error Handling Validation
- **Agent Input (Invalid Country Name):**
  ```json
  { "name": "NonExistentCountry123" }
  ```
- **Tool Response:**
  ```json
  { "error": "Country 'NonExistentCountry123' not found." }
  ```

---

## Error Handling Approach
Both tools guard against server crashes by implementing structured exception handling:
1. **Input Validation:** Whitespace stripping and checking for empty string inputs prior to dispatching network requests.
2. **HTTP Error Mapping:** Catching `404 Not Found` responses and translating them into user-friendly diagnostic objects (`{"error": "..."}`) rather than letting raw exceptions escape.
3. **Network Resiliency:** Enforcing a 10-second timeout via `httpx.AsyncClient` to prevent request hangs, catching `httpx.TimeoutException` and general `Exception` instances cleanly.

---

## Reflection
Building an MCP server illustrates how structured tools grant AI agents deterministic control over real-world data context. By decoupling tool implementation from model execution, agents gain access to live external APIs without risking context buffer overload or hallucinated specifications. Standardizing tools via MCP ensures robust error boundaries, giving LLMs structured feedback when calls fail so they can self-correct effectively.