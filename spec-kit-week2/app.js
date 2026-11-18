// Quotations and their original play/scene references come from William
// Shakespeare's early modern English works. The original works are public domain.
export const QUOTES = Object.freeze([
  {
    id: 'hamlet-brevity',
    text: 'Brevity is the soul of wit.',
    attribution: 'William Shakespeare · Hamlet, Act II, Scene II',
    // Source: Hamlet, Act II, Scene II. Reuse-rights basis: original play, c. 1600, public domain.
  },
  {
    id: 'hamlet-self-true',
    text: 'This above all: to thine own self be true.',
    attribution: 'William Shakespeare · Hamlet, Act I, Scene III',
    // Source: Hamlet, Act I, Scene III. Reuse-rights basis: original play, c. 1600, public domain.
  },
  {
    id: 'hamlet-what-we-may-be',
    text: 'We know what we are, but know not what we may be.',
    attribution: 'William Shakespeare · Hamlet, Act IV, Scene V',
    // Source: Hamlet, Act IV, Scene V. Reuse-rights basis: original play, c. 1600, public domain.
  },
  {
    id: 'king-lear-nothing',
    text: 'Nothing will come of nothing.',
    attribution: 'William Shakespeare · King Lear, Act I, Scene I',
    // Source: King Lear, Act I, Scene I. Reuse-rights basis: original play, c. 1606, public domain.
  },
  {
    id: 'alls-well-love-all',
    text: 'Love all, trust a few, do wrong to none.',
    attribution: "William Shakespeare · All's Well That Ends Well, Act I, Scene I",
    // Source: All's Well That Ends Well, Act I, Scene I. Reuse-rights basis: original play, c. 1603, public domain.
  },
  {
    id: 'twelfth-night-greatness',
    text: "Some are born great, some achieve greatness, and some have greatness thrust upon 'em.",
    attribution: 'William Shakespeare · Twelfth Night, Act II, Scene V',
    // Source: Twelfth Night, Act II, Scene V. Reuse-rights basis: original play, c. 1601, public domain.
  },
  {
    id: 'measure-for-measure-doubts',
    text: 'Our doubts are traitors, and make us lose the good we oft might win, by fearing to attempt.',
    attribution: 'William Shakespeare · Measure for Measure, Act I, Scene IV',
    // Source: Measure for Measure, Act I, Scene IV. Reuse-rights basis: original play, c. 1604, public domain.
  },
]);

export const FAVORITES_STORAGE_KEY = 'a-little-perspective:favorites:v1';
const STORAGE_WARNING = 'Favorites may not be saved in this browser. You can still browse quotes.';

function quoteIdentity(quote) {
  const text = quote.text.trim().replace(/\s+/g, ' ').toLocaleLowerCase();
  const attribution = quote.attribution.trim().replace(/\s+/g, ' ').toLocaleLowerCase();
  return `${text}\u0000${attribution}`;
}

function distinctQuotes(quotes) {
  const seen = new Set();
  return quotes.filter((quote) => {
    const identity = quoteIdentity(quote);
    if (seen.has(identity)) return false;
    seen.add(identity);
    return true;
  });
}

export function pickNextQuote(quotes, previousQuoteId = null, random = Math.random) {
  const usableQuotes = distinctQuotes(quotes.filter((quote) => (
    quote
    && typeof quote.id === 'string'
    && quote.id.length > 0
    && typeof quote.text === 'string'
    && quote.text.trim().length > 0
    && typeof quote.attribution === 'string'
    && quote.attribution.trim().length > 0
  )));

  if (usableQuotes.length === 0) return null;

  const alternatives = previousQuoteId && usableQuotes.length > 1
    ? usableQuotes.filter((quote) => quote.id !== previousQuoteId)
    : usableQuotes;
  const sample = Number(random());
  const boundedSample = Number.isFinite(sample)
    ? Math.min(Math.max(sample, 0), 1 - Number.EPSILON)
    : 0;

  return alternatives[Math.floor(boundedSample * alternatives.length)];
}

function readFavoriteIds() {
  try {
    const stored = window.localStorage.getItem(FAVORITES_STORAGE_KEY);
    if (stored === null) return { ids: [], available: true };

    const parsed = JSON.parse(stored);
    if (!Array.isArray(parsed)) return { ids: [], available: false };

    const knownIds = new Set(QUOTES.map((quote) => quote.id));
    const ids = [...new Set(parsed.filter((id) => typeof id === 'string' && knownIds.has(id)))];
    return { ids, available: true };
  } catch {
    return { ids: [], available: false };
  }
}

