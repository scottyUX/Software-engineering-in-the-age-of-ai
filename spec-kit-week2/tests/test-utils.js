/**
 * Zero-dependency lightweight test utility library for unit and integration testing.
 * Compatible with modern browser ES modules and JavaScript engines.
 */

export const testResults = {
  total: 0,
  passed: 0,
  failed: 0,
  suites: []
};

let currentSuite = null;

export function describe(name, fn) {
  const previousSuite = currentSuite;
  currentSuite = {
    name,
    tests: [],
    passed: 0,
    failed: 0
  };
  testResults.suites.push(currentSuite);

  try {
    fn();
  } catch (err) {
    console.error(`Suite "${name}" failed with unexpected error:`, err);
  } finally {
    currentSuite = previousSuite;
  }
}

export function it(testName, fn) {
  testResults.total += 1;
  const targetSuite = currentSuite || { name: "Default Suite", tests: [], passed: 0, failed: 0 };
  if (!currentSuite) {
    testResults.suites.push(targetSuite);
  }

  const testEntry = {
    name: testName,
    passed: false,
    error: null
  };

  try {
    fn();
    testEntry.passed = true;
    testResults.passed += 1;
    targetSuite.passed += 1;
  } catch (err) {
    testEntry.passed = false;
    testEntry.error = err.message || String(err);
    testResults.failed += 1;
    targetSuite.failed += 1;
  }

  targetSuite.tests.push(testEntry);
}

export function assert(condition, message = "Assertion failed") {
  if (!condition) {
    throw new Error(message);
  }
}

export function assertEqual(actual, expected, message) {
  if (actual !== expected) {
    throw new Error(message || `Expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
  }
}

export function assertNotEqual(actual, expected, message) {
  if (actual === expected) {
    throw new Error(message || `Expected values not to equal ${JSON.stringify(expected)}`);
  }
}

export function assertDeepEqual(actual, expected, message) {
  const actualStr = JSON.stringify(actual);
  const expectedStr = JSON.stringify(expected);
  if (actualStr !== expectedStr) {
    throw new Error(message || `Expected deep equality:\nExpected: ${expectedStr}\nActual:   ${actualStr}`);
  }
}

export function assertThrows(fn, expectedErrorRegexOrMessage, message) {
  let threw = false;
  let thrownError = null;
  try {
    fn();
  } catch (err) {
    threw = true;
    thrownError = err;
  }

  if (!threw) {
    throw new Error(message || "Expected function to throw, but it did not throw.");
  }

  if (expectedErrorRegexOrMessage) {
    const errText = thrownError?.message || String(thrownError);
    if (expectedErrorRegexOrMessage instanceof RegExp) {
      if (!expectedErrorRegexOrMessage.test(errText)) {
        throw new Error(message || `Thrown error "${errText}" did not match pattern ${expectedErrorRegexOrMessage}`);
      }
    } else if (typeof expectedErrorRegexOrMessage === "string") {
      if (!errText.includes(expectedErrorRegexOrMessage)) {
        throw new Error(message || `Thrown error "${errText}" did not include "${expectedErrorRegexOrMessage}"`);
      }
    }
  }
}
