#!/usr/bin/env bash
# Week 6 Guardrail Hook: Format check (black), Lint check (ruff), and Test runner (pytest)
set -e

echo "=== [Guardrail] 1. Black Code Formatting Check ==="
if [ -f "assignments/06-agentic-code-review-and-testing/starter/.venv/bin/black" ]; then
    VENV_BIN="assignments/06-agentic-code-review-and-testing/starter/.venv/bin"
elif [ -f ".venv/bin/black" ]; then
    VENV_BIN=".venv/bin"
else
    VENV_BIN=""
fi

if [ -n "$VENV_BIN" ]; then
    $VENV_BIN/black --check assignments/06-agentic-code-review-and-testing/starter/
    echo "=== [Guardrail] 2. Ruff Linter Check ==="
    $VENV_BIN/ruff check assignments/06-agentic-code-review-and-testing/starter/
    echo "=== [Guardrail] 3. Pytest Test Suite ==="
    $VENV_BIN/pytest -q assignments/06-agentic-code-review-and-testing/starter/test_main.py
else
    black --check .
    ruff check .
    pytest -q test_main.py
fi

echo "=== [Guardrail] All checks passed successfully! ==="
exit 0
