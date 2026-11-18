const STORAGE_KEY = "quote-of-the-day:favorites";

const quoteText = document.getElementById("quote-text");
const quoteAuthor = document.getElementById("quote-author");
const newQuoteButton = document.getElementById("new-quote");
const favoriteButton = document.getElementById("favorite");

function loadFavorites() {
  try {
    return QuoteLogic.parseFavorites(localStorage.getItem(STORAGE_KEY), QUOTES);
  } catch {
    return [];
  }
}

function saveFavorites(favorites) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(favorites));
  } catch {
    // Favorites still apply for this visit when saving is unavailable.
  }
}

let favorites = loadFavorites();
let currentQuote = QuoteLogic.pickRandomQuote(QUOTES);

function render() {
  const isFavorite = favorites.includes(currentQuote.id);
  quoteText.textContent = currentQuote.text;
  quoteAuthor.textContent = currentQuote.author;
  favoriteButton.setAttribute("aria-pressed", String(isFavorite));
  favoriteButton.textContent = isFavorite ? "Favorited" : "Favorite";
}

newQuoteButton.addEventListener("click", () => {
  currentQuote = QuoteLogic.pickDifferentQuote(QUOTES, currentQuote);
  render();
});

favoriteButton.addEventListener("click", () => {
  favorites = QuoteLogic.toggleFavorite(favorites, currentQuote.id);
  saveFavorites(favorites);
  render();
});

render();
