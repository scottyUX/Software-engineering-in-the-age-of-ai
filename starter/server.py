"""Data Explorer — MCP server skeleton for Week 4.

Wraps the free, no-key REST Countries API (https://restcountries.com) and exposes it
to an agent as MCP tools over STDIO. One tool is implemented as a worked example;
finish the second (and improve error handling) to complete the assignment.

Setup:
    pip install -r requirements.txt
Run (STDIO) — register this command in your MCP client (e.g. Claude Desktop / an IDE):
    python server.py
"""
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server for the assignment
mcp = FastMCP("data-explorer")

BASE_URL = "https://restcountries.com/v3.1"

@mcp.tool()
def search_countries(query: str, limit: int = 5) -> str:
    """Search for countries by name."""
    query = query.strip()
    if not query:
        return "Error: Query cannot be empty."

    try:
        # Added follow_redirects=True to handle 301 Moved Permanently
        resp = httpx.get(f"{BASE_URL}/name/{query}", timeout=10, follow_redirects=True)
        
        if resp.status_code == 404:
            return f"No results found for '{query}'."
            
        resp.raise_for_status()
        data = resp.json()

        # Hardening check: Prevent slice error if API returns a dictionary instead of a list
        if isinstance(data, dict):
            return "API Error: Unexpected data format. The API may be unavailable or moved."

        # Slicing is now safe because we verified data is a list
        results = data[:limit]
        
        output = []
        for c in results:
            name = c.get("name", {}).get("common", "Unknown")
            capital = ", ".join(c.get("capital", ["Unknown"]))
            region = c.get("region", "Unknown")
            pop = c.get("population", "Unknown")
            output.append(f"- {name} (Capital: {capital}, Region: {region}, Population: {pop})")
            
        return "\n".join(output) if output else "No results found."

    except httpx.TimeoutException:
        return "Error: Request timed out. Please try again."
    except httpx.HTTPError as e:
        return f"Error: HTTP request failed - {str(e)}"
    except Exception as e:
        return f"Error: An unexpected error occurred - {str(e)}"


@mcp.tool()
def get_country_details(name: str) -> str:
    """Get detailed information about a specific country."""
    name = name.strip()
    if not name:
        return "Error: Country name cannot be empty."

    try:
        # Added follow_redirects=True to handle 301 Moved Permanently
        resp = httpx.get(f"{BASE_URL}/name/{name}?fullText=true", timeout=10, follow_redirects=True)
        
        if resp.status_code == 404:
            return f"No results found for '{name}'."
            
        resp.raise_for_status()
        data = resp.json()

        # Hardening check: Prevent KeyError: 0 if API returns a dictionary instead of a list
        if isinstance(data, dict):
            return "API Error: Unexpected data format. The API may be unavailable or moved."

        # Indexing is now safe because we verified data is a list
        country = data[0]
        
        # Extract required details: currencies, languages, borders, flag URL
        common_name = country.get("name", {}).get("common", name)
        
        currencies_dict = country.get("currencies", {})
        currencies = [f"{v.get('name', '')} ({v.get('symbol', '')})" for k, v in currencies_dict.items()]
        curr_str = ", ".join(currencies) if currencies else "None"

        langs_dict = country.get("languages", {})
        langs = list(langs_dict.values())
        lang_str = ", ".join(langs) if langs else "None"

        borders = country.get("borders", [])
        border_str = ", ".join(borders) if borders else "None (island nation or no land borders)"

        flags = country.get("flags", {})
        flag_url = flags.get("png") or flags.get("svg", "No flag available")

        return (
            f"Details for {common_name}:\n"
            f"- Currencies: {curr_str}\n"
            f"- Languages: {lang_str}\n"
            f"- Borders: {border_str}\n"
            f"- Flag URL: {flag_url}"
        )

    except httpx.TimeoutException:
        return "Error: Request timed out. Please try again."
    except httpx.HTTPError as e:
        return f"Error: HTTP request failed - {str(e)}"
    except Exception as e:
        return f"Error: An unexpected error occurred - {str(e)}"

if __name__ == "__main__":
    # Start the FastMCP server over STDIO
    mcp.run()