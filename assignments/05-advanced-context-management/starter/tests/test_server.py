"""Offline tests for the Data Explorer MCP server.

`httpx.get` is replaced in every test, so no test touches the network. The last two
tests go through the real MCP protocol with an in-memory client session.
"""
import json

import anyio
import httpx
import pytest
from mcp.shared.memory import create_connected_server_and_client_session

import server

COUNTRIES = [
    {
        "name": {"common": "Germany", "official": "Federal Republic of Germany"},
        "cca2": "DE",
        "cca3": "DEU",
        "altSpellings": ["DE", "Bundesrepublik Deutschland"],
        "capital": ["Berlin"],
        "region": "Europe",
        "subregion": "Western Europe",
        "currencies": {"EUR": {"name": "Euro", "symbol": "€"}},
        "languages": {"deu": "German"},
        "borders": ["AUT", "POL"],
    },
    {
        "name": {"common": "Austria", "official": "Republic of Austria"},
        "cca2": "AT",
        "cca3": "AUT",
        "capital": ["Vienna"],
        "region": "Europe",
        "subregion": "Central Europe",
        "currencies": {"EUR": {"name": "Euro", "symbol": "€"}},
        "languages": {"bar": "Austro-Bavarian German", "deu": "German"},
        "borders": ["DEU"],
    },
    {
        "name": {"common": "Niger", "official": "Republic of Niger"},
        "cca2": "NE",
        "cca3": "NER",
        "capital": ["Niamey"],
        "region": "Africa",
        "subregion": "Western Africa",
        "currencies": {"XOF": {"name": "West African CFA franc", "symbol": "Fr"}},
        "languages": {"fra": "French"},
        "borders": [],
    },
    {
        "name": {"common": "Nigeria", "official": "Federal Republic of Nigeria"},
        "cca2": "NG",
        "cca3": "NGA",
        "capital": ["Abuja"],
        "region": "Africa",
        "subregion": "Western Africa",
        "currencies": {"NGN": {"name": "Nigerian naira", "symbol": "₦"}},
        "languages": {"eng": "English"},
        "borders": ["NER"],
    },
    {
        "name": {"common": "Türkiye", "official": "Republic of Türkiye"},
        "cca2": "TR",
        "cca3": "TUR",
        "altSpellings": ["TR", "Turkiye", "Republic of Turkey"],
        "capital": ["Ankara"],
        "region": "Asia",
        "subregion": "Western Asia",
        "currencies": {"TRY": {"name": "Turkish lira", "symbol": "₺"}},
        "languages": {"tur": "Turkish"},
        "borders": [],
    },
    {
        "name": {"common": "Antarctica", "official": "Antarctica"},
        "cca2": "AQ",
        "cca3": "ATA",
        "region": "Antarctic",
        "currencies": {},
        "languages": {},
        "borders": [],
    },
]


def respond(status=200, body=None, text=None):
    """Return a fake httpx.get that answers with the given status and body."""

    def fake_get(url, **kwargs):
        request = httpx.Request("GET", url)
        if text is not None:
            return httpx.Response(status, text=text, request=request)
        return httpx.Response(status, json=COUNTRIES if body is None else body, request=request)

    return fake_get


def fail_with(exc):
    def fake_get(url, **kwargs):
        raise exc

    return fake_get


@pytest.fixture(autouse=True)
def fresh_cache(monkeypatch):
    """Every test starts with an empty cache and the fake dataset."""
    monkeypatch.setattr(server, "_countries", None)
    monkeypatch.setattr(server.httpx, "get", respond())


# --- get_country_details: success ---------------------------------------------------

def test_details_return_shape():
    result = server.get_country_details("Germany")
    assert result == {
        "name": "Germany",
        "official_name": "Federal Republic of Germany",
        "cca3": "DEU",
        "currencies": [{"code": "EUR", "name": "Euro", "symbol": "€"}],
        "languages": ["German"],
        "borders": [{"code": "AUT", "name": "Austria"}, {"code": "POL", "name": "POL"}],
        "flag_url": "https://raw.githubusercontent.com/mledoze/countries/master/data/deu.svg",
    }


@pytest.mark.parametrize(
    "name", ["germany", "  GERMANY  ", "DEU", "de", "Federal Republic of Germany", "Bundesrepublik Deutschland"]
)
def test_details_accepts_names_codes_and_alt_spellings(name):
    assert server.get_country_details(name)["name"] == "Germany"


