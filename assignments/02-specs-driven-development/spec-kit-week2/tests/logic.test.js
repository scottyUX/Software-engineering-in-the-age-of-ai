const { test } = require("node:test");
const assert = require("node:assert/strict");
const { QUOTES } = require("../js/quotes.js");
const { QuoteLogic } = require("../js/logic.js");

test("the built-in list has at least 10 complete quotes with unique ids", () => {
  assert.ok(QUOTES.length >= 10);
  assert.equal(new Set(QUOTES.map((quote) => quote.id)).size, QUOTES.length);
  for (const quote of QUOTES) {
    assert.ok(quote.id && quote.text && quote.author, `incomplete quote: ${quote.id}`);
  }
});

test("pickRandomQuote always returns a quote from the list", () => {
  for (const random of [0, 0.5, 0.999999]) {
    assert.ok(QUOTES.includes(QuoteLogic.pickRandomQuote(QUOTES, () => random)));
  }
});

test("pickDifferentQuote never returns the current quote (FR-003)", () => {
  let current = QUOTES[0];
  for (let i = 0; i < 10000; i++) {
    const next = QuoteLogic.pickDifferentQuote(QUOTES, current);
    assert.notEqual(next.id, current.id);
    assert.ok(QUOTES.includes(next));
    current = next;
  }
});

test("100 new quotes show at least half of the quotes (SC-002)", () => {
  const seen = new Set();
  let current = QUOTES[0];
  for (let i = 0; i < 100; i++) {
    current = QuoteLogic.pickDifferentQuote(QUOTES, current);
    seen.add(current.id);
  }
  assert.ok(seen.size >= QUOTES.length / 2);
});

test("toggleFavorite marks and then unmarks a quote", () => {
  const marked = QuoteLogic.toggleFavorite([], "a");
  assert.deepEqual(marked, ["a"]);
  assert.deepEqual(QuoteLogic.toggleFavorite(marked, "a"), []);
});

test("parseFavorites starts empty for missing or corrupt data", () => {
  for (const saved of [null, "", "not json", "{}", "42", "null"]) {
    assert.deepEqual(QuoteLogic.parseFavorites(saved, QUOTES), [], `saved: ${saved}`);
  }
});

test("parseFavorites ignores unknown, non-string, and duplicate entries", () => {
  const saved = JSON.stringify(["torvalds-code", "removed-quote", 7, null, "torvalds-code"]);
  assert.deepEqual(QuoteLogic.parseFavorites(saved, QUOTES), ["torvalds-code"]);
});
