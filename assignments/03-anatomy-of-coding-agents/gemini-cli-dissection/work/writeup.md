# Week 3 Writeup — Inside a Coding Agent

**Name:** İsmet Efe Balık (Efeblk)
**Gemini CLI version (`gemini --version`):** 0.64.0
**OS / shell:** Windows 11 Pro + Git Bash (the agent's own `run_shell_command` runs `powershell.exe -NoProfile -Command`, see Part III)
**Model(s) seen in trace:** `gemini-3.5-flash-lite` only
**Session commit:** `d05bd73` ("Week 3: Gemini CLI session (agent's changes)")

> Evidence tags: `[OBSERVED]` = cite a timeline line, call number, or diff hunk.
> `[INFERRED]` = say what you're reasoning from.
>
> Line numbers like `timeline L20` refer to `submission/session_timeline.txt`. Call numbers
> (`#5`) match `submission/session_calls.csv`.

**How the session was run (differs from the default setup; read this first).**
- **Headless, not interactive.** The CLI was started headless with `gemini -m gemini-3.5-flash-lite --approval-mode auto_edit --allowed-tools run_shell_command -o stream-json -p "<the exact prompt>"`. Nobody was available to click approvals, so edits (`auto_edit`) and shell commands (`--allowed-tools`) were pre-approved. `--yolo` was not used. The effect is the same as approving every call, which the rules ask for anyway. But the system prompt says **Auto-Edit** mode and contains a "Non-Interactive Environment" rule (system.md L68) that an interactive session wouldn't have.
- **Operator.** The session was operated through Claude Code on my behalf.
- **Clean config.** Gemini CLI ran with an empty, isolated home folder, so no personal settings, memory or skills leaked into the prompt.
- **Extra trace file.** Headless mode also printed a JSON event stream. I kept it, redacted, as `submission/session_stream.jsonl`, because the telemetry log stops early (see Part I).
- **System prompt export.** `prompts/system.md` was exported the same headless way, so it says **Default** mode. Apart from that mode line, it is identical to `submission/session_system.md`.

---

## Part I — Session

**Narrative (one paragraph):**
1. **Research.** The agent opened with `update_topic` ("Reading Task Requirements") and read `TASK.md` in the same turn (timeline L5–6). It ran `python -m pytest` to reproduce the 2 failures (L9). Then it read all three `shopcart/` modules in one parallel turn (L12–14) and both test files in the next (L17–18).
2. **The long think.** After a 3,152-token think (call #5, L20) it published the plan as a second `update_topic`: fix `add_item`, fix discount-before-tax, add shipping in `pricing.py`, update the old totals with comments, add tests (L21).
3. **Implementation.** It made two `replace` edits, one to `cart.py` and one to `pricing.py` (L24, L27), and re-ran pytest (L30). The 2 original bugs were fixed, but 3 `Cart.total()` tests now failed because shipping was added. It re-read both test files (L33, L36), updated the three old expected values with a comment, added a free-shipping cart test (L39) and four `calculate_shipping` unit tests (L42).
4. **Validation and the end.** It ran `python -m pytest -v` (L46): 19/19 passed. The next model request hit the free-tier **429** (250,000 input tokens per minute; L48). The CLI waited about 60 s and retried. The agent then ran `git status` and a final "Task Completed" `update_topic`. The request after that failed with a **403** and the CLI process crashed (`session_stream.jsonl`, last 4 events).
5. **No text replies.** The agent never produced a single text message; every turn was tool calls only (`session_stream.jsonl` has no `"role":"assistant"` message events).

| Metric | Value |
|---|---|
| User prompts | 1 `[OBSERVED]` timeline L1, Summary |
| Model calls | 15 successful + 2 failed. Telemetry logged 13 responses and 1 error, a 429 (L48, Summary "13 (errors: 1)"). The stream shows 2 more successful calls after the retry (tool calls at 23:50:06 and 23:50:09) and a final call that failed with 403 (result at 23:50:10). Telemetry stopped at 23:49:00 because the process crashed before flushing. |
| Tool calls (failed) | 20 (0). Telemetry shows 18: `read_file` 8, `replace` 4, `update_topic` 3, `run_shell_command` 3. The stream adds `git status` (shell) and a 4th `update_topic`. |
| Final `pytest` result | **19 passed**. The agent's own run (stream, tool #18 output) and my rerun after it finished both passed: `19 passed in 0.02s`. |
| Did you step in? When / what? | No typed input. Tool calls were pre-approved by flags rather than clicked (see top). The session ended on an API 403 after the agent had finished the task, not because anyone stepped in. |

---

## Part II — System prompt annotation

### Outline
Line numbers refer to `prompts/system.md`.
1. L1 — Identity and mode ("You are Gemini CLI … operating in **Default** mode").
2. L3–9 — Core Mandates / Security & System Integrity: secrets, no unrequested commits, untrusted tool output.
3. L10–38 — Context Efficiency: turns cost more than tokens; parallel, scoped reads and searches.
4. L40–51 — Engineering Standards: `GEMINI.md` precedence, conventions, no hacks, Directive vs Inquiry, testing, scope.
5. L52–64 — Topic Updates: how and when to call `update_topic`.
6. L66–68 — Misc rules: don't revert, skill guidance, non-interactive (headless) environment.
7. L70–107 — Available Sub-Agents: `invoke_agent`, when to delegate, concurrency safety.
8. L109–124 — Available Agent Skills: `activate_skill` list.
9. L126–131 — Hook Context: treat `<hook_context>` as data.
10. L133–150 — Primary Workflows / Development Lifecycle: Research → Strategy → Execution (Plan → Act → Validate), re-evaluation after 3 failed fixes.
11. L152–166 — New Applications: plan mode first, default stacks.
12. L168–180 — Tone and Style.
13. L182–184 — Security and Safety Rules: explain modifying commands.
14. L186–215 — Tool Usage: response rules, parallelism, edit collisions, shell, memory files, confirmation protocol.
15. L217–219 — Interaction Details (`/help`, `/bug`).
16. L221–238 — Git Repository: never commit unless asked, how to commit, never push.

### Annotations (≥6)
#### Section: Tone and Style (tone and verbosity), L170–180
> "**Minimal Output:** Aim for fewer than 3 lines of text output (excluding tool use/code generation) per response whenever practical."
> "**No Chitchat:** Avoid conversational filler, preambles ("Okay, I will now...") … unless they are part of the **Topic Model**."
- **Behavior it produces:** Terse turns. Narration is moved into `update_topic`. `[OBSERVED]` Output tokens per call were 24–597 and mostly function-call arguments (`session_calls.csv`). The session contains zero assistant text messages (`session_stream.jsonl`).
- **Failure it prevents:** A CLI flooding the terminal and the context window with "Sure! Let me…" padding. Every text token is re-sent on every later call, because the full history is replayed (L16).
- **Side effect:** My prompt said "First write out your plan". The agent wrote the plan only inside `update_topic` (call #5 → L21), never as plain text. `[INFERRED]` The "No Chitchat … unless part of the Topic Model" rule pushed it there.

#### Section: Security and Safety Rules + Confirmation Protocol (when not to act / confirm), L182–183, L215
> "Before executing commands with `run_shell_command` that modify the file system, codebase, or system state, you *must* provide a brief explanation of the command's purpose and potential impact. … You should not ask permission to use the tool; the user will be presented with a confirmation dialogue upon use"
> "**Confirmation Protocol:** If a tool call is declined or cancelled, respect the decision immediately. Do not re-attempt the action or "negotiate" for the same tool call"
- **Behavior it produces:** Every shell call carries a human-readable `description`. Permission is enforced by the harness, not by the model asking. `[OBSERVED]` All 4 shell calls had a description, e.g. `"Run pytest to check failing tests"` (L9).
- **Failure it prevents:**
  - Users approving commands they don't understand.
  - A model that asks "may I run this?" in chat and then runs it anyway.
  - A model that retries a command the user refused.

#### Section: Development Lifecycle (workflow), L136–145
> "Operate using a **Research -> Strategy -> Execution** lifecycle. For the Execution phase, resolve each sub-task through an iterative **Plan -> Act -> Validate** cycle."
> "**Validation is the only path to finality.** Never assume success or settle for unverified changes."
- **Behavior it produces:** Read everything first, reproduce the failure, then edit, then test. `[OBSERVED]` The order was: pytest before any edit (L9), reads (L12–18), plan (L21), edits (L24, L27), pytest (L30), test edits (L39, L42), final pytest (L46).
- **Failure it prevents:** Editing code the model hasn't read, and declaring "done" without running anything.

#### Section: Tool Usage — response and editing rules (tool usage), L192–198
> "**File Editing Collisions:** Do NOT make multiple calls to the `replace` tool for the SAME file in a single turn."
> "**Post-Edit Response Rules:** 1. After an edit tool execution (e.g. `replace`, `write_file`), you MUST ALWAYS generate a user-facing text response summarizing: What changes were made …"
- **Behavior it produces:** Parallel calls for independent work, sequential calls for edits to the same file. `[OBSERVED]`
  - Reads were batched: 3 files in call #3 (L12–14), 2 in call #4 (L17–18).
  - Each `replace` was the only edit in its turn (calls #6, #7, #11, #12).
  - The agent **ignored** the post-edit text rule: no text after any of the 4 edits (stream has no assistant messages).
- **Failure it prevents:**
  - Two `replace` calls on the same file racing: the second `old_string` no longer matches once the first edit lands.
  - Silent edits the user cannot follow. That second rule failed here, `[INFERRED]` probably because the small flash-lite model weighs "minimal output" more heavily.

#### Section: Context Efficiency, L10–29
> "The agent passes the full history with each subsequent message. The larger context is early in the session, the more expensive each subsequent turn is."
> "Unnecessary turns are generally more expensive than other types of wasted context."
- **Behavior it produces:** Parallel reads and small, scoped tool outputs. `[OBSERVED]` Five files were read in 2 turns instead of 5.
- **Where it was not followed:** The agent re-read `tests/test_cart.py` and `tests/test_pricing.py` in calls #9–#10 (L33, L36). Both were already in context from call #4. That cost 2 extra turns, which is the exact waste this section names. `[OBSERVED]`
- **Failure it prevents:** Runaway token cost and latency. `[OBSERVED]` By the last call, every request re-sent 25k tokens (call #13).

#### Section: Engineering Standards — Contextual Precedence and Testing, L41, L49
> "**Contextual Precedence:** Instructions found in `GEMINI.md` files are foundational mandates. They take absolute precedence over the general workflows and tool defaults described in this system prompt."
> "**Testing:** ALWAYS search for and update related tests after making a code change. You must add a new test case …"
- **Behavior it produces:** Project rules override the generic prompt, and every change ships with tests.
  - `[OBSERVED]` The agent kept money in integer cents (`599`, `5000`) and put the rule in `pricing.py`, both as `GEMINI.md` says (session commit, `pricing.py` hunk).
  - `[OBSERVED]` It added 5 tests (session commit, `test_cart.py` and `test_pricing.py` hunks).
- **Failure it prevents:**
  - A generic default (e.g. floats for money) beating a project convention.
  - Features merged without tests.

#### Section: Git Repository, L224, L238
> "**NEVER** stage or commit your changes, unless you are explicitly instructed to commit."
- **Behavior it produces:** The agent checked `git status` and stopped (stream, tool #19). It did not commit, so the agent's work became its own commit when I made it (`d05bd73`).
- **Failure it prevents:** Agents committing half-done or unreviewed work, or pushing to a remote.

### Context injection (`GEMINI.md`)
**`GEMINI.md` is not in the system prompt.** `[OBSERVED]` Neither `prompts/system.md` nor `submission/session_system.md` contains its text (e.g. "Never use floats for stored amounts"). The system prompt only refers to it (L41, L202: "The current contents of all loaded `GEMINI.md` files … are already in your context").

**It is injected into the first user message.** `[OBSERVED]` In the raw telemetry, the `gemini_cli.api_request` for call #1 has a `request_text` that begins:
```
[{"role":"user","parts":[{"text":"<session_context>\nThis is the Gemini CLI. We are setting up the context for our chat.\n…
- **Directory Structure:** … ├───GEMINI.md …
<loaded_context>
<project_context>
--- Context from: C:/Users/[REDACTED]/…/work/run/GEMINI.md ---
# Project context
- Python 3.10+ library; no third-party runtime dependencies.
- All money is integer **cents**. Never use floats for stored amounts.
…
```
The same text is in `gen_ai.input.messages` of every later call, never in `gen_ai.system_instructions`.

**Source** (v0.64.0):
- `packages/core/src/config/config.ts` L2614–2634: `getSessionMemory()` ("Returns Tier 2 memory (extension + project) for injection into the first user message"). It wraps the project memory in `<project_context>` inside `<loaded_context>`.
- `packages/core/src/utils/environmentContext.ts` L69–77: builds the surrounding `<session_context>` block with the date, OS, workspace and directory tree.

`[INFERRED]` Keeping project context out of the system prompt keeps the system prompt identical across projects. Identical prompts can be cached, and `cached=8121` already shows up on call #2 (L8).

---

## Part III — Tool design

### Inventory
`/tools` is a UI command and doesn't run in headless mode; sending `-p "/tools"` just went to the model. So this list comes from the v0.64.0 registration code (`packages/core/src/config/config.ts` L4008–4123) and the names in `definitions/base-declarations.ts` and `tool-names.ts`. Conditional tools are marked. "Used" counts come from the timeline Summary plus the stream (tools #19–#20).

| Category | Tools | Used in session (count) |
|---|---|---|
| File | `read_file`, `write_file`, `replace`, `list_directory`, `read_many_files` | `read_file` ×8, `replace` ×4 |
| Search | `grep_search` (ripgrep version or the JS fallback; here the fallback, log event `ripgrep_fallback`), `glob` | 0 |
| Shell | `run_shell_command`, `list_background_processes`, `read_background_output` | `run_shell_command` ×4 (3 × pytest, 1 × `git status`) |
| Web | `google_web_search`, `web_fetch` | 0 |
| Planning and narration | `update_topic`, `enter_plan_mode` / `exit_plan_mode` (if plan mode is enabled; the prompt mentions it), `write_todos` (only if `useWriteTodos`), `tracker_*` (only if the tracker is enabled) | `update_topic` ×4 |
| Delegation | `invoke_agent` (sub-agents `codebase_investigator`, `cli_help`, `generalist`), `activate_skill` | 0 |
| Memory / other | `ask_user` (excluded in headless mode, CLI `config.ts` L803), `get_internal_docs`, `read_mcp_resource`, `list_mcp_resources`, `complete_task` (sub-agents only) | 0 |

### Tool A: `replace` (file edit)
- **Source file:**
  - Name and parameters: `definitions/base-declarations.ts` L65–69.
  - What the model sees: `definitions/model-family-sets/gemini-3.ts` L356–394.
  - What runs: `tools/edit.ts` (`EditToolInvocation` L460, `validateToolParamValues` L1176).
- **Schema:**
  ```
  replace {
    file_path:      string   (required)  "The path to the file to modify."
    instruction:    string   (required)  "A clear, semantic instruction for the code change …"
    old_string:     string   (required)  "The exact literal text to replace, unescaped. …"
    new_string:     string   (required)  "The exact literal text to replace `old_string` with, unescaped. …"
    allow_multiple: boolean  (optional)  "If true … replace all occurrences … If false (default), it will only succeed if exactly one occurrence is found."
  }
  ```
- **Why each parameter:**
  - `file_path` — which file to change. Relative paths are resolved and checked against the workspace (`validateToolParamValues` → `correctPath`).
  - `old_string` — the anchor. Edits are located by content, not by position.
  - `new_string` — the full replacement text, which keeps the diff small and reviewable.
  - `instruction` — the intent in plain words. It is shown to the user, and if the exact match fails, `FixLLMEditWithInstruction` (`edit.ts` L49) uses it to repair the edit. `[OBSERVED]` The agent filled it in, e.g. "Fix add_item to increment quantity instead of overwriting." (L24).
  - `allow_multiple` — makes "replace all" an explicit choice. Otherwise an ambiguous match fails instead of silently editing the wrong place.
- **Description line that corrects a model mistake:** > "Do not use omission placeholders like '(rest of methods ...)', '...', or 'unchanged code'; provide exact literal code." **Mistake:** LLMs often abbreviate unchanged code with `...` or "rest unchanged". Written literally into a file, that deletes real code.
- **Deliberately does not:** Edit by line numbers, or apply an ambiguous match.
  - `edit.ts` L372–375 returns `Failed to edit, Expected 1 occurrence but found N … set 'allow_multiple' to true` instead of picking one.
  - With 0 matches it refuses and tells the model to re-read the file (L369).
  - It also never leaves the workspace (path validation in `validateToolParamValues`).
  - **Why:** A wrong-but-plausible edit is worse than a failed one; a failure costs one turn and is visible.

### Tool B: `run_shell_command`
- **Source file:**
  - Name and parameters: `definitions/base-declarations.ts` L56–58.
  - What the model sees: `definitions/dynamic-declaration-helpers.ts` (`getShellToolDescription` L36, `getShellDeclaration` L85). Both model families call the same helper.
  - What runs: `tools/shell.ts` (`ShellToolInvocation` L102, `validateToolParamValues` L1220).
- **Schema** (as generated on Windows, sandboxing off):
  ```
  run_shell_command {
    command:       string   (required)  "Exact command to execute as `powershell.exe -NoProfile -Command <command>`"
    description:   string   (optional)  "Brief description of the command for the user. … No line breaks."
    dir_path:      string   (optional)  "(OPTIONAL) The path of the directory to run the command in. … Must be a directory within the workspace"
    is_background: boolean  (optional)  "Set to true if this command should be run in the background …"
    delay_ms:      integer  (optional)  "Delay in milliseconds to wait after starting the process in the background …"
    [additional_permissions: object — only when tool sandboxing is enabled]
  }
  ```
- **Why each parameter:**
  - `command` — the only required field. The description names the exact interpreter (`powershell.exe` on Windows, `bash -c` elsewhere) so the model writes the right syntax.
  - `description` — the one-line text in the approval dialog; it pairs with the system-prompt rule to explain modifying commands.
  - `dir_path` — run somewhere other than the root without `cd … &&` chains. It is validated against the workspace (L1227–1232).
  - `is_background` and `delay_ms` — start servers or watchers and still get some early output back.
  - `additional_permissions` — lets the model ask for more only after a sandbox denial.
- **Description line that corrects a model mistake:** > "To run a command in the background, set the `is_background` parameter to true. Do NOT use PowerShell background constructs." (on Linux/macOS: "Do NOT use `&` to background commands."). **Mistake:** Models background processes with `&` or `Start-Job`. The harness then loses track of the process: no PID, no output, and it may hang or orphan it.
- **Deliberately does not:** Allow command substitution.
  - `shell.ts` L528–538 blocks any command containing `$()`, backticks, `<()` or `>()`, plus PowerShell `@()` and `$()`: "Command injection detected … the command was blocked."
  - **Why:** Approval policy checks the *root commands* (`getCommandRoots`, L296). Substitution would hide a second command inside an approved one, e.g. `echo $(rm -rf …)`.
  - It also won't run outside the workspace (`PATH_NOT_IN_WORKSPACE`, L574–588).
  - It kills commands that go silent, via an inactivity timeout (L554–660) instead of a fixed wall-clock limit.

### Why old/new string edits?
Two reasons:
1. **Robust to drift.** Line numbers go stale as soon as an earlier edit (or the user) shifts the file. A literal `old_string` still finds the right spot, or fails loudly with "0 occurrences" or "expected 1, found N" (`edit.ts` L366–375).
2. **Cheap and reviewable.**
   - Rewriting the whole file costs output tokens proportional to its size and risks dropping code (hence the "no `...` placeholders" rule).
   - An old/new pair is tiny, and it *is* the diff the user approves.
   - The gemini-3 description says so directly: it "minimizes token usage, simplifies code reviews, and avoids accidental deletions".

**Trace moment** `[OBSERVED]`:
- All 4 `replace` calls matched exactly. Telemetry logged four `gemini_cli.edit_strategy` events with `strategy: "exact"` (23:48:44, :46, :55, :57), so the `flexible`, `regex` and `fuzzy` fallbacks (`edit.ts` L328–347) were never needed.
- It mattered most in call #11 (L39). The agent replaced three whole test functions in one `old_string` block in `test_cart.py`. It had re-read the file just before (#9, L33), so the literal text matched on the first try.

`[INFERRED]` With line numbers, that edit would have been fragile, because the earlier edits in `cart.py` and `pricing.py` happened in the same session and an older read of `test_cart.py` was already in context.

### Per-model tool descriptions
**Compared:** `replace` in `gemini-3.ts` L356 vs `default-legacy.ts` L349. (`run_shell_command` is identical in both; both call `getShellDeclaration`.)

What the legacy version has that gemini-3 drops:
- "Always use the read_file tool to examine the file's current content before attempting a text replacement."
- A 5-point "Expectation for required parameters" list, including "Include at least 3 lines of context BEFORE and AFTER the target text" and "NEVER escape `old_string` or `new_string`".
- A long `instruction` description with WHY/WHERE/WHAT/outcome questions and GOOD/BAD examples.
- "Prefer to break down complex and long changes into multiple smaller atomic calls".
- `old_string` wording: legacy says "*preferably* unescaped" plus the 3-line rule; gemini-3 just says "unescaped".

What gemini-3 adds: the reason for the tool ("preferred for surgical edits … minimizes token usage, simplifies code reviews, and avoids accidental deletions").

**Why describe the same tool differently?**
- `[INFERRED]` Older models made the mistakes the legacy text lists: escaping strings, too little context, vague instructions, editing without reading first. They needed explicit rules and examples.
- Newer models follow a short description, and every description token is paid on *every* call. The ~10k-token first request (call #1, `input=10367`) is mostly system prompt plus tool schemas.
- So a CLI tunes descriptions per model family: as much guidance as that model needs, and no more.

---

## Part IV — Behavioral analysis

### 1. The loop
```
user → call#1 → [update_topic ∥ read_file TASK.md]
     → call#2 → run_shell_command "python -m pytest"   (2 failed / 12 passed)
     → call#3 → [read_file cart.py ∥ catalog.py ∥ pricing.py]
     → call#4 → [read_file test_cart.py ∥ test_pricing.py]
     → call#5 → update_topic "Implementing Cart Fixes and Shipping Rules"   (3,152 thinking tokens)
     → call#6 → replace cart.py
     → call#7 → replace pricing.py
     → call#8 → run_shell_command "python -m pytest"   (3 failed / 11 passed)
     → call#9 → read_file test_cart.py
     → call#10 → read_file test_pricing.py
     → call#11 → replace test_cart.py
     → call#12 → replace test_pricing.py
     → call#13 → [update_topic "Validating Test Suite" ∥ run_shell_command "python -m pytest -v"]  (19 passed)
     → request → 429 RESOURCE_EXHAUSTED → CLI waits ~60 s and retries
     → call#14 → run_shell_command "git status"
     → call#15 → update_topic "Task Completed"
     → request → 403 PERMISSION_DENIED → CLI exits with an error
```
`[OBSERVED]` Calls #1–#13 and the 429: timeline L1–48. Calls #14–#15 and the 403: `session_stream.jsonl` (tool events at 23:50:06 and 23:50:09, result `error` at 23:50:10).

**What ended it:** **An API error, not the agent and not me.**
- The agent had finished: its last tool call was a "Task Completed" `update_topic` recapping all three tasks.
- `[INFERRED]` The 403 hit the follow-up request that would have returned the final text answer. Without the error, the loop would have ended when the model replied with no tool call.
- `[INFERRED]` The 429 came from the free tier's 250,000 input-tokens-per-minute limit. The summed input over the 35 s from call #1 to #13 is 230,956 (timeline Summary), and the next request pushed it over.

### 2. Context growth
`input_token_count` and `cached_content_token_count` per call, from `session_calls.csv`:

| call | input | cached | uncached | bar (input, 1 █ ≈ 1k) |
|---|---|---|---|---|
| 1 | 10,367 | 0 | 10,367 | ██████████ |
| 2 | 11,023 | 8,121 | 2,902 | ███████████ |
| 3 | 12,011 | 8,120 | 3,891 | ████████████ |
| 4 | 13,058 | 10,137 | 2,921 | █████████████ |
| 5 | 13,824 | 10,130 | 3,694 | █████████████▊ |
| 6 | 17,350 | 12,175 | 5,175 | █████████████████▎ |
| 7 | 18,513 | 16,234 | 2,279 | ██████████████████▌ |
| 8 | 19,942 | 16,237 | 3,705 | ███████████████████▉ |
| 9 | 20,807 | 18,265 | 2,542 | ████████████████████▊ |
| 10 | 22,046 | 18,266 | 3,780 | ██████████████████████ |
| 11 | 22,465 | 20,290 | 2,175 | ██████████████████████▍ |
| 12 | 24,303 | 20,296 | 4,007 | ████████████████████████▎ |
| 13 | 25,247 | 22,324 | 2,923 | █████████████████████████▏ |

**Why it grows:** Each call re-sends the whole history: system prompt, tool schemas, the `<session_context>` message, then every earlier call and tool result. `[OBSERVED]` The prompt says so itself: "The agent passes the full history with each subsequent message" (system.md L16).
- The baseline is about 10.4k tokens before any work (call #1).
- Each turn adds its tool outputs. Pytest output and file contents are the big ones, e.g. #8 → #9 adds about 0.9k after the failing pytest output.
- The biggest jump, +3.5k from #5 to #6, follows call #5's 3,152 thinking tokens. `[INFERRED]` The reasoning (or its signature) and the long `update_topic` plan are carried forward in history.
- The re-reads of the test files (#9–#10) added about 1.6k tokens of context that was already there.

**Caching:** `cached_content_token_count` is the part of the input the API served from its prompt cache.
- `[OBSERVED]` 0 on call #1, then about 8k from call #2 onward. It grows to 22.3k (88% of the input) by call #13.
- Because the history only ever grows by appending, each request starts with the previous one, so the cache covers almost everything except the newest tool results. That's the "uncached" column: only 2–5k new tokens per call.
- **Why it matters:**
  - Cached input is billed at a fraction of the normal price, and it skips re-processing the prefix, which lowers time to first token. `[INFERRED]` Most calls took about 0.8–2.5 s despite a 20k+ context.
  - Cost grows roughly with the *sum* of inputs. That sum was 230,956 for 13 calls.
- **Caching didn't help with the quota.** `[OBSERVED]` The free-tier per-minute limit counts *all* input tokens, cached or not, so this session ran into the 250k/min ceiling anyway (L48).

### 3. Planning
**How it planned:** Only with `update_topic`.
- `[OBSERVED]` No `write_todos`, no `enter_plan_mode`, and no plain-text plan, even though the prompt asked to "First write out your plan". There are no assistant text messages in the stream.
- It called `update_topic` 4 times, as the "Topic Updates" section (system.md L52–64) prescribes:
  - first turn: "Reading Task Requirements" (call #1);
  - the plan, at the research → implementation switch: "Implementing Cart Fixes and Shipping Rules" (call #5);
  - "Validating Test Suite" (call #13);
  - the last-turn recap: "Task Completed" (call #15).
- That follows "Always call update_topic in your first turn", "also call update_topic in your last turn" and "3 or more times".
- `[INFERRED]` Plan mode wasn't used because L138 says "Do NOT use Plan Mode for straightforward bug fixes".

**Did the plan match what it did?** Mostly yes. The call #5 summary lists five steps, and the edits (L24, L27, L39, L42) follow them in order.

**Where it departed:**
1. **No topic update after the surprise failure.** The plan said "update existing test assertions … to include shipping". But the agent first ran pytest after editing the code (L30), hit 3 failures it had predicted, and only then re-read and edited the tests (L33–39). L61 asks for `update_topic` "when you experience an unexpected event (e.g., a test failure…)", and none was published there. `[OBSERVED]`
2. **No new reproduction tests for the bugs.** L46 says "For bug fixes, you must empirically reproduce the failure with a new test case". The agent relied on the existing failing tests instead. That is reasonable here, since TASK.md says the existing tests describe the intended behavior. `[OBSERVED]` The session commit adds no `add_item` or discount-order test.
3. **Where the shipping rule is used.** TASK.md says to "use it from `Cart.total()`". The agent called `calculate_shipping` from `final_total()` in `pricing.py`, which `Cart.total()` calls. `Cart.total()` itself is unchanged (session commit, `pricing.py` hunk; `cart.py` hunk only touches `add_item`). `[OBSERVED]` The behavior is the same, `[INFERRED]` but it is not literally what the task said.

### 4. Error recovery
**The first failure** is the reproduction run (L9), expected by design: `2 failed` (`test_add_same_item_twice_increments_quantity`, `test_fixed_discount_applied_before_tax`).

**The first failure caused by the agent's own changes** is the pytest run after its code edits (call #8 → L30; full output in the stream, tool #12):
> ```
> tests\test_cart.py ......FFF
> >       assert cart.total() == 2160  # 2000 + 8% tax
> E       assert 2759 == 2160
> ```
> (also `2932 == 2333` and the `TENOFF` total, now `3839`, against the old `3240`)

**What it did next** `[OBSERVED]`:
1. Thought for 711 tokens (call #9; the second-highest after #5).
2. Re-read `tests/test_cart.py` (L33) and `tests/test_pricing.py` (L36).
3. Changed only the three expected `Cart.total()` values, each +599 cents, with a comment giving the reason (L39).
4. Added the new shipping tests (L42).
5. Re-ran the full suite: 19 passed (L46).

**Was the recovery good?** Yes on substance.
- The old totals were wrong only because shipping now exists, which TASK.md explicitly allows the agent to update.
- It fixed the expectations rather than bending the code.
- Each new value is the old one + 599: 2160 → 2759, 2333 → 2932, 3240 → 3839. The old values were right for a cart without shipping; for example, 3240 = (4000 − 1000) × 1.08 is the corrected discount-before-tax total. `[INFERRED]` The comments break each total into tax plus 599 shipping, which suggests the agent worked out the new values rather than pasting whatever pytest printed.
- It was not efficient: the two re-reads repeated files already in context (call #4).

### 5. The tests
**Yes, it edited existing tests: three expected values in `tests/test_cart.py`.** From the session commit `d05bd73`:
```diff
-    assert cart.total() == 2160  # 2000 + 8% tax
+    assert cart.total() == 2759  # 2000 + 8% tax + 599 cents shipping (< $50 threshold)
 ...
-    assert cart.total() == 2333  # (2400 - 10%) + 8% tax
+    assert cart.total() == 2932  # (2400 - 10%) + 8% tax + 599 cents shipping (< $50 threshold)
 ...
-    assert cart.total() == 3240  # (4000 - 1000) + 8% tax
+    assert cart.total() == 3839  # (4000 - 1000) + 8% tax + 599 cents shipping (< $50 threshold)
```
**Allowed?** Yes.
- TASK.md step 2 says: "Some existing tests check `Cart.total()` with values from before shipping existed. You may update those expected values — and only those — and note why in a comment."
- All three are `Cart.total()` checks. Only the number changed, and each has a comment explaining the shipping fee. `[OBSERVED]`
- `test_fixed_discount_applied_before_tax` was also one of the step-1 tests that must not be edited "for this step". The agent did not touch it during step 1: it fixed the code, and the test's old value 3240 became correct before shipping was added (call #8 output shows `3839`, not `1160`). It changed the number only for the step-2 shipping reason. `[OBSERVED]`

**Other test changes** were additions only (TASK.md step 3):
- `test_free_shipping_threshold` in `test_cart.py`;
- four `calculate_shipping` tests in `test_pricing.py`;
- a changed import line in `test_pricing.py` to import `calculate_shipping`.

**Gap in the new tests** `[OBSERVED]`: every shipping test passes the same value for `subtotal_cents` and `discounted_cents`. None checks the rule's key phrase, "*after discount*".
- I checked one case by hand: TEE×2 + CAP = 5500, with `TENOFF` → 4500 after discount → pays 599 → total `5459`.
- The code gets it right, but no test would catch a regression to checking the pre-discount subtotal.
- A $3 sticker with `TENOFF` discounts to $0 and still pays 599 shipping. That is defensible, since "Empty cart" means no items, but it is untested and undocumented.

### 6. Models
**Model:** `[OBSERVED]` Every row of `session_calls.csv` and every RESPONSE line in the timeline says `model=gemini-3.5-flash-lite`. The routing event confirms the router was bypassed: `decision_source: "agent-router/override"`, reasoning "Routing bypassed by forced model directive. Using: gemini-3.5-flash-lite".

**Most "thinking"** (`thoughts_token_count`):
| call | thoughts | what the agent was deciding |
|---|---|---|
| #5 | **3,152** | It had just read every source and test file (#3–#4) and seen the 2 failures. Its output was the whole plan (`update_topic`, L21). It was working out both root causes (overwrite in `add_item`; tax applied before discount in `final_total`), where shipping goes, and that 3 old totals would change. `[OBSERVED]` output → `[INFERRED]` content |
| #9 | 711 | Right after the post-fix pytest showed 3 failures (L30). Deciding whether those failures meant the code was wrong or the expected values were out of date, and whether TASK.md allows editing them. It then chose to re-read the tests. |
| #6 | 563 | Writing the first edit (`add_item`) and committing to an order for the edits. |
| #11 | 552 | Writing the multi-function test replacement with the new numbers (2759/2932/3839/6480), which takes arithmetic. |

Mechanical turns (reads, re-runs) used 15–65 thinking tokens (#3, #4, #8, #12, #13). `[OBSERVED]` The model spends its reasoning where a decision is made, not on tool plumbing.

**Why split router and worker** (`flash-lite` routes, `3.8-flash` works) `[INFERRED]`:
- Most turns in an agent loop are easy: read this file, run tests, pick the next tool. A small model answers them fast and cheaply.
- A cheap classifier (the log shows `enable_numerical_routing: true`, `classifier_threshold: "90"`) can send only the hard requests to the bigger model. You get big-model quality where it matters without paying big-model latency and price on every one of the ~15 calls.
- It also spreads load across two per-model free-tier quotas, which matters given this session hit a per-minute limit.

**If the whole session ran on a bigger model** `[INFERRED]`:
- **Slower and pricier:** higher per-token cost on the same ~231k input tokens, and longer latency per call. Call #5 alone took 8.5 s on flash-lite.
- **On the free tier, stricter limits:** the assignment notes the default model allows only 20 requests per day, which this session's ~17 requests would nearly use up.
- **Quality:** probably more efficient rather than more correct. Flash-lite already reached 19/19, but it wasted turns (two redundant re-reads) and broke two prompt rules: no text after edits, and no topic update after the test failure.
- **What I'd expect from a bigger model:** fewer, larger turns; a plain-text plan as asked; a test for the "after discount" threshold edge case (Part IV.5).