def test_exact_match_beats_partial_match():
    # "niger" is also a substring of "Nigeria"; the exact name must win.
    assert server.get_country_details("Niger")["name"] == "Niger"


def test_partial_match_on_alt_spelling():
    assert server.get_country_details("Turkey")["name"] == "Türkiye"


def test_country_without_currencies_languages_or_borders():
    result = server.get_country_details("Antarctica")
    assert result["currencies"] == [] and result["languages"] == [] and result["borders"] == []
    assert result["flag_url"].endswith("/ata.svg")


# --- get_country_details: failures -------------------------------------------------

@pytest.mark.parametrize("bad", ["", "   ", "x" * 101, None, 42])
def test_details_invalid_input(bad):
    assert server.get_country_details(bad)["error_type"] == "invalid_input"


def test_details_not_found():
    result = server.get_country_details("Atlantis")
    assert result["error_type"] == "not_found"
    assert "search_countries" in result["error"]


def test_details_ambiguous_lists_candidates():
    result = server.get_country_details("republic")
    assert result["error_type"] == "ambiguous"
    assert result["match_count"] == 5
    assert result["candidates"] == ["Austria", "Germany", "Niger", "Nigeria", "Türkiye"]


def test_details_ambiguous_candidates_are_capped(monkeypatch):
    many = [{"name": {"common": f"Land {i:02d}", "official": f"Land {i:02d}"}, "cca3": f"L{i:02d}"} for i in range(30)]
    monkeypatch.setattr(server.httpx, "get", respond(body=many))
    result = server.get_country_details("land")
    assert result["match_count"] == 30
    assert len(result["candidates"]) == server.MAX_CANDIDATES


# --- upstream failures (both tools) ---------------------------------------------------

UPSTREAM_CASES = [
    (fail_with(httpx.ReadTimeout("timed out")), "upstream_timeout"),
    (respond(status=503), "upstream_http_error"),
    (respond(status=404), "upstream_http_error"),
    (fail_with(httpx.ConnectError("no route")), "upstream_unavailable"),
    (respond(text="<html>not json</html>"), "bad_upstream_data"),
    (respond(body={"not": "a list"}), "bad_upstream_data"),
]


@pytest.mark.parametrize("fake_get,error_type", UPSTREAM_CASES)
def test_details_upstream_failures(monkeypatch, fake_get, error_type):
    monkeypatch.setattr(server.httpx, "get", fake_get)
    result = server.get_country_details("Germany")
    assert result["error_type"] == error_type
    assert result["error"]


@pytest.mark.parametrize("fake_get,error_type", UPSTREAM_CASES)
def test_search_upstream_failures(monkeypatch, fake_get, error_type):
    monkeypatch.setattr(server.httpx, "get", fake_get)
    result = server.search_countries("ger")
    assert len(result) == 1
    assert result[0]["error_type"] == error_type and result[0]["error"]


def test_http_error_message_includes_status(monkeypatch):
    monkeypatch.setattr(server.httpx, "get", respond(status=503))
    assert "HTTP 503" in server.get_country_details("Germany")["error"]


def test_failed_fetch_is_not_cached(monkeypatch):
    monkeypatch.setattr(server.httpx, "get", fail_with(httpx.ConnectError("offline")))
    assert server.get_country_details("Germany")["error_type"] == "upstream_unavailable"
    monkeypatch.setattr(server.httpx, "get", respond())
    assert server.get_country_details("Germany")["name"] == "Germany"


# --- search_countries ----------------------------------------------------------------

def test_search_return_shape_and_limit():
    assert server.search_countries("republic", limit=2) == [
        {"name": "Germany", "capital": "Berlin", "region": "Europe", "subregion": "Western Europe"},
        {"name": "Austria", "capital": "Vienna", "region": "Europe", "subregion": "Central Europe"},
    ]


def test_search_no_results_is_empty_list():
    assert server.search_countries("Atlantis") == []


def test_search_missing_capital_is_none():
    assert server.search_countries("antarctica") == [
        {"name": "Antarctica", "capital": None, "region": "Antarctic", "subregion": None}
    ]


