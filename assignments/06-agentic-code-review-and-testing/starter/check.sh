#!/usr/bin/env bash
set -e

echo "==> 1. Checking code formatting with Black..."
black --check .

echo "==> 2. Linting code with Ruff..."
ruff check .

echo "==> 3. Running automated tests with Pytest..."
pytest

echo "==> All guardrail checks passed successfully!"
