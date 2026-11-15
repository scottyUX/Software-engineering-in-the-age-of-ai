#!/usr/bin/env bash
# Git pre-commit hook: Lint/Format check + Test suite gate
set -e

echo "=== [Guardrail Hook] Running Ruff Lint Check ==="
if [ -f "assignments/05-agentic-codebase-structure/starter/.venv/bin/ruff" ]; then
    RUFF="assignments/05-agentic-codebase-structure/starter/.venv/bin/ruff"
    PYTEST="assignments/05-agentic-codebase-structure/starter/.venv/bin/pytest"
elif [ -f ".venv/bin/ruff" ]; then
    RUFF=".venv/bin/ruff"
    PYTEST=".venv/bin/pytest"
else
    RUFF="ruff"
    PYTEST="pytest"
fi

$RUFF check assignments/05-agentic-codebase-structure/starter/

echo "=== [Guardrail Hook] Running Pytest Suite ==="
$PYTEST -q assignments/05-agentic-codebase-structure/starter/test_main.py

echo "=== [Guardrail Hook] All checks passed! Proceeding with commit. ==="
exit 0
