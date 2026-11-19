#!/usr/bin/env bash
# Local guardrails: the same three checks CI runs. Stops at the first failure.
set -euo pipefail
cd "$(dirname "$0")"
echo "== black (format)"; python -m black --check --diff .
echo "== ruff (lint)";    python -m ruff check .
echo "== pytest";         python -m pytest
echo "All checks passed."
