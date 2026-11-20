const STORAGE_KEY = 'quote-of-day-favorites';
const EMPTY_STATE_MESSAGE = 'No quotes available right now. Please check back soon.';

const quotes = [
  { id: 1, text: 'The future depends on what you do today.', author: 'Mahatma Gandhi' },
  { id: 2, text: 'Success is the sum of small efforts, repeated day in and day out.', author: 'Robert Collier' },
  { id: 3, text: 'It always seems impossible until it is done.', author: 'Nelson Mandela' },
  { id: 4, text: 'Your limitation—it is only your imagination.', author: 'Anonymous' },
  { id: 5, text: 'Don’t watch the clock; do what it does. Keep going.', author: 'Sam Levenson' },
  { id: 6, text: 'Dream bigger. Do bigger.', author: 'Unknown' },
  { id: 7, text: 'The secret of getting ahead is getting started.', author: 'Mark Twain' },
  { id: 8, text: 'Small steps every day lead to big results.', author: 'Anonymous' }
];

const quoteTextEl = document.getElementById('quote-text');
const quoteAuthorEl = document.getElementById('quote-author');
const newQuoteBtn = document.getElementById('new-quote-btn');
const favoriteBtn = document.getElementById('favorite-btn');
const favoritesListEl = document.getElementById('favorites-list');
const favoritesCountEl = document.getElementById('favorites-count');

let currentQuote = null;

function getStoredFavorites() {
  try {
    const rawValue = window.localStorage.getItem(STORAGE_KEY);
    if (!rawValue) {
      return [];
    }

    const parsedValue = JSON.parse(rawValue);
    if (!Array.isArray(parsedValue)) {
      return [];
    }

    return parsedValue.filter((item) => typeof item === 'number' || typeof item === 'string');
  } catch (error) {
    console.warn('Unable to read favorites from localStorage.', error);
    return [];
  }
}

function saveFavorites(favorites) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(favorites));
  } catch (error) {
    console.warn('Unable to save favorites to localStorage.', error);
  }
}

function normalizeFavorites(favorites) {
  const validQuoteIds = new Set(quotes.map((quote) => quote.id));
  return favorites.filter((id) => validQuoteIds.has(Number(id)));
}

function getValidQuotes() {
  if (!Array.isArray(quotes)) {
    return [];
  }

  return quotes.filter((quote) => quote && typeof quote === 'object' && typeof quote.text === 'string' && quote.text.trim() && typeof quote.author === 'string' && quote.author.trim());
}

function renderEmptyState() {
  currentQuote = null;
  quoteTextEl.textContent = EMPTY_STATE_MESSAGE;
  quoteAuthorEl.textContent = '';
  favoriteBtn.disabled = true;
  favoriteBtn.setAttribute('aria-pressed', 'false');
  favoriteBtn.textContent = 'Add to favorites';
  favoritesListEl.innerHTML = '<li class="empty-state">No favorites available.</li>';
  favoritesCountEl.textContent = '0';
}

function getRandomQuote(excludedId = null) {
  const validQuotes = getValidQuotes();

  if (validQuotes.length === 0) {
    return null;
  }

  const availableQuotes = validQuotes.filter((quote) => quote.id !== excludedId);
  const selection = availableQuotes.length > 0 ? availableQuotes : validQuotes;
  const randomIndex = Math.floor(Math.random() * selection.length);
  return selection[randomIndex];
}

function isCurrentQuoteFavorite() {
  if (!currentQuote) {
    return false;
  }

  const storedFavorites = normalizeFavorites(getStoredFavorites());
  return storedFavorites.includes(currentQuote.id);
}

function renderFavoriteButton() {
  if (!currentQuote) {
    return;
  }

  const isFavorite = isCurrentQuoteFavorite();

  favoriteBtn.disabled = false;
  favoriteBtn.classList.toggle('is-favorite', isFavorite);
  favoriteBtn.setAttribute('aria-pressed', String(isFavorite));
  favoriteBtn.textContent = isFavorite ? 'Remove favorite' : 'Add to favorites';
}

function renderFavorites() {
  const storedFavorites = normalizeFavorites(getStoredFavorites());
  const favoriteQuotes = quotes.filter((quote) => storedFavorites.includes(quote.id));

  favoritesCountEl.textContent = String(favoriteQuotes.length);

  if (favoriteQuotes.length === 0) {
    favoritesListEl.innerHTML = '<li class="empty-state">No favorite quotes yet.</li>';
    return;
  }

  favoritesListEl.innerHTML = favoriteQuotes
    .map(
      (quote) => `
        <li class="favorite-item">
          <p>${quote.text} — ${quote.author}</p>
          <button class="remove-btn" type="button" data-remove-id="${quote.id}" aria-label="Remove ${quote.author} from favorites">
            Remove
          </button>
        </li>
      `
    )
    .join('');
}

function updateQuoteDisplay() {
  if (!currentQuote) {
    renderEmptyState();
    return;
  }

  quoteTextEl.textContent = currentQuote.text;
  quoteAuthorEl.textContent = `— ${currentQuote.author}`;
  renderFavoriteButton();
  renderFavorites();
}

function setCurrentQuote(nextQuote) {
  if (!nextQuote) {
    renderEmptyState();
    return;
  }

  currentQuote = nextQuote;
  updateQuoteDisplay();
}

function toggleCurrentQuoteFavorite() {
  if (!currentQuote) {
    return;
  }

  const storedFavorites = normalizeFavorites(getStoredFavorites());
  const favorites = storedFavorites.includes(currentQuote.id)
    ? storedFavorites.filter((id) => id !== currentQuote.id)
    : [...storedFavorites, currentQuote.id];

  saveFavorites(favorites);
  updateQuoteDisplay();
}

function removeFavoriteById(idToRemove) {
  const storedFavorites = normalizeFavorites(getStoredFavorites()).filter((id) => id !== Number(idToRemove));
  saveFavorites(storedFavorites);
  updateQuoteDisplay();
}

function initializeQuote() {
  const validQuotes = getValidQuotes();
  if (validQuotes.length === 0) {
    renderEmptyState();
    return;
  }

  const favorites = normalizeFavorites(getStoredFavorites());
  const fallbackQuote = validQuotes[0];
  const preferredQuote = favorites.length > 0 ? validQuotes.find((quote) => quote.id === Number(favorites[0])) || fallbackQuote : getRandomQuote();
  setCurrentQuote(preferredQuote);
}

newQuoteBtn.addEventListener('click', () => {
  const nextQuote = getRandomQuote(currentQuote ? currentQuote.id : null);
  setCurrentQuote(nextQuote);
});

favoriteBtn.addEventListener('click', () => {
  if (!currentQuote) {
    return;
  }

  toggleCurrentQuoteFavorite();
});

favoritesListEl.addEventListener('click', (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }

  const removeButton = target.closest('[data-remove-id]');
  if (!removeButton) {
    return;
  }

  removeFavoriteById(removeButton.getAttribute('data-remove-id'));
});

initializeQuote();
