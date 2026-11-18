/**
 * Zero-dependency Assertion Library for Unit Tests
 */

export class AssertionError extends Error {
  constructor(message) {
    super(message);
    this.name = 'AssertionError';
  }
}

export function assert(condition, message = 'Assertion failed') {
  if (!condition) {
    throw new AssertionError(message);
  }
}

export function assertTrue(value, message = 'Expected value to be true') {
  if (value !== true) {
    throw new AssertionError(`${message} (got ${JSON.stringify(value)})`);
  }
}

export function assertFalse(value, message = 'Expected value to be false') {
  if (value !== false) {
    throw new AssertionError(`${message} (got ${JSON.stringify(value)})`);
  }
}

export function assertEqual(actual, expected, message) {
  const isDeepEqual = (a, b) => {
    if (a === b) return true;
    if (a == null || b == null) return false;
    if (typeof a !== 'object' || typeof b !== 'object') return false;
    
    const keysA = Object.keys(a);
    const keysB = Object.keys(b);
    if (keysA.length !== keysB.length) return false;
    
    for (const key of keysA) {
      if (!keysB.includes(key) || !isDeepEqual(a[key], b[key])) {
        return false;
      }
    }
    return true;
  };

  if (!isDeepEqual(actual, expected)) {
    const defaultMsg = `Expected ${JSON.stringify(expected)}, but got ${JSON.stringify(actual)}`;
    throw new AssertionError(message ? `${message}: ${defaultMsg}` : defaultMsg);
  }
}

export function assertNotEqual(actual, unexpected, message) {
  if (actual === unexpected) {
    const defaultMsg = `Expected value NOT to equal ${JSON.stringify(unexpected)}`;
    throw new AssertionError(message ? `${message}: ${defaultMsg}` : defaultMsg);
  }
}

export function assertThrows(fn, expectedErrorType, message) {
  let threw = false;
  let caughtError = null;
  try {
    fn();
  } catch (err) {
    threw = true;
    caughtError = err;
  }

  if (!threw) {
    throw new AssertionError(message || 'Expected function to throw an error, but it did not');
  }

  if (expectedErrorType && !(caughtError instanceof expectedErrorType)) {
    throw new AssertionError(
      message || `Expected error of type ${expectedErrorType.name}, but caught ${caughtError.name}: ${caughtError.message}`
    );
  }
}
