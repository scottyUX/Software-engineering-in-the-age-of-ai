/**
 * Zero-dependency Test Suite Runner
 */

class TestRunner {
  constructor() {
    this.suites = [];
    this.currentSuite = null;
    this.totalTests = 0;
    this.passedTests = 0;
    this.failedTests = 0;
  }

  describe(name, fn) {
    const suite = { name, tests: [] };
    this.suites.push(suite);
    this.currentSuite = suite;
    fn();
    this.currentSuite = null;
  }

  test(name, fn) {
    if (!this.currentSuite) {
      this.describe('Default Suite', () => this.test(name, fn));
      return;
    }
    this.currentSuite.tests.push({ name, fn });
  }

  async run() {
    this.totalTests = 0;
    this.passedTests = 0;
    this.failedTests = 0;
    const results = [];

    for (const suite of this.suites) {
      const suiteResult = { name: suite.name, tests: [] };
      for (const t of suite.tests) {
        this.totalTests++;
        let passed = false;
        let error = null;
        try {
          await t.fn();
          passed = true;
          this.passedTests++;
        } catch (err) {
          passed = false;
          error = err;
          this.failedTests++;
        }
        suiteResult.tests.push({ name: t.name, passed, error });
      }
      results.push(suiteResult);
    }

    const summary = {
      total: this.totalTests,
      passed: this.passedTests,
      failed: this.failedTests,
      success: this.failedTests === 0,
      suites: results
    };

    if (typeof window !== 'undefined') {
      window.__TEST_RESULTS__ = summary;
      this.renderHTML(summary);
    }

    return summary;
  }

  renderHTML(summary) {
    const root = document.getElementById('test-results');
    if (!root) return;

    let html = `
      <div class="test-summary ${summary.success ? 'all-passed' : 'has-failures'}">
        <h2>${summary.success ? '✓ All Tests Passed' : '✗ Some Tests Failed'}</h2>
        <p>Total: <strong>${summary.total}</strong> | Passed: <strong class="passed-count">${summary.passed}</strong> | Failed: <strong class="failed-count">${summary.failed}</strong></p>
      </div>
    `;

    for (const suite of summary.suites) {
      html += `<div class="suite-card"><h3>${suite.name}</h3><ul class="test-list">`;
      for (const t of suite.tests) {
        if (t.passed) {
          html += `<li class="test-item pass"><span class="badge">PASS</span> <span class="test-name">${t.name}</span></li>`;
        } else {
          html += `<li class="test-item fail">
            <span class="badge">FAIL</span> <span class="test-name">${t.name}</span>
            <pre class="error-msg">${t.error ? (t.error.stack || t.error.message) : 'Unknown error'}</pre>
          </li>`;
        }
      }
      html += `</ul></div>`;
    }

    root.innerHTML = html;
  }
}

export const runner = new TestRunner();
export const describe = (name, fn) => runner.describe(name, fn);
export const test = (name, fn) => runner.test(name, fn);
