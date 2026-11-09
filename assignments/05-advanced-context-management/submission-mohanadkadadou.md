# Week 5 Submission (MCP Data Explorer): Mohanad Kadadou (2309115218)

Repository: https://github.com/mohanadkadadou/week5-mcp-data-explorer

- FastMCP server over STDIO with `search_countries` and the new `get_country_details` (currencies, languages, borders, flag URL); both return structured errors and never crash the server (32 offline tests).
- Driven from an MCP client over STDIO; transcript in `transcript.txt` and `writeup.md`. Claude Desktop registration is documented in the README but I did not edit its config.
- Deviation: restcountries.com v3.1 no longer works, so I used key-less public sources (mledoze/countries via jsDelivr, World Bank, flagcdn) and pinned `mcp<2`.
- README has install/run/register steps and a tool reference.