@pytest.mark.parametrize("query,limit", [("", 5), ("   ", 5), ("x" * 101, 5), ("ger", 0), ("ger", 51), ("ger", True)])
def test_search_invalid_input(query, limit):
    result = server.search_countries(query, limit)
    assert len(result) == 1 and result[0]["error_type"] == "invalid_input"


# --- through the MCP protocol --------------------------------------------------------

def call_over_mcp(steps):
    async def run():
        async with create_connected_server_and_client_session(server.mcp) as client:
            return await steps(client)

    return anyio.run(run)


def test_mcp_lists_both_tools_with_descriptions():
    async def steps(client):
        return (await client.list_tools()).tools

    tools = {t.name: t for t in call_over_mcp(steps)}
    assert set(tools) == {"search_countries", "get_country_details"}
    assert "flag URL" in tools["get_country_details"].description
    assert tools["get_country_details"].inputSchema["required"] == ["name"]


def test_mcp_calls_both_tools_and_returns_errors_as_data():
    async def steps(client):
        found = await client.call_tool("search_countries", {"query": "nig"})
        details = await client.call_tool("get_country_details", {"name": "Germany"})
        missing = await client.call_tool("get_country_details", {"name": "Atlantis"})
        return found, details, missing

    found, details, missing = call_over_mcp(steps)
    assert not found.isError and not details.isError and not missing.isError
    assert [c["name"] for c in (json.loads(b.text) for b in found.content)] == ["Niger", "Nigeria"]
    assert json.loads(details.content[0].text)["cca3"] == "DEU"
    assert json.loads(missing.content[0].text)["error_type"] == "not_found"


@pytest.mark.parametrize(
    "tool,args",
    [
        ("get_country_details", {"name": 42}),
        ("get_country_details", {"name": None}),
        ("search_countries", {"query": 123}),
        ("search_countries", {"query": "ger", "limit": "five"}),
        ("search_countries", {"query": "ger", "limit": True}),
    ],
)
def test_mcp_wrong_typed_arguments_return_structured_errors(tool, args):
    async def steps(client):
        return await client.call_tool(tool, args)

    result = call_over_mcp(steps)
    assert not result.isError
    assert json.loads(result.content[0].text)["error_type"] == "invalid_input"


def test_mcp_schema_still_advertises_types_and_limits():
    async def steps(client):
        return (await client.list_tools()).tools

    tools = {t.name: t.inputSchema["properties"] for t in call_over_mcp(steps)}
    assert tools["get_country_details"]["name"]["type"] == "string"
    assert tools["search_countries"]["query"]["type"] == "string"
    assert tools["search_countries"]["limit"] == {
        **tools["search_countries"]["limit"],
        "type": "integer", "minimum": 1, "maximum": server.MAX_LIMIT, "default": 5,
    }


# --- malformed records in the dataset --------------------------------------------------

GERMANY = COUNTRIES[0]


@pytest.mark.parametrize(
    "broken",
    [
        {**GERMANY, "name": "Germany"},
        {**GERMANY, "name": {"official": "Federal Republic of Germany"}},
        {**GERMANY, "cca3": 276},
        {**GERMANY, "capital": "Berlin"},
        {**GERMANY, "borders": "AUT"},
        {**GERMANY, "currencies": ["EUR"]},
        {**GERMANY, "languages": ["German"]},
    ],
)
def test_malformed_record_is_rejected_and_not_cached(monkeypatch, broken):
    monkeypatch.setattr(server.httpx, "get", respond(body=[broken] + COUNTRIES[1:]))
    assert server.get_country_details("Austria")["error_type"] == "bad_upstream_data"
    assert server.search_countries("aus")[0]["error_type"] == "bad_upstream_data"
    assert server._countries is None

    monkeypatch.setattr(server.httpx, "get", respond())
    assert server.get_country_details("Austria")["name"] == "Austria"


def test_missing_optional_fields_are_accepted(monkeypatch):
    minimal = [{"name": {"common": "Nowhere"}, "cca3": "NWH"}]
    monkeypatch.setattr(server.httpx, "get", respond(body=minimal))
    assert server.get_country_details("Nowhere") == {
        "name": "Nowhere",
        "official_name": "",
        "cca3": "NWH",
        "currencies": [],
        "languages": [],
        "borders": [],
        "flag_url": "https://raw.githubusercontent.com/mledoze/countries/master/data/nwh.svg",
    }
