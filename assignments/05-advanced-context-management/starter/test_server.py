import httpx
import pytest

import server

GERMANY = {
    "name": {"common": "Germany", "official": "Federal Republic of Germany"},
    "cca2": "DE", "cca3": "DEU", "capital": ["Berlin"], "region": "Europe",
    "subregion": "Western Europe",
    "currencies": {"EUR": {"name": "Euro", "symbol": "€"}},
    "languages": {"deu": "German"},
    "borders": ["AUT", "XXX"],
}
AUSTRIA = {
    "name": {"common": "Austria", "official": "Republic of Austria"},
    "cca2": "AT", "cca3": "AUT", "capital": ["Vienna"], "region": "Europe",
    "currencies": {"EUR": {"name": "Euro", "symbol": "€"}},
    "languages": {"bar": "Austro-Bavarian German", "deu": "German"},
    "borders": ["DEU"],
}
GUINEA = {"name": {"common": "Guinea", "official": "Republic of Guinea"}, "cca2": "GN", "cca3": "GIN"}
GUINEA_BISSAU = {"name": {"common": "Guinea-Bissau", "official": "Republic of Guinea-Bissau"}, "cca2": "GW", "cca3": "GNB"}
PAPUA = {"name": {"common": "Papua New Guinea", "official": "Independent State of Papua New Guinea"}, "cca2": "PG", "cca3": "PNG"}
ANTARCTICA = {"name": {"common": "Antarctica", "official": "Antarctica"}, "cca2": "AQ", "cca3": "ATA"}
DATA = [GERMANY, AUSTRIA, GUINEA, GUINEA_BISSAU, PAPUA, ANTARCTICA]


@pytest.fixture(autouse=True)
def fresh_cache(monkeypatch):
    monkeypatch.setattr(server, "_countries", None)


def serve(monkeypatch, handler):
    """Route the server's HTTP call through a fake transport."""
    def fake_get(url, **kwargs):
        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            return client.get(url)
    monkeypatch.setattr(server.httpx, "get", fake_get)


def serve_data(monkeypatch):
    serve(monkeypatch, lambda request: httpx.Response(200, json=DATA))


def test_details_returns_currencies_languages_borders_and_flag(monkeypatch):
    serve_data(monkeypatch)
    details = server.get_country_details("Germany")
    assert details == {
        "name": "Germany",
        "official_name": "Federal Republic of Germany",
        "cca3": "DEU",
        "currencies": [{"code": "EUR", "name": "Euro", "symbol": "€"}],
        "languages": ["German"],
        "borders": [{"code": "AUT", "name": "Austria"}, {"code": "XXX", "name": "XXX"}],
        "flag_url": "https://raw.githubusercontent.com/mledoze/countries/master/data/deu.svg",
    }


@pytest.mark.parametrize("name", ["germany", "  GERMANY ", "Federal Republic of Germany", "DE", "deu"])
def test_details_accepts_names_and_iso_codes(monkeypatch, name):
    serve_data(monkeypatch)
    assert server.get_country_details(name)["cca3"] == "DEU"


def test_details_exact_name_beats_partial_matches(monkeypatch):
    serve_data(monkeypatch)
    assert server.get_country_details("Guinea")["name"] == "Guinea"


def test_details_unique_partial_match(monkeypatch):
    serve_data(monkeypatch)
    assert server.get_country_details("papua")["name"] == "Papua New Guinea"


def test_details_ambiguous_name_lists_candidates(monkeypatch):
    serve_data(monkeypatch)
    result = server.get_country_details("guin")
    assert "several countries" in result["error"]
    assert result["candidates"] == ["Guinea", "Guinea-Bissau", "Papua New Guinea"]


def test_details_country_without_currencies_or_borders(monkeypatch):
    serve_data(monkeypatch)
    details = server.get_country_details("Antarctica")
    assert details["currencies"] == [] and details["languages"] == [] and details["borders"] == []


@pytest.mark.parametrize("name", ["", "   ", None, 42])
def test_details_rejects_empty_or_invalid_name(monkeypatch, name):
    serve_data(monkeypatch)
    assert server.get_country_details(name) == {"error": "name must be a non-empty string"}


def test_details_unknown_country(monkeypatch):
    serve_data(monkeypatch)
    assert server.get_country_details("Atlantis") == {"error": "no country matches 'Atlantis'"}


def test_search_finds_matches_and_empty_list_for_none(monkeypatch):
    serve_data(monkeypatch)
    assert [c["name"] for c in server.search_countries("guinea", limit=2)] == ["Guinea", "Guinea-Bissau"]
    assert server.search_countries("Atlantis") == []


@pytest.mark.parametrize("query", ["", "  ", None])
def test_search_rejects_empty_query(monkeypatch, query):
    serve_data(monkeypatch)
    assert server.search_countries(query) == [{"error": "query must be a non-empty string"}]


@pytest.mark.parametrize("limit", [0, -1, 51, "5"])
def test_search_rejects_bad_limit(monkeypatch, limit):
    serve_data(monkeypatch)
    assert server.search_countries("germany", limit=limit) == [{"error": "limit must be an integer from 1 to 50"}]


def raise_timeout(request):
    raise httpx.ReadTimeout("timed out", request=request)


def raise_connect_error(request):
    raise httpx.ConnectError("name resolution failed", request=request)


@pytest.mark.parametrize("handler, message", [
    (raise_timeout, "upstream request timed out; try again shortly"),
    (lambda request: httpx.Response(503), "upstream returned HTTP 503"),
    (raise_connect_error, "upstream request failed: name resolution failed"),
    (lambda request: httpx.Response(200, text="<html>not json</html>"), "upstream returned data that is not valid JSON"),
])
def test_both_tools_return_clean_errors_on_upstream_failure(monkeypatch, handler, message):
    serve(monkeypatch, handler)
    assert server.get_country_details("Germany") == {"error": message}
    assert server.search_countries("Germany") == [{"error": message}]


def test_failed_fetch_is_not_cached(monkeypatch):
    serve(monkeypatch, lambda request: httpx.Response(503))
    assert "error" in server.get_country_details("Germany")
    serve_data(monkeypatch)
    assert server.get_country_details("Germany")["name"] == "Germany"
