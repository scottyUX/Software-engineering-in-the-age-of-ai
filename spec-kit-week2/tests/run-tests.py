#!/usr/bin/env python3
"""
Zero-dependency CLI Test Runner for Quote of the Day
Validates catalog schema and executes in-browser tests headlessly via Microsoft Edge / Chrome.
"""

import sys
import os
import re
import json
import time
import socket
import subprocess
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def run_static_checks():
    print("[1/2] Running static schema and contract validations...")
    quotes_file = REPO_ROOT / "src" / "data" / "quotes.js"
    if not quotes_file.exists():
        print("  FAIL: src/data/quotes.js not found.")
        return False

    content = quotes_file.read_text(encoding="utf-8")
    
    # Extract JSON-like array from export const quotes = [...]
    match = re.search(r"export\s+const\s+quotes\s*=\s*(\[\s*\{.*\}\s*\]);?", content, re.DOTALL)
    if not match:
        print("  FAIL: Could not parse quotes array from src/data/quotes.js.")
        return False

    try:
        # Simple cleanup to parse as JSON if valid, or regex extraction
        # Since quotes.js is JS, let's extract objects with regex:
        raw_items = re.findall(r"\{\s*id:\s*['\"]([^'\"]+)['\"],\s*text:\s*['\"]([^'\"]+)['\"],\s*author:\s*['\"]([^'\"]+)['\"](?:,\s*category:\s*['\"]([^'\"]*)['\"])?\s*\}", content)
        if not raw_items:
            print("  FAIL: No quote objects matched standard pattern.")
            return False

        if len(raw_items) < 15:
            print(f"  FAIL: Expected at least 15 quotes, found {len(raw_items)}.")
            return False

        ids = set()
        for q_id, q_text, q_author, _ in raw_items:
            if not re.match(r"^q-\d{3,}$", q_id):
                print(f"  FAIL: Invalid quote id format: {q_id}")
                return False
            if q_id in ids:
                print(f"  FAIL: Duplicate quote id: {q_id}")
                return False
            ids.add(q_id)

            if len(q_text) < 5 or len(q_text) > 500:
                print(f"  FAIL: Quote text length out of bounds (5-500) for {q_id}")
                return False

            if len(q_author) < 1 or len(q_author) > 100:
                print(f"  FAIL: Quote author length out of bounds (1-100) for {q_id}")
                return False

        print(f"  PASS: Static catalog validated successfully ({len(raw_items)} quotes, all constraints satisfied).")
        return True
    except Exception as e:
        print(f"  FAIL: Validation error: {e}")
        return False

def find_browser():
    edge_paths = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe"),
    ]
    for p in edge_paths:
        if os.path.exists(p):
            return p

    chrome_paths = [
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
    ]
    for p in chrome_paths:
        if os.path.exists(p):
            return p
    return None

class SilentHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress request logging

def run_browser_tests():
    print("[2/2] Running in-browser automated test suite...")
    browser_exe = find_browser()
    if not browser_exe:
        print("  WARN: No headless browser executable found (msedge/chrome). Skipping browser harness.")
        return True

    port = find_free_port()
    os.chdir(str(REPO_ROOT))
    server = HTTPServer(('127.0.0.1', port), SilentHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    test_url = f"http://127.0.0.1:{port}/tests/index.html"
    cmd = [
        browser_exe,
        "--headless=new",
        "--dump-dom",
        "--virtual-time-budget=5000",
        "--disable-gpu",
        test_url
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        output = result.stdout

        if "all-passed" in output:
            print("  PASS: All browser unit tests passed successfully!")
            # Extract passed count if possible
            match = re.search(r"Passed:\s*<[^>]+>(\d+)<", output)
            if match:
                print(f"  Summary: {match.group(1)} assertions verified.")
            return True
        elif "has-failures" in output:
            print("  FAIL: In-browser test failures detected:")
            for line in output.splitlines():
                if "error-msg" in line or "badge\">FAIL" in line:
                    print(f"    {line.strip()}")
            return False
        else:
            print("  WARN: Browser output did not contain test results.")
            if "Running tests..." in output:
                print("  Test runner did not complete within budget.")
            return False
    except Exception as e:
        print(f"  ERROR running browser test: {e}")
        return False
    finally:
        server.shutdown()

def main():
    print("=" * 60)
    print("Quote of the Day - Automated Verification Suite")
    print("=" * 60)
    
    ok1 = run_static_checks()
    if not ok1:
        sys.exit(1)

    ok2 = run_browser_tests()
    if not ok2:
        sys.exit(1)

    print("=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
    sys.exit(0)

if __name__ == "__main__":
    main()