function writeFavoriteIds(ids) {
  try {
    window.localStorage.setItem(FAVORITES_STORAGE_KEY, JSON.stringify([...ids]));
    return true;
  } catch {
    return false;
  }
}

function initializeQuotePage() {
  const quoteRegion = document.getElementById('quoteRegion');
  if (!quoteRegion) return;

  const quoteCard = document.getElementById('quoteCard');
  const quoteText = document.getElementById('quoteText');
  const quoteAttribution = document.getElementById('quoteAttribution');
  const newQuoteButton = document.getElementById('newQuoteButton');
  const favoriteButton = document.getElementById('favoriteButton');
  const favoritesList = document.getElementById('favoritesList');
  const noFavoritesMessage = document.getElementById('noFavoritesMessage');
  const favoritesCount = document.getElementById('favoritesCount');
  const statusMessage = document.getElementById('statusMessage');
  const noQuotesMessage = document.getElementById('noQuotesMessage');
  const usableQuotes = QUOTES.filter((quote) => (
    quote.id && quote.text.trim() && quote.attribution.trim()
  ));
  if (usableQuotes.length === 0) {
    quoteCard.hidden = true;
    noQuotesMessage.hidden = false;
    favoriteButton.disabled = true;
    return;
  }

  const favoriteState = readFavoriteIds();
  const favoriteIds = new Set(favoriteState.ids);
  let storageAvailable = favoriteState.available;
  let currentQuote = pickNextQuote(usableQuotes);

  function setStatus(message) {
    statusMessage.textContent = message;
  }

  function persistFavorites(successMessage) {
    if (!storageAvailable || !writeFavoriteIds(favoriteIds)) {
      storageAvailable = false;
      setStatus(STORAGE_WARNING);
      return;
    }
    setStatus(successMessage);
  }

  function renderFavoriteToggle() {
    const isFavorite = favoriteIds.has(currentQuote.id);
    favoriteButton.setAttribute('aria-pressed', String(isFavorite));
    favoriteButton.setAttribute(
      'aria-label',
      `${isFavorite ? 'Remove' : 'Add'} “${currentQuote.text}” ${isFavorite ? 'from' : 'to'} favorites`,
    );
  }

  function renderFavorites() {
    favoritesList.replaceChildren();
    const savedQuotes = usableQuotes.filter((quote) => favoriteIds.has(quote.id));
    for (const quote of savedQuotes) {
      const item = document.createElement('li');
      item.className = 'favorite-item';

      const details = document.createElement('div');
      details.className = 'favorite-details';
      const text = document.createElement('p');
      text.className = 'favorite-quote-text';
      text.textContent = quote.text;
      const attribution = document.createElement('p');
      attribution.className = 'favorite-attribution';
      attribution.textContent = quote.attribution;
      details.append(text, attribution);

      const removeButton = document.createElement('button');
      removeButton.className = 'favorite-remove';
      removeButton.type = 'button';
      removeButton.textContent = 'Remove';
      removeButton.setAttribute('aria-label', `Remove favorite: ${quote.text}`);
      removeButton.addEventListener('click', () => {
        favoriteIds.delete(quote.id);
        renderFavorites();
        renderFavoriteToggle();
        persistFavorites('Removed from favorites.');
      });

      item.append(details, removeButton);
      favoritesList.append(item);
    }

    noFavoritesMessage.hidden = savedQuotes.length > 0;
    favoritesCount.textContent = `${savedQuotes.length} ${savedQuotes.length === 1 ? 'quote' : 'quotes'} saved`;
  }

  function renderQuote(quote) {
    currentQuote = quote;
    quoteText.textContent = quote.text;
    quoteAttribution.textContent = quote.attribution;
    renderFavoriteToggle();
  }

  favoriteButton.disabled = false;
  if (!storageAvailable) setStatus(STORAGE_WARNING);
  renderQuote(currentQuote);
  renderFavorites();

  newQuoteButton.addEventListener('click', () => {
    const nextQuote = pickNextQuote(usableQuotes, currentQuote.id);
    if (nextQuote) renderQuote(nextQuote);
  });

  favoriteButton.addEventListener('click', () => {
    if (favoriteIds.has(currentQuote.id)) {
      favoriteIds.delete(currentQuote.id);
    } else {
      favoriteIds.add(currentQuote.id);
    }

    renderFavoriteToggle();
    renderFavorites();
    persistFavorites(favoriteIds.has(currentQuote.id) ? 'Added to favorites.' : 'Removed from favorites.');
  });
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeQuotePage, { once: true });
  } else {
    initializeQuotePage();
  }
}
