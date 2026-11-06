#!/usr/bin/env bash
# Run every guardrail. Stops at the first failure and exits non-zero, so a formatting
# problem, a lint error, or a failing test fails the build.
set -euo pipefail

echo "== black =="
black --check .
echo "== ruff =="
ruff check .
echo "== pytest =="
pytest -q
echo "All checks passed."
