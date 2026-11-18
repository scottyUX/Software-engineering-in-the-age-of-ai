"""Data Explorer — MCP server skeleton for Week 5.

Wraps an open country dataset and exposes it to an agent as MCP tools over STDIO.
One tool is implemented as a worked example; finish the second (and improve error
handling) to complete the assignment.

Data source: the open `mledoze/countries` dataset (the data REST Countries was built
on), served as one JSON file from GitHub. No API key. It is fetched over HTTPS on the
first call and cached in memory, so HTTP errors and timeouts are still real failure
modes your tools must handle.

Setup:
    pip install -r requirements.txt
Run (STDIO) — register this command in your MCP client (e.g. Claude Desktop / an IDE):
    python server.py
"""
import httpx
from mcp.server.fastmcp import FastMCP

DATA_URL = "https://raw.githubusercontent.com/mledoze/countries/master/countries.json"
# Each country has a 3-letter `cca3` code; its flag lives at this URL.
FLAG_URL = "https://raw.githubusercontent.com/mledoze/countries/master/data/{cca3}.svg"

mcp = FastMCP("data-explorer")

_countries: list[dict] | None = None  # in-memory cache of the dataset


MAX_LIMIT = 50


def load_countries() -> list[dict]:
    """Download the dataset once and cache it. Raises httpx.HTTPError on failure."""
    global _countries
    if _countries is None:
        resp = httpx.get(DATA_URL, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        _countries = resp.json()
    return _countries


def fetch_countries() -> tuple[list[dict] | None, str | None]:
    """Return (countries, None) on success or (None, error message) on any upstream failure."""
    try:
        return load_countries(), None
    except httpx.TimeoutException:
        return None, "upstream request timed out; try again shortly"
    except httpx.HTTPStatusError as exc:
        return None, f"upstream returned HTTP {exc.response.status_code}"
    except httpx.HTTPError as exc:
        return None, f"upstream request failed: {exc}"
    except ValueError:
        return None, "upstream returned data that is not valid JSON"


@mcp.tool()
def search_countries(query: str, limit: int = 5) -> list[dict]:
    """Search countries by name. Returns a list of {name, capital, region, subregion}.

    This tool is a WORKED EXAMPLE — study how it validates input, fetches the data,
    handles errors, and returns model-friendly data.
    """
    if not isinstance(query, str) or not query.strip():
        return [{"error": "query must be a non-empty string"}]
    if not isinstance(limit, int) or not 1 <= limit <= MAX_LIMIT:
        return [{"error": f"limit must be an integer from 1 to {MAX_LIMIT}"}]
    countries, error = fetch_countries()
    if error:
        return [{"error": error}]

    q = query.strip().lower()
    matches = [
        c for c in countries
        if q in c["name"]["common"].lower() or q in c["name"]["official"].lower()
    ]
    # No matches is not an error: return an empty list.
    results = []
    for c in matches[:limit]:
        results.append(
            {
                "name": c["name"]["common"],
                "capital": (c.get("capital") or [None])[0],
                "region": c.get("region"),
                "subregion": c.get("subregion"),
            }
        )
    return results


def find_country(countries: list[dict], name: str) -> tuple[dict | None, dict | None]:
    """Return (country, None) for one clear match, or (None, error dict) otherwise.

    An exact name or ISO code wins, so "Guinea" or "DE" never collide with partial matches.
    """
    q = name.strip().lower()
    for c in countries:
        names = {c["name"]["common"].lower(), c["name"]["official"].lower()}
        codes = {c.get("cca2", "").lower(), c.get("cca3", "").lower()}
        if q in names or q in codes:
            return c, None
    partial = [c for c in countries if q in c["name"]["common"].lower() or q in c["name"]["official"].lower()]
    if len(partial) == 1:
        return partial[0], None
    if not partial:
        return None, {"error": f"no country matches '{name.strip()}'"}
    candidates = sorted(c["name"]["common"] for c in partial)
    return None, {"error": f"'{name.strip()}' matches several countries; use an exact name", "candidates": candidates[:10]}


@mcp.tool()
def get_country_details(name: str) -> dict:
    """Get one country's currencies, languages, neighbouring countries, and flag URL.

    `name` is a common or official name, or a 2- or 3-letter ISO code ("Germany", "DE", "DEU").
    Returns {name, official_name, cca3, currencies, languages, borders, flag_url}, or
    {"error": ...} with "candidates" when the name matches several countries.
    """
    if not isinstance(name, str) or not name.strip():
        return {"error": "name must be a non-empty string"}
    countries, error = fetch_countries()
    if error:
        return {"error": error}

    country, error = find_country(countries, name)
    if error:
        return error

    names_by_code = {c["cca3"]: c["name"]["common"] for c in countries}
    return {
        "name": country["name"]["common"],
        "official_name": country["name"]["official"],
        "cca3": country["cca3"],
        "currencies": [
            {"code": code, "name": info.get("name"), "symbol": info.get("symbol")}
            for code, info in (country.get("currencies") or {}).items()
        ],
        "languages": sorted((country.get("languages") or {}).values()),
        "borders": [
            {"code": code, "name": names_by_code.get(code, code)}
            for code in country.get("borders") or []
        ],
        "flag_url": FLAG_URL.format(cca3=country["cca3"].lower()),
    }


if __name__ == "__main__":
    mcp.run()
