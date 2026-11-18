const { quotes, getRandomQuote, renderQuote, appState } = require('../src/app');

describe('User Story 1 - Random Quote Selection', () => {
  it('getRandomQuote should return a valid quote from the list', () => {
    const quote = getRandomQuote();
    expect(quote).toBeDefined();
    expect(quotes).toContainEqual(quote);
    expect(quote).toHaveProperty('id');
    expect(quote).toHaveProperty('text');
    expect(quote).toHaveProperty('author');
  });

  it('getRandomQuote should not always return the same quote', () => {
    let firstQuote = getRandomQuote();
    let gotDifferent = false;
    for (let i = 0; i < 20; i++) {
      if (getRandomQuote().id !== firstQuote.id) {
        gotDifferent = true;
        break;
      }
    }
    expect(gotDifferent).toBe(true);
  });
});

describe('User Story 2 - Render and Update State', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <blockquote id="quote-text"></blockquote>
      <p id="quote-author"></p>
    `;
  });

  it('renderQuote should update DOM and appState.currentQuoteId', () => {
    const quote = quotes[0];
    renderQuote(quote);
    expect(document.getElementById('quote-text').textContent).toBe(`"${quote.text}"`);
    expect(document.getElementById('quote-author').textContent).toBe(`- ${quote.author}`);
    expect(appState.currentQuoteId).toBe(quote.id);
  });
});

describe('User Story 3 - Favorites (localStorage)', () => {
  const { loadFavorites, saveFavorites, toggleFavorite } = require('../src/app');

  beforeEach(() => {
    localStorage.clear();
    appState.favorites = [];
    appState.currentQuoteId = null;
    
    document.body.innerHTML = `
      <blockquote id="quote-text"></blockquote>
      <p id="quote-author"></p>
      <button id="favorite-btn" class="icon-empty"></button>
    `;
  });

  it('loadFavorites should read from localStorage and default to empty array', () => {
    expect(loadFavorites()).toEqual([]);
    localStorage.setItem('quoteApp_favorites', JSON.stringify(['q1', 'q3']));
    expect(loadFavorites()).toEqual(['q1', 'q3']);
  });

  it('saveFavorites should write appState.favorites to localStorage', () => {
    appState.favorites = ['q2'];
    saveFavorites();
    expect(JSON.parse(localStorage.getItem('quoteApp_favorites'))).toEqual(['q2']);
  });

  it('toggleFavorite should add/remove quote id from favorites and update localStorage', () => {
    appState.currentQuoteId = 'q1';
    toggleFavorite();
    expect(appState.favorites).toContain('q1');
    expect(JSON.parse(localStorage.getItem('quoteApp_favorites'))).toContain('q1');

    toggleFavorite();
    expect(appState.favorites).not.toContain('q1');
    expect(JSON.parse(localStorage.getItem('quoteApp_favorites'))).not.toContain('q1');
  });
});

