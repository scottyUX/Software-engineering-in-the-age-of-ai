/**
 * Unit Tests for UIController and Visual Transitions
 */

import { describe, test } from './test-runner.js';
import { assert, assertTrue, assertFalse, assertEqual } from './assert.js';
import { UIController } from '../src/ui/ui-controller.js';

describe('UIController Test Suite', () => {
  test('Applies fade-in class to quote-text element on renderQuote', () => {
    // Create mock DOM structure if running in browser
    if (typeof document === 'undefined') return;

    let testContainer = document.getElementById('test-dom-fixture');
    if (!testContainer) {
      testContainer = document.createElement('div');
      testContainer.id = 'test-dom-fixture';
      testContainer.innerHTML = `
        <article id="quote-card">
          <blockquote id="quote-text"></blockquote>
          <cite id="quote-author"></cite>
          <span id="quote-category"></span>
          <button id="btn-favorite"><span id="favorite-btn-text"></span></button>
          <button id="btn-new-quote"></button>
          <button id="btn-open-favorites"><span id="favorites-count">0</span></button>
          <button id="btn-close-favorites"></button>
          <aside id="favorites-drawer">
            <ul id="favorites-list"></ul>
            <div id="favorites-empty"></div>
          </aside>
          <div id="drawer-backdrop"></div>
          <div id="storage-warning" hidden></div>
        </article>
      `;
      document.body.appendChild(testContainer);
    }

    const ui = new UIController();
    const testQuote = {
      id: 'q-999',
      text: 'Testing fade in animation',
      author: 'Tester',
      category: 'Unit'
    };

    ui.renderQuote(testQuote, false);

    const quoteTextElem = document.getElementById('quote-text');
    assertEqual(quoteTextElem.textContent, 'Testing fade in animation');
    assertTrue(quoteTextElem.classList.contains('fade-in'), 'quote-text must have fade-in class');

    // Render another quote to verify transition restart
    const nextQuote = {
      id: 'q-998',
      text: 'Second test quote',
      author: 'Tester Two'
    };
    ui.renderQuote(nextQuote, true);
    assertEqual(quoteTextElem.textContent, 'Second test quote');
    assertTrue(quoteTextElem.classList.contains('fade-in'), 'quote-text must retain fade-in class on restart');
  });

  test('Updates favorite button status attributes and text correctly', () => {
    if (typeof document === 'undefined') return;
    const ui = new UIController();

    ui.updateFavoriteStatus(true);
    const btn = document.getElementById('btn-favorite');
    assertEqual(btn.getAttribute('aria-pressed'), 'true');
    const label = document.getElementById('favorite-btn-text');
    assertEqual(label.textContent, 'Favorited');

    ui.updateFavoriteStatus(false);
    assertEqual(btn.getAttribute('aria-pressed'), 'false');
    assertEqual(label.textContent, 'Favorite');
  });
});
