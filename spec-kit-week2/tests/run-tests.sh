#!/bin/bash
# Test runner executing all unit and integration test suites
set -e

if command -v node >/dev/null 2>&1; then
  echo "Running test suite via Node.js..."
  node --test tests/**/*.test.js
elif [ -f "/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc" ]; then
  echo "Running test suite via JavaScriptCore (jsc)..."
  /usr/bin/python3 -c '
import subprocess, json

js_code = """
import("./tests/test-utils.js").then(async ({ testResults }) => {
    await import("./tests/unit/storage.test.js");
    await import("./tests/unit/quote-manager.test.js");
    await import("./tests/integration/app-flow.test.js");
    print(JSON.stringify(testResults));
}).catch(err => {
    print("FATAL ERROR: " + err);
});
"""

p = subprocess.run(["/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc", "-e", js_code], capture_output=True, text=True)
data = json.loads(p.stdout.strip())
for suite in data["suites"]:
    suite_name = suite["name"]
    print("\n--- " + suite_name + " ---")
    for t in suite["tests"]:
        status = "✔ PASS" if t["passed"] else "✖ FAIL"
        t_name = t["name"]
        print("  " + status + ": " + t_name)
        if t["error"]:
            print("      Error: " + str(t["error"]))

tot = data["total"]
pas = data["passed"]
fai = data["failed"]
print("\nTotal: " + str(tot) + " | Passed: " + str(pas) + " | Failed: " + str(fai))
if fai > 0:
    exit(1)
'
else
  echo "Open tests/runner.html in any web browser to view test results."
fi
