import { expect, test } from '@playwright/test';
import { FAVORITES_STORAGE_KEY, pickNextQuote, QUOTES } from '../app.js';

test.describe('User Story 1: read and browse quotes', () => {
  test('the built-in quote collection has five or more distinct, complete entries', () => {
    expect(QUOTES.length).toBeGreaterThanOrEqual(5);
    expect(new Set(QUOTES.map((quote) => quote.id)).size).toBe(QUOTES.length);
    expect(new Set(QUOTES.map((quote) => `${quote.text}\u0000${quote.attribution}`)).size).toBe(QUOTES.length);
    for (const quote of QUOTES) {
      expect(quote.id).toBeTruthy();
      expect(quote.text.trim()).toBe(quote.text);
      expect(quote.text).toBeTruthy();
      expect(quote.attribution.trim()).toBe(quote.attribution);
      expect(quote.attribution).toBeTruthy();
    }
  });

  test('20 consecutive page openings show exactly one quote and attribution', async ({ page }) => {
    await page.goto('/');

    for (let opening = 0; opening < 20; opening += 1) {
      await expect(page.locator('#quoteCard blockquote')).toHaveCount(1);
      await expect(page.locator('#quoteText')).toBeVisible();
      await expect(page.locator('#quoteText')).not.toBeEmpty();
      await expect(page.locator('#quoteAttribution')).toBeVisible();
      await expect(page.locator('#quoteAttribution')).not.toBeEmpty();
      await expect(page.getByRole('button', { name: 'New quote' })).toBeEnabled();

      if (opening < 19) await page.reload();
    }
  });

  test('New quote changes the current quote without an immediate repeat', async ({ page }) => {
    await page.goto('/');

    const quote = page.locator('#quoteText');
    let previousQuote = await quote.innerText();
    const newQuoteButton = page.getByRole('button', { name: 'New quote' });
    for (let attempt = 0; attempt < 20; attempt += 1) {
      await newQuoteButton.click();
      const nextQuote = await quote.innerText();
      expect(nextQuote).not.toBe(previousQuote);
      previousQuote = nextQuote;
    }
  });

  test('the selection helper handles empty, single-entry, and non-repeating collections', () => {
    expect(pickNextQuote([], null, () => 0)).toBeNull();
    expect(pickNextQuote([{ id: 'invalid', text: '   ', attribution: 'A. Writer' }], null, () => 0)).toBeNull();

    const onlyQuote = { id: 'only', text: 'One quote', attribution: 'A. Writer' };
    expect(pickNextQuote([onlyQuote], onlyQuote.id, () => 0)).toEqual(onlyQuote);

    const alternatives = [
      { id: 'first', text: 'First quote', attribution: 'A. Writer' },
      { id: 'second', text: 'Second quote', attribution: 'B. Writer' },
    ];
    expect(pickNextQuote(alternatives, 'first', () => 0).id).toBe('second');
    expect(pickNextQuote([
      alternatives[0],
      { ...alternatives[0], id: 'duplicate-id' },
      alternatives[1],
    ], 'first', () => 0).id).toBe('second');
  });
});

async function setInitialQuote(page, quoteIndex = 0) {
  await page.addInitScript(({ index, count }) => {
    Math.random = () => (index + 0.25) / count;
  }, { index: quoteIndex, count: QUOTES.length });
}

test.describe('User Story 2: save and revisit favorite quotes', () => {
  test('the heart toggle is keyboard-operable and exposes its saved state', async ({ page }) => {
    await setInitialQuote(page);
    await page.goto('/');

    const favoriteButton = page.getByRole('button', { name: /add .* to favorites/i });
    await expect(favoriteButton).toHaveAttribute('aria-pressed', 'false');
    await favoriteButton.focus();
    await page.keyboard.press('Space');
    await expect(page.getByRole('button', { name: /remove .* from favorites/i }))
      .toHaveAttribute('aria-pressed', 'true');
    await expect(page.locator('#favoritesList').getByRole('listitem')).toHaveCount(1);
  });

  test('20 same-profile save and reload checks preserve favorites and removals', async ({ page }) => {
    const quote = QUOTES[0];
    await setInitialQuote(page);
    await page.goto('/');

    for (let check = 0; check < 20; check += 1) {
      await expect(page.locator('#quoteText')).toHaveText(quote.text);
      await page.getByRole('button', { name: /add .* to favorites/i }).click();
      await expect(page.locator('#favoritesList')).toContainText(quote.text);

      await page.reload();
      await expect(page.locator('#quoteText')).toHaveText(quote.text);
      await expect(page.getByRole('button', { name: /remove .* from favorites/i }))
        .toHaveAttribute('aria-pressed', 'true');
      await expect(page.locator('#favoritesList')).toContainText(quote.text);

      await page.locator('#favoritesList')
        .getByRole('button', { name: `Remove favorite: ${quote.text}` }).click();
      await expect(page.locator('#favoritesList')).not.toContainText(quote.text);
      await expect(page.locator('#noFavoritesMessage')).toBeVisible();

      await page.reload();
      await expect(page.locator('#favoritesList')).not.toContainText(quote.text);
      await expect(page.locator('#noFavoritesMessage')).toBeVisible();
    }
  });

  test('an empty favorites collection has a clear empty state', async ({ page }) => {
    await page.goto('/');

    await expect(page.locator('#noFavoritesMessage')).toBeVisible();
    await expect(page.locator('#favoritesList').getByRole('listitem')).toHaveCount(0);
  });

  test('malformed saved data is ignored with a non-blocking warning', async ({ page }) => {
    await page.addInitScript((key) => localStorage.setItem(key, '{not valid json'), FAVORITES_STORAGE_KEY);
    await page.goto('/');

    await expect(page.locator('#statusMessage')).toContainText(/favorites may not be saved/i);
    await expect(page.locator('#quoteText')).not.toBeEmpty();
    await page.getByRole('button', { name: 'New quote' }).click();
    await expect(page.locator('#quoteText')).not.toBeEmpty();
  });

  test('blocked storage leaves quotes usable and warns about persistence', async ({ page }) => {
    await page.addInitScript(() => {
      Object.defineProperty(window, 'localStorage', {
        configurable: true,
        get() {
          throw new DOMException('Storage is blocked', 'SecurityError');
        },
      });
    });
    await page.goto('/');

    await expect(page.locator('#statusMessage')).toContainText(/favorites may not be saved/i);
    await page.getByRole('button', { name: 'New quote' }).click();
    await expect(page.locator('#quoteText')).not.toBeEmpty();
    await page.getByRole('button', { name: /add .* to favorites/i }).click();
    await expect(page.locator('#favoritesList').getByRole('listitem')).toHaveCount(1);
  });

  test('a localStorage write failure warns but keeps favorites in the page', async ({ page }) => {
    await page.addInitScript(() => {
      Storage.prototype.setItem = () => {
        throw new DOMException('Storage is full', 'QuotaExceededError');
      };
    });
    await page.goto('/');
    await page.getByRole('button', { name: /add .* to favorites/i }).click();

    await expect(page.locator('#statusMessage')).toContainText(/favorites may not be saved/i);
    await expect(page.locator('#favoritesList').getByRole('listitem')).toHaveCount(1);
    await page.getByRole('button', { name: 'New quote' }).click();
    await expect(page.locator('#quoteText')).not.toBeEmpty();
  });
});

