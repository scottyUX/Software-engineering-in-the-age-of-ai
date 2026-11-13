# Week 3 Writeup — Inside a Coding Agent

**Name:** OMAR DIAB (220911379)
**Gemini CLI version (`gemini --version`):** 0.64.0 (banner: `Gemini CLI v0.64.0`)
**OS / shell:** macOS (Darwin 24.6) + zsh; the agent's shell tool runs `bash -c <command>`
**Model(s) seen in trace:** `gemini-3.5-flash-lite` on all 11 calls
**Session commit:** `977e580`

> Evidence tags: `[OBSERVED]` = cite a timeline line, call number, or diff hunk.
> `[INFERRED]` = say what you're reasoning from.

> **Setup notes.** On first launch, Gemini CLI updated itself in the background, first to 0.66.0 and
> then to 0.68.0. I set `general.enableAutoUpdate: false` in `~/.gemini/settings.json`, reinstalled
> 0.64.0, and re-exported `system.md` and recorded the session only after the banner showed
> `v0.64.0`. The session was run through a pseudo-terminal by my coding agent (Claude Code), which
> typed the exact prompt and answered each confirmation with **Allow once** after reading it.
> Nothing else was typed.

---

## Part I — Session

**Narrative (one paragraph):** The agent first read `TASK.md` (call #1). In one turn (call #2) it
ran `python -m pytest` and read `cart.py`, `pricing.py`, `test_cart.py` and `test_pricing.py` in
parallel, which reproduced the 2 failing tests. After the longest "thinking" step (call #3, 5,314
thought tokens), it fixed `Cart.add_item` to add to the existing quantity (call #4). It then rewrote
`final_total` to discount before tax and added `calculate_shipping` in one `replace` (call #5). The
second test run failed 3 tests whose expected totals predated shipping (call #6). It updated those 3
expected values with comments and added 3 shipping tests (call #7). It ran the suite again, which
passed with 17 tests (call #8), reviewed `git status && git diff` without committing (call #9), and
ended with a summary (calls #10–#11).

| Metric | Value |
|---|---|
| User prompts | 1 |
| Model calls | 11 (0 errors) |
| Tool calls (failed) | 19 (0) — see note below |
| Final `pytest` result | `17 passed in 0.01s` (run by me after `/quit`) |
| Did you step in? When / what? | No. Only the 7 confirmation prompts were answered, each with "Allow once". |

**Note on the tool-call count.** `session_timeline.txt` reports 17 tool calls, but the raw log has
19 `gemini_cli.tool_call` events. The extra 2 are `read_file` on `tests/test_cart.py` and
`tests/test_pricing.py`. They ran in the same second as the other reads of call #2. The summarizer
de-duplicates on `(name, event.timestamp, function_name, prompt_id)`
(`tools/summarize_log.py` line 144), so same-name calls with the same timestamp collapse into one.
Both reads appear as `functionCall`s in the request history sent with call #3. The 19 calls are:
`update_topic` 7, `read_file` 5, `run_shell_command` 4, `replace` 3.

---

## Part II — System prompt annotation

### Outline
1. Identity and mode (line 1) — "You are Gemini CLI … operating in **Default** mode."
2. Core Mandates: Security & System Integrity (5–8) — secrets, no commits, untrusted tool output.
3. Context Efficiency (10–38) — how to spend tokens and turns: parallel reads, scoped searches.
4. Engineering Standards (40–51) — `GEMINI.md` precedence, conventions, testing, directive vs inquiry.
5. Topic Updates (52–67) — when and how to narrate with `update_topic`, plus no-revert and skill rules.
6. Available Sub-Agents (69–106) — delegation policy and the three sub-agents.
7. Available Agent Skills (108–128) — installed skills and how to activate them.
8. Hook Context (130–135) — hook output is data, not instructions.
9. Primary Workflows: Development Lifecycle (137–154) — Research → Strategy → Execution (Plan → Act → Validate).
10. New Applications (156–170) — default stacks and mandatory plan mode for new apps.
11. Tone and Style (172–184) — brief, direct CLI voice.
12. Security and Safety Rules (186–188) — explain modifying commands; no `ask_user` for permission.
13. Tool Usage (190–219) — response rules, parallelism, edit collisions, background, memory files.
14. Interaction Details (221–223) — `/help` and `/bug`.
15. Git Repository (225–243) — never stage/commit/push unless asked; commit procedure.

### Annotations (≥6)
#### Section: Tone and Style (tone and verbosity)
> "**Minimal Output:** Aim for fewer than 3 lines of text output (excluding tool use/code generation) per response whenever practical." (line 179)
> "**No Chitchat:** Avoid conversational filler, preambles ("Okay, I will now...")…" (line 180)
- **Behavior it produces:** The model narrates through tools instead of prose. `[OBSERVED]` In the
  request history sent with call #11, none of the 10 earlier model turns contains a text part; they
  only contain function calls. The only prose is the final summary from call #11.
- **Failure it prevents:** A chatty agent that fills the terminal with "Sure! Let me…" and repeats
  itself. That wastes output tokens and buries the information the user actually needs.

#### Section: Git Repository + Core Mandates (when not to act / confirm)
> "**NEVER** stage or commit your changes, unless you are explicitly instructed to commit." (line 228)
> "You should not ask permission to use the tool; the user will be presented with a confirmation dialogue upon use" (line 187)
- **Behavior it produces:** The agent may inspect git but leaves committing to the human, and it
  relies on the CLI's confirmation dialog instead of asking in chat. `[OBSERVED]` It ran
  `git status && git diff` (timeline 12:47:07) but made no commit, and it never called `ask_user`.
  The 7 approvals all came through the built-in dialog.
- **Failure it prevents:** Unwanted, irreversible repository changes, such as a commit or push the
  user did not ask for. Also double confirmation, where the model asks "may I?" and then the dialog
  asks again.

#### Section: Development Lifecycle (workflow)
> "Operate using a **Research -> Strategy -> Execution** lifecycle. For the Execution phase, resolve each sub-task through an iterative **Plan -> Act -> Validate** cycle." (line 140)
> "**Prioritize empirical reproduction of reported issues to confirm the failure state.**" (line 142)
- **Behavior it produces:** It reproduces first, changes second and verifies last. `[OBSERVED]`
  Call #2 ran pytest before any edit (`2 failed, 12 passed`). The edits came in calls #4, #5 and #7,
  with validation runs after the code change (call #6) and after the test change (call #8).
- **Failure it prevents:** "Fixing" a bug the agent never confirmed, or declaring success without
  evidence. Line 149 says "Validation is the only path to finality."

#### Section: Tool Usage — Parallelism & Sequencing (tool usage)
> "Execute multiple independent tool calls in parallel when feasible … you MUST set the `wait_for_previous` parameter to `true` on the dependent tool" (line 201)
> "Do NOT make multiple calls to the `replace` tool for the SAME file in a single turn." (line 202)
- **Behavior it produces:** Batched, ordered tool use. `[OBSERVED]` Call #2 issued 6 tools in one
  turn (1 `update_topic`, 1 `run_shell_command`, 4 `read_file`), and every later `update_topic`
  before a test run set `"wait_for_previous": true`. The 3 `replace` calls each came in their own
  turn (calls #4, #5, #7).
- **Failure it prevents:** Wasted turns from reading files one by one, and races where two edits to
  the same file, or a test run during an edit, see stale content.

#### Section: Topic Updates
> "Always call update_topic in your first turn." … "For tasks taking multiple turns, also call update_topic in your last turn to recap what was done." (lines 56–57)
- **Behavior it produces:** A visible, phase-by-phase progress log. `[OBSERVED]` 7 `update_topic`
  calls. The first comes in call #1 ("Reading Task Requirements") and the last in call #10 ("Task
  Completed").
- **Failure it prevents:** The user losing track of what a long, autonomous session is doing. This
  matters most when confirmations are the only interaction.

#### Section: Engineering Standards — Contextual Precedence
> "Instructions found in `GEMINI.md` files are foundational mandates. They take absolute precedence over the general workflows and tool defaults described in this system prompt." (line 41)
- **Behavior it produces:** Project rules override the generic defaults. `[OBSERVED]` The agent used
  integer cents (`SHIPPING_FEE = 599`, `FREE_SHIPPING_THRESHOLD = 5000`) and put the rule in
  `shopcart/pricing.py`, as `GEMINI.md` says. `[INFERRED]` It ran `python -m pytest` without the
  `-q` that `GEMINI.md` specifies, so precedence did not guarantee every detail.
- **Failure it prevents:** A generic agent ignoring a team's conventions, such as floats for money
  or logic in the wrong module, because its built-in defaults differ.

#### Section: Context Efficiency
> "The agent passes the full history with each subsequent message. The larger context is early in the session, the more expensive each subsequent turn is." (line 16)
- **Behavior it produces:** Fewer, larger turns with small reads. `[OBSERVED]` The whole task took
  11 calls, and all files were read once each, in a single turn.
- **Failure it prevents:** Runaway cost and latency from many small turns, each of which resends
  the entire history (see Part IV §2).

### Context injection (`GEMINI.md`)
`GEMINI.md`'s content is **not** in the exported `system.md`. That file only refers to it, for
example in line 41 and line 206 ("The current contents of all loaded `GEMINI.md` files … are already
in your context"). `[OBSERVED]` The content travels in the **first user-role message** of every
request, not in the system instruction. The `request_text` of each `gemini_cli.api_request` begins:

```text
[{"role":"user","parts":[{"text":"<session_context>
This is the Gemini CLI. We are setting up the context for our chat.
…
<loaded_context>
<project_context>
--- Context from: /Users/[REDACTED]/…/work/run/GEMINI.md ---
# Project context
- Python 3.10+ library; no third-party runtime dependencies.
- All money is integer **cents**. …
```

The phrase "All money is integer" appears 44 times in the raw log: 4 records for each of the 11
requests. It is therefore resent as part of the conversation history on every call.

---

## Part III — Tool design

### Inventory
`/tools` listed 16 built-in tools.

| Category | Tools | Used in session (count) |
|---|---|---|
| File | `read_file`, `write_file`, `replace`, `list_directory` | `read_file` 5, `replace` 3 |
| Search | `glob`, `grep_search` | 0 |
| Shell | `run_shell_command`, `list_background_processes`, `read_background_output` | `run_shell_command` 4 |
| Web | `google_web_search`, `web_fetch` | 0 |
| Planning & narration | `update_topic`, `enter_plan_mode` | `update_topic` 7 |
| Delegation | `invoke_agent`, `activate_skill` | 0 |
| Other | `ask_user` | 0 |

### Tool A: `replace` (file edit)
- **Source file:** name and parameters in `definitions/base-declarations.ts` L64–69; description and
  schema in `definitions/model-family-sets/gemini-3.ts` L356; behavior in `edit.ts`
  (`EditToolInvocation` L460, `validateToolParamValues` L1176). The schema below matches the one
  the CLI sent in the session.
- **Schema:**
  ```
  file_path       string   required
  instruction     string   required
  old_string      string   required
  new_string      string   required
  allow_multiple  boolean  optional (default false)
  ```
- **Why each parameter:**
  - `file_path` names the target; it is resolved and checked against the workspace.
  - `old_string` anchors the edit to exact text that must occur once.
  - `new_string` is the literal replacement.
  - `instruction` states the intent. If `old_string` doesn't match, `edit.ts` passes it to
    `FixLLMEditWithInstruction` (L588) to try to repair the edit. It is also what the user sees.
  - `allow_multiple` is an explicit opt-in for bulk replacement.
- **Description line that corrects a model mistake:** > "Do not use omission placeholders like
  '(rest of methods ...)', '...', or 'unchanged code'; provide exact literal code." **Mistake:**
  models abbreviate unchanged code, so writing their output would delete real code.
- **Deliberately does not:** replace more than one match unless asked. With 0 matches it fails with
  "Could not find an exact match for old_string…". With more than 1 match and no `allow_multiple`,
  it fails with "Failed to edit, Expected 1 occurrence but found N…" (`edit.ts` L366–376). It also
  refuses a no-op edit (L377–382). This turns an ambiguous edit into a visible error instead of a
  silent wrong change.

### Tool B: `run_shell_command`
- **Source file:** names in `base-declarations.ts` L56–58; description and schema from
  `getShellToolDescription` (L36) and `getShellDeclaration` (L85) in
  `dynamic-declaration-helpers.ts`; behavior in `shell.ts` (`ShellToolInvocation` L102,
  `validateToolParamValues` L1220).
- **Schema** (macOS variant, as sent in the session):
  ```
  command        string   required  "Exact bash command to execute as `bash -c <command>`"
  description    string   optional
  dir_path       string   optional
  is_background  boolean  optional
  delay_ms       integer  optional
  ```
  `additional_permissions` is added only when tool sandboxing is enabled.
- **Why each parameter:**
  - `command` is the thing to run.
  - `description` is the one-line purpose shown in the confirmation dialog, so the human can decide
    `[OBSERVED]`: each of the 4 shell calls set it.
  - `dir_path` selects a working directory but must stay inside the workspace (validated at L1227–1233).
  - `is_background` starts long-running servers or watchers without blocking the loop.
  - `delay_ms` lets a background process print its first output before control returns.
- **Description line that corrects a model mistake:** > "Pagination: Always disable terminal
  pagination to ensure commands terminate (e.g., use `git --no-pager` …)". **Mistake:** a command
  like `git diff` opens a pager that waits for keyboard input, so the agent hangs.
- **Deliberately does not:** run forever or let the model pick a timeout. An inactivity timer
  (`getShellToolInactivityTimeout`, L554) aborts the command with "Command was automatically
  cancelled because it exceeded the timeout of N minutes without output" (L879). Safety approval is
  also not in the tool's own validation, which only checks for an empty command and the directory
  (L1220–1235). Approval is left to the confirmation dialog and policy layer.

### Why old/new string edits?
1. **Line numbers go stale.** Each edit shifts later lines, and models are poor at counting lines.
   An exact text anchor stays valid no matter what changed above it. `[OBSERVED]` Call #5 inserted
   16 lines above `final_total` in `pricing.py`, and a line-number edit planned before that would
   have targeted the wrong place.
2. **It fails safely and cheaply.** Whole-file rewrites cost output tokens for every unchanged line
   and invite omissions (see the placeholder rule above). An exact-match edit is checked: 0 or 2+
   matches produce an error the model can recover from.

`[OBSERVED]` In this session, every `gemini_cli.edit_strategy` event was `"strategy": "exact"`, and all
3 `replace` calls succeeded the first time. The fallbacks in `edit.ts` (flexible, regex, fuzzy and the
LLM fixer) were never needed, because the agent had read each file in full in call #2.

### Per-model tool descriptions
Compared tool: `replace`, `gemini-3.ts` L356 vs `default-legacy.ts` L349.
- **Legacy adds hand-holding** that the Gemini 3 version removes:
  - "Always use the read_file tool to examine the file's current content before attempting a text replacement."
  - A numbered list of requirements, ending with "NEVER escape `old_string` or `new_string`".
  - "Include at least 3 lines of context BEFORE and AFTER the target text".
  - "Prefer to break down complex and long changes into multiple smaller atomic calls".
  - A long `instruction` description with WHY/WHERE/WHAT guidance and GOOD/BAD examples.
- **Gemini 3 is shorter and adds a reason to prefer the tool:** "This tool is preferred for surgical
  edits to existing files as it minimizes token usage, simplifies code reviews, and avoids accidental
  deletions." It also changes "preferably unescaped" to "unescaped".
- **Why** `[INFERRED]`: tool declarations are resent on every call, so each extra sentence costs
  tokens on all 11 requests. Newer models follow the schema reliably, so the CLI can drop corrective
  text that older models needed after making those mistakes, such as escaped strings, too little
  context or edits without reading. Instead, it nudges the newer model toward the right choice
  between tools. The CLI picks the description set by model family, so each model gets the prompt
  its failure modes require.

---

## Part IV — Behavioral analysis

### 1. The loop
```
user prompt
→ call#1 → update_topic + read_file(TASK.md)
→ call#2 → update_topic + run_shell_command(pytest: 2 failed) + read_file ×4
→ call#3 → update_topic("Implementing Fixes and Shipping Feature")
→ call#4 → replace(cart.py)
→ call#5 → replace(pricing.py)
→ call#6 → update_topic + run_shell_command(pytest: 3 failed)
→ call#7 → replace(tests/test_cart.py)
→ call#8 → update_topic + run_shell_command(pytest: 17 passed)
→ call#9 → update_topic + run_shell_command(git status && git diff)
→ call#10 → update_topic("Task Completed")
→ call#11 → final text summary, no tool call → loop ends
```
What ended it: **the agent decided it was done.** `[OBSERVED]` Response #11 (timeline 12:47:23) has
text and no tool call. No limit was reached, and I did not interrupt.

### 2. Context growth
`[OBSERVED]` from `session_calls.csv`, where █ ≈ 1,000 input tokens:

| Call | Input tokens | Cached | Thoughts | Growth |
|---:|---:|---:|---:|---|
| 1 | 11,545 | 0 | 139 | ████████████ |
| 2 | 12,042 | 8,112 | 386 | ████████████ |
| 3 | 14,732 | 10,124 | 5,314 | ███████████████ |
| 4 | 20,173 | 14,210 | 199 | ████████████████████ |
| 5 | 20,781 | 18,266 | 938 | █████████████████████ |
| 6 | 22,479 | 20,301 | 25 | ██████████████████████ |
| 7 | 23,485 | 20,293 | 1,077 | ███████████████████████ |
| 8 | 25,946 | 0 | 22 | ██████████████████████████ |
| 9 | 26,298 | 22,320 | 63 | ██████████████████████████ |
| 10 | 28,283 | 24,350 | 38 | ████████████████████████████ |
| 11 | 28,398 | 24,342 | 22 | ████████████████████████████ |

**Why it grows** `[OBSERVED]`: each request resends the system prompt, the tool schemas, the
`<session_context>` block and the whole history. The last request held 21 turns. The biggest jumps
follow large tool outputs. From call #3 to #4 (+5,441), the 4 files and the 2,739-character pytest
failure output were added. From call #7 to #8 (+2,461), the 3,291-character failing pytest output
and the test edit were added. Call #1 already starts at 11,545 tokens before any work, which is the
fixed cost of the system prompt, tools and context.

**Caching:** `cached_content_token_count` is the part of the input the API served from its prompt
cache, which is the unchanged prefix from earlier calls. `[OBSERVED]` From call #2 on, 67–89% of the
input was cached. Calls #1 and #8 had 0 cached tokens. `[INFERRED]` Call #1 is a cold start. Call #8
is most likely a cache miss or expiry, since implicit caching is best-effort and the prefix itself
did not change. Caching matters because cached tokens are billed at a reduced rate and skip
re-processing the prefix. As the history grows, almost all of each request is repeated prefix, so
caching keeps the cost and time per call from growing with the full input size.

### 3. Planning
The agent planned only with **`update_topic`**. It did not use `write_todos`, which is not in
v0.64.0's tool list, or `enter_plan_mode`. `[OBSERVED]` The prompt said "First write out your plan",
but no model turn contains plan text: the 10 model turns before the summary contain only function
calls. The "plan" is the series of topic titles. The fullest one is call #3's strategic intent:
"Implement bug fixes in shopcart/cart.py and shopcart/pricing.py, add shipping logic, update existing
test assertions, and add new shipping tests."

This follows the system prompt's "Topic Updates" section, "call update_topic … 3 or more times. Each
corresponds to a distinct phase" (line 60), together with the "Minimal Output" rule (line 179).

**Where it departed from the plan** `[OBSERVED]`:
- The call #3 plan bundled "update existing test assertions" into implementation. The agent only did
  that after a separate test run (call #6, new topic "Running Tests and Updating Assertions")
  revealed which assertions broke.
- It added a "Reviewing Changes" phase (call #9) that was not in the stated plan.
- `[INFERRED]` It skipped the system prompt's own rule for bug fixes: "you must empirically reproduce
  the failure with a new test case or reproduction script" (line 46). It relied on the existing
  failing tests as the reproduction.

### 4. Error recovery
The first failure was the initial test run in call #2:
> `FAILED tests/test_cart.py::test_add_same_item_twice_increments_quantity - AssertionError: assert {'MUG': 2} == {'MUG': 3}`
> `FAILED tests/test_cart.py::test_fixed_discount_applied_before_tax - assert 1160 == 3240`
> `2 failed, 12 passed`

**What it did next** `[OBSERVED]`: it already had the source and tests from the same turn, so it went
straight to targeted fixes. Call #4 changed `self.items[sku] = quantity` to
`self.items.get(sku, 0) + quantity`. Call #5 changed the order to `apply_discount` first, then
`apply_tax`.

The next failure (call #6: `3 failed, 11 passed`, e.g. `assert 3839 == 3240`) was expected, because
shipping now changes old totals. The agent updated exactly those 3 expected values (call #7), and the
next run passed (call #8).

**Was it good?** Yes. It diagnosed from evidence, not guesses, and each failure was fixed in one
edit with no retries. The second failure output also shows that the discount-before-tax fix was
right: 3839 is 3240 + 599 shipping.

### 5. The tests
`[OBSERVED]` Yes. The agent edited 3 existing tests in `tests/test_cart.py` (commit `977e580`):

```diff
-    assert cart.total() == 2160  # 2000 + 8% tax
+    assert cart.total() == 2759  # 2000 + 8% tax + 599 shipping
-    assert cart.total() == 2333  # (2400 - 10%) + 8% tax
+    assert cart.total() == 2932  # ((2400 - 10%) + 8% tax) + 599 shipping
-    assert cart.total() == 3240  # (4000 - 1000) + 8% tax
+    assert cart.total() == 3839  # ((4000 - 1000) + 8% tax) + 599 shipping
```

**Allowed?** Yes. `TASK.md` step 2 allows updating the expected values of `Cart.total()` tests from
before shipping, "and only those", with a comment explaining why.
- `[OBSERVED]` It did not edit tests during step 1. Both originally failing tests were fixed in code
  (calls #4–#5). `test_fixed_discount_applied_before_tax` was changed only after call #6 showed
  `3839`, which is the correct pre-shipping value 3240 plus 599.
- Each new value has a comment showing the added `599 shipping`.

**Coverage** `[OBSERVED]`: it added 3 tests. They cover free shipping at 6000, free shipping after a
10% discount (5400), and paid shipping after a 25% discount (4500).
- `test_shipping_free_at_threshold` actually tests 6000, not the 5000 boundary. No test checks exactly
  4999 or 5000.
- The empty-cart rule is covered only by the existing `test_empty_cart_total_is_zero`.

### 6. Models
`[OBSERVED]` The `model` field is `gemini-3.5-flash-lite` for all 11 responses. The
`gemini_cli.model_routing` event records `"decision_source": "agent-router/override"` and
`"reasoning": "Routing bypassed by forced model directive. Using: gemini-3.5-flash-lite"`, so `-m`
turned the router off.

**Most thinking** (`thoughts_token_count`):

| Call | Thought tokens | What it was deciding |
|---:|---:|---|
| #3 | 5,314 | After seeing both failures and all 4 files at once, how to fix both bugs and design shipping. It produced the "Implementing Fixes and Shipping Feature" plan. |
| #7 | 1,077 | After `3 failed`, whether the failures were bugs or expected shipping changes, and the new totals: 2759, 2932, 3839 and the 3 new tests. |
| #5 | 938 | The structure of `calculate_shipping` and the new `final_total`. |

Bookkeeping turns used only 22–63 thought tokens.

**Why split routing and work across two models** `[INFERRED]`: most turns in an agent loop are
routine, as the 22–63 thought-token turns show. A cheap, fast model can classify each request, and
the expensive model is used only where it matters. This cuts cost and latency and leaves more of the
free-tier quota.

**If the whole session ran on the bigger model** (`gemini-3.8-flash`) `[INFERRED]`:
- **Quality:** probably the same or a little better for this small task, for example a boundary test
  at exactly 5000.
- **Speed:** each call slower.
- **Cost and quota:** higher per token. This session's 11 calls would also use over half of that
  model's free daily limit of 20 requests.
