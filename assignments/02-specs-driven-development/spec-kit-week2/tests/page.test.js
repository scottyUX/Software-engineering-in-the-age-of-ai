// Drives the real page in installed Chrome through the DevTools protocol, with no packages.
const { test, before, after } = require("node:test");
const assert = require("node:assert/strict");
const { spawn } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { pathToFileURL } = require("node:url");

const CHROME_PATHS = [
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/usr/bin/google-chrome",
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
];
const chromePath = CHROME_PATHS.find((candidate) => fs.existsSync(candidate));
const skip = chromePath ? false : "Google Chrome not found";

const PAGE_URL = pathToFileURL(path.join(__dirname, "..", "index.html")).href;
const FIXED_QUOTE = "Math.random = () => 0;";
const BLOCKED_STORAGE = `
  Storage.prototype.getItem = () => { throw new Error("blocked"); };
  Storage.prototype.setItem = () => { throw new Error("blocked"); };
`;

let chrome;
let profileDir;
let port;

async function waitForPort() {
  const portFile = path.join(profileDir, "DevToolsActivePort");
  for (let i = 0; i < 100; i++) {
    if (fs.existsSync(portFile)) {
      const contents = fs.readFileSync(portFile, "utf8");
      if (contents.includes("\n")) {
        return contents.split("\n")[0];
      }
    }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error("Chrome did not start");
}

// Opens the page in a new tab, running setupScript before the page's own scripts on every load.
async function openPage(setupScript) {
  const response = await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: "PUT" });
  const { webSocketDebuggerUrl } = await response.json();
  const socket = new WebSocket(webSocketDebuggerUrl);
  await new Promise((resolve) => socket.addEventListener("open", resolve));

  let nextId = 1;
  const pending = new Map();
  const loadWaiters = [];
  socket.addEventListener("message", ({ data }) => {
    const message = JSON.parse(data);
    if (message.id) {
      pending.get(message.id)(message.result);
    } else if (message.method === "Page.loadEventFired") {
      loadWaiters.splice(0).forEach((resolve) => resolve());
    }
  });
  const send = (method, params = {}) =>
    new Promise((resolve) => {
      const id = nextId++;
      pending.set(id, resolve);
      socket.send(JSON.stringify({ id, method, params }));
    });
  const nextLoad = () => new Promise((resolve) => loadWaiters.push(resolve));

  await send("Page.enable");
  await send("Page.bringToFront");
  await send("Runtime.enable");
  if (setupScript) {
    await send("Page.addScriptToEvaluateOnNewDocument", { source: setupScript });
  }
  const page = {
    async evaluate(expression) {
      const { result, exceptionDetails } = await send("Runtime.evaluate", {
        expression,
        returnByValue: true,
      });
      assert.equal(exceptionDetails, undefined);
      return result.value;
    },
    text: (id) => page.evaluate(`document.getElementById("${id}").textContent`),
    click: (id) => page.evaluate(`document.getElementById("${id}").click()`),
    pressed: () => page.evaluate(`document.getElementById("favorite").getAttribute("aria-pressed")`),
    async press(key) {
      const text = key === "Enter" ? "\r" : undefined;
      const windowsVirtualKeyCode = key === "Enter" ? 13 : 9;
      await send("Input.dispatchKeyEvent", { type: "keyDown", key, code: key, text, windowsVirtualKeyCode });
      await send("Input.dispatchKeyEvent", { type: "keyUp", key, code: key, windowsVirtualKeyCode });
    },
    async goto(url) {
      const loaded = nextLoad();
      await send("Page.navigate", { url });
      await loaded;
    },
    async reload() {
      const loaded = nextLoad();
      await send("Page.reload");
      await loaded;
    },
    close: () => socket.close(),
  };
  await page.goto(PAGE_URL);
  await page.evaluate("localStorage.clear()").catch(() => {});
  await page.reload();
  return page;
}

before(async () => {
  if (skip) return;
  profileDir = fs.mkdtempSync(path.join(os.tmpdir(), "quote-test-"));
  chrome = spawn(chromePath, [
    "--headless=new",
    "--remote-debugging-port=0",
    "--no-first-run",
    `--user-data-dir=${profileDir}`,
    "about:blank",
  ], { stdio: "ignore" });
  port = await waitForPort();
});

after(() => {
  if (skip) return;
  chrome.kill();
  fs.rmSync(profileDir, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
});

test("opening the page shows one quote and author (US1)", { skip }, async () => {
  const page = await openPage();
  assert.ok(await page.text("quote-text"));
  assert.ok(await page.text("quote-author"));
  page.close();
});

test("New quote always changes the displayed quote (US2)", { skip }, async () => {
  const page = await openPage();
  assert.equal(await page.text("new-quote"), "New quote");
  for (let i = 0; i < 50; i++) {
    const before = await page.text("quote-text");
    await page.click("new-quote");
    assert.notEqual(await page.text("quote-text"), before);
  }
  page.close();
});

test("a quote is visible within 1 second of opening (SC-001)", { skip }, async () => {
  const page = await openPage();
  assert.ok(await page.text("quote-text"));
  assert.ok((await page.evaluate("performance.now()")) < 1000);
  page.close();
});

test("both buttons work by keyboard (FR-008)", { skip }, async () => {
  const page = await openPage(FIXED_QUOTE);
  await page.press("Tab");
  assert.equal(await page.evaluate("document.activeElement.id"), "new-quote");
  const before = await page.text("quote-text");
  await page.press("Enter");
  assert.notEqual(await page.text("quote-text"), before);
  await page.press("Tab");
  assert.equal(await page.evaluate("document.activeElement.id"), "favorite");
  await page.press("Enter");
  assert.equal(await page.pressed(), "true");
  page.close();
});

test("a favorite can be marked and unmarked (US3)", { skip }, async () => {
  const page = await openPage(FIXED_QUOTE);
  assert.equal(await page.pressed(), "false");
  await page.click("favorite");
  assert.equal(await page.pressed(), "true");
  assert.equal(await page.text("favorite"), "Favorited");
  await page.click("favorite");
  assert.equal(await page.pressed(), "false");
  assert.equal(await page.text("favorite"), "Favorite");
  page.close();
});

test("a favorite is still marked after a reload (FR-006)", { skip }, async () => {
  const page = await openPage(FIXED_QUOTE);
  await page.click("favorite");
  await page.reload();
  assert.equal(await page.pressed(), "true");
  page.close();
});

test("corrupt saved favorites do not break the page (FR-007)", { skip }, async () => {
  const page = await openPage(FIXED_QUOTE);
  await page.evaluate(`localStorage.setItem("quote-of-the-day:favorites", "{broken")`);
  await page.reload();
  assert.ok(await page.text("quote-text"));
  assert.equal(await page.pressed(), "false");
  await page.click("favorite");
  assert.equal(await page.pressed(), "true");
  page.close();
});

test("blocked storage still allows quotes and favorites for the visit (FR-007)", { skip }, async () => {
  const page = await openPage(FIXED_QUOTE + BLOCKED_STORAGE);
  assert.ok(await page.text("quote-text"));
  await page.click("favorite");
  assert.equal(await page.pressed(), "true");
  await page.click("new-quote");
  assert.ok(await page.text("quote-text"));
  page.close();
});
