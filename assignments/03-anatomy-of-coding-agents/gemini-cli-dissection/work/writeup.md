# Week 3 Writeup — Inside a Coding Agent

**Name:** Leen Nofal  
**Gemini CLI version (`gemini --version`):** `0.64.0`  
**OS / shell:** macOS + zsh  
**Model(s) seen in trace:** `gemini-3.5-flash-lite`, `gemini-3.8-flash` (an attempted `gemini-3.1-pro-preview` request failed before a response because the API key was invalid)  
**Session commit:** `182f04fe4963de5cc853003bf42e5ca0f65e7586`

> Evidence tags: `[OBSERVED]` = evidence from the captured timeline/system prompt or the task/diff.  
> `[INFERRED]` = interpretation based on that evidence.

---

## Part I — Session

**Narrative:** [OBSERVED] The session began with an authentication failure, then I re-ran the task and asked Gemini to inspect the assignment/repository and fix the two existing failing tests by changing implementation code. The agent first read `TASK.md`, reproduced the failures with pytest, inspected the cart, pricing, and test files, then used targeted `replace` edits and reran the tests. That first coding pass fixed quantity accumulation and discount-before-tax behavior. I then stepped in with a third user prompt asking Gemini to read `TASK.md` and complete all of it, because the shipping portion was still unfinished. Gemini planned the remaining work, added the shipping rule in `pricing.py`, updated `Cart.total()`, updated only the old total expectations affected by shipping, added shipping tests, and reran the suite. The final run passed all 21 tests. It then reviewed the diff/status. A 429 quota error occurred near the end; the client retried after the indicated delay and completed normally. [OBSERVED: timeline calls #1–#35; tools around calls #2–#15 and #17–#35.]

| Metric | Value |
|---|---|
| User prompts | **3** `[OBSERVED: timeline Summary]` |
| Model calls | **35** (**3 model/API errors**) `[OBSERVED: timeline Summary]` |
| Tool calls (failed) | **43 (0)** `[OBSERVED: timeline Summary]` |
| Final `pytest` result | **21 passed** `[OBSERVED: after call #29 / update_topic]` |
| Did you step in? When / what? | **Yes.** After the first pass fixed the original two bugs but had not completed the shipping feature, I prompted: “Read TASK.md and complete all of it. First write out your plan, then carry it out…” `[OBSERVED: USER entry before call #17]` |

Tool totals from the trace were: `run_shell_command` 15, `update_topic` 11, `read_file` 11, `replace` 5, and `grep_search` 1.

---

## Part II — System prompt annotation

### Outline

The exported system-instruction file contained three variants. Variant 1 is a task-complexity router; Variant 2 is the main Gemini CLI coding-agent prompt; Variant 3 was empty in this capture.

1. **Task routing / complexity scoring** — classifies the request before coding.
2. **Core Mandates** — security, source-control boundaries, and treatment of untrusted data.
3. **Context Efficiency** — reduce unnecessary context and tool turns.
4. **Engineering Standards** — conventions, testing, intent alignment, and scope.
5. **Topic Updates** — keep the user informed during multi-step work.
6. **Sub-agents and Skills** — delegate suitable work and activate specialized guidance.
7. **Hook Context** — treat hook-provided content as read-only informational context.
8. **Primary Workflows** — Research → Strategy → Execution; Plan → Act → Validate.
9. **Operational Guidelines** — tone, safety, tool usage, sequencing, memory/instruction files.
10. **Git Repository** — explicit rules for status/diff/commit/push behavior.

### Annotations

#### Section: Tone and Style (tone and verbosity)
> “Concise & Direct: Adopt a professional, direct, and concise tone suitable for a CLI environment.”

- **Behavior it produces:** [INFERRED] Keeps progress messages short and focused on the action/rationale rather than conversational filler.
- **Failure it prevents:** [INFERRED] Long chatty output that hides the actual coding status or next action.
- **Evidence:** `[OBSERVED: session_system.md, Variant 2, Operational Guidelines → Tone and Style]`

#### Section: Expertise & Intent Alignment (when not to act / confirm)
> “Assume all requests are Inquiries unless they contain an explicit instruction to perform a task.”

- **Behavior it produces:** [INFERRED] Separates questions from directives and avoids editing files when the user only asked for analysis.
- **Failure it prevents:** [INFERRED] Unrequested modifications or scope expansion.
- **Evidence:** `[OBSERVED: session_system.md, Variant 2, Engineering Standards]`

#### Section: Development Lifecycle (workflow)
> “Research -> Strategy -> Execution”

and

> “Plan -> Act -> Validate”

- **Behavior it produces:** [OBSERVED] The trace follows this pattern: read `TASK.md`/tests/code, form a plan/topic, edit, then run pytest and review the diff.
- **Failure it prevents:** [INFERRED] Editing before understanding the repository or declaring success without verification.
- **Evidence:** `[OBSERVED: session_system.md, Primary Workflows; timeline calls #17–#30]`

#### Section: Tool Usage (tool sequencing)
> “Do NOT make multiple calls to the `replace` tool for the SAME file in a single turn.”

- **Behavior it produces:** [INFERRED] Same-file edits are sequenced so each edit sees the latest file state.
- **Failure it prevents:** [INFERRED] Lost updates or edits based on stale content.
- **Evidence:** `[OBSERVED: session_system.md, Tool Usage → File Editing Collisions]`

#### Section: Context Efficiency
> “Prefer using tools like grep_search to identify points of interest instead of reading lots of files individually.”

- **Behavior it produces:** [OBSERVED] During the second phase the agent used `grep_search` on the tests for `total` before changing shipping-related expectations.
- **Failure it prevents:** [INFERRED] Unnecessarily large context and extra read turns.
- **Evidence:** `[OBSERVED: session_system.md, Context Efficiency; timeline tool before call #23]`

#### Section: Testing
> “ALWAYS search for and update related tests after making a code change.”

- **Behavior it produces:** [OBSERVED] The agent added shipping tests and reran the complete suite after implementation.
- **Failure it prevents:** [INFERRED] Shipping behavior being added without regression coverage.
- **Evidence:** `[OBSERVED: session_system.md, Engineering Standards → Testing; timeline calls #27–#29]`

#### Section: Security & Source Control
> “Do not stage or commit changes unless specifically requested by the user.”

- **Behavior it produces:** [OBSERVED] The agent inspected `git status`/`git diff` but did not automatically commit the work.
- **Failure it prevents:** [INFERRED] Unexpected repository history changes or accidental commits.
- **Evidence:** `[OBSERVED: session_system.md, Core Mandates; timeline calls #30–#34]`

#### Section: Validation
> “Validation is the only path to finality.”

- **Behavior it produces:** [OBSERVED] The agent repeatedly used pytest after edits and only concluded after the suite reached 21 passing tests.
- **Failure it prevents:** [INFERRED] Treating an edit as correct merely because it looks plausible.
- **Evidence:** `[OBSERVED: session_system.md, Primary Workflows; timeline call #29 and following update_topic]`

### Context injection (`GEMINI.md`)

[OBSERVED] The workspace `GEMINI.md` says that money is stored as integer cents, pricing rules belong in `shopcart/pricing.py`, cart state belongs in `shopcart/cart.py`, and tests should be run with `python -m pytest -q`. The exported system prompt explicitly says that loaded `GEMINI.md` instructions are “foundational mandates” that take precedence over general workflows. It also states that project `./GEMINI.md` contains team-shared architecture/conventions/workflows and that loaded instruction files are already in context.

[INFERRED] Therefore the project context enters the agent as loaded contextual/project instructions rather than needing the user to paste those rules into each prompt. The resulting implementation is consistent with that context: shipping logic was placed in `pricing.py`, cart integration in `cart.py`, and integer cents were used. The exported prompt proves the precedence/routing rule; the repository `GEMINI.md` provides the concrete project instructions.

---

## Part III — Tool design

### Inventory

| Category | Tools | Used in session (count) |
|---|---|---|
| File | `read_file`, `replace`, plus available `write_file`, `list_directory`, `read_many_files` | `read_file` **11**, `replace` **5** |
| Search | `grep_search`, plus available `glob` | `grep_search` **1** |
| Shell | `run_shell_command` | **15** |
| Web | `google_web_search`, `web_fetch` | **0** |
| Memory / other | `update_topic` and instruction/memory-file mechanisms | `update_topic` **11** |

[OBSERVED] The counts come from `session_timeline.txt`; the broader available-tool inventory comes from Gemini CLI's built-in tool declarations/documentation. Tools listed as available but unused are not counted as session activity.

### Tool A: `replace`

- **Source file:** `packages/core/src/tools/edit.ts` with model-family declarations under `packages/core/src/tools/definitions/model-family-sets/`.
- **Schema:**
  ```json
  {
    "type": "object",
    "properties": {
      "file_path": {"type": "string"},
      "instruction": {"type": "string"},
      "old_string": {"type": "string"},
      "new_string": {"type": "string"},
      "allow_multiple": {"type": "boolean"}
    },
    "required": ["file_path", "instruction", "old_string", "new_string"]
  }
  ```
- **Why each parameter:** `file_path` identifies the target; `instruction` gives the semantic intent; `old_string` anchors the edit to exact existing text; `new_string` provides the replacement; `allow_multiple` makes replacing multiple identical occurrences an explicit choice rather than an accidental global edit.
- **Description line that corrects a model mistake:** > “Do not use omission placeholders.”  
  **Mistake:** A model might output `...` or “unchanged code” inside the replacement and accidentally delete real code.
- **Deliberately does not:** [INFERRED] It does not prove the program is correct. It makes a targeted textual edit; correctness must be checked separately with tests/validation.
- **Session evidence:** [OBSERVED] `replace` was used five times, including the original bug fixes and later shipping/test changes.

### Tool B: `run_shell_command`

- **Source file:** `packages/core/src/tools/shell.ts` (with declaration helpers in `packages/core/src/tools/definitions/dynamic-declaration-helpers.ts`).
- **Schema:**
  ```json
  {
    "type": "object",
    "properties": {
      "command": {"type": "string"},
      "description": {"type": "string"},
      "dir_path": {"type": "string"},
      "is_background": {"type": "boolean"}
    },
    "required": ["command"]
  }
  ```
  The active schema can add other environment/configuration-dependent fields; the public reference lists these four core arguments.
- **Why each parameter:** `command` is the exact shell operation; `description` tells the user what it is for; `dir_path` selects the working directory; `is_background` explicitly handles long-lived processes without encoding backgrounding into the command string.
- **Description line that corrects a model mistake:** > “Do NOT use `&` to background commands.”  
  **Mistake:** A model could hide background behavior inside shell syntax instead of using the structured `is_background` field.
- **Deliberately does not:** [INFERRED] A successful shell invocation does not imply the software behavior is correct; the model still has to interpret exit status/output and perform the right validation.
- **Session evidence:** [OBSERVED] It was the most-used tool (15 calls), for pytest and Git inspection.

### Why old/new string edits?

First, exact old/new replacement is a lightweight optimistic-concurrency check: if the expected old text is no longer present or is ambiguous, the tool can stop rather than silently editing the wrong location. Second, it keeps edits surgical: only the intended snippet is regenerated, which reduces unrelated changes and makes the proposed diff easier to review.

[OBSERVED] In this trace the agent first read `cart.py` and `pricing.py`, then used `replace` for the two targeted fixes. Later it read/searched the relevant files before using `replace` for shipping and tests. `[timeline around calls #3–#9 and #20–#28]` This matches the system guidance that `replace` can fail when `old_string` is ambiguous and that the agent should gather enough context to make the edit unique.

### Per-model tool descriptions

[OBSERVED from Gemini CLI source] The tool interface can expose model-specific schemas/descriptions through `getSchema(modelId)`. Comparing the `replace` declarations for the Gemini-3 family and the default/legacy family shows the same basic edit interface (`file_path`, `instruction`, `old_string`, `new_string`, `allow_multiple`) but different amounts of prompting guidance. The legacy wording is more prescriptive about reading/context and exact replacement requirements, while the Gemini-3 wording is more compact and emphasizes surgical, reviewable edits.

[INFERRED] This lets the CLI adapt instructions to model behavior without changing the underlying capability. The two successful model names in this trace (`gemini-3.5-flash-lite` and `gemini-3.8-flash`) are both Gemini-3-family names, so they are expected to receive the Gemini-3-style tool declaration rather than a Gemini-2/default-legacy declaration. This is a source-based inference, not a claim that one of the two session models is better.

---

## Part IV — Behavioral analysis

### 1. The loop

```text
[OBSERVED]
call #1/#2
→ update_topic
→ read TASK.md + run pytest
→ calls #3–#7
→ read implementation/tests/config
→ replace cart bug
→ call #8
→ replace pricing bug
→ call #9
→ run pytest
→ calls #10–#15
→ inspect git state / summarize first pass

new user directive
→ calls #16/#17
→ update_topic + read TASK.md
→ run pytest + inspect code/tests
→ grep shipping-related totals
→ calls #23/#24
→ replace pricing/cart shipping logic
→ run pytest
→ update existing shipping-affected expectations
→ add shipping tests
→ run pytest
→ 21 passed
→ inspect git diff/status
→ quota error/retry
→ final update and response #35
```

**What ended it:** [OBSERVED] Successful full-suite validation (`21 passed`), followed by diff/status review and a concluding `update_topic`/final response. The 429 quota error delayed the ending but did not terminate the task.

### 2. Context growth

Selected calls from the trace:

| Response | Model | Input tokens | Cached tokens | Observation |
|---|---|---:|---:|---|
| #1 | gemini-3.5-flash-lite | 1,239 | 0 | Start of first routed interaction |
| #2 | gemini-3.8-flash | 11,429 | 0 | Worker receives much larger coding context |
| #7 | gemini-3.8-flash | 17,912 | 15,450 | Context has grown; much is cached |
| #15 | gemini-3.8-flash | 21,375 | 18,798 | End of first coding pass |
| #16 | gemini-3.5-flash-lite | 799 | 0 | New routing/session phase has a small input again |
| #17 | gemini-3.5-flash-lite | 11,402 | 0 | New user directive with project context |
| #24 | gemini-3.5-flash-lite | 24,228 | 20,297 | Shipping implementation phase |
| #29 | gemini-3.5-flash-lite | 30,648 | 28,401 | Final test phase |
| #35 | gemini-3.5-flash-lite | 32,321 | 28,356 | Final response |

[OBSERVED] Within each coding phase, input tokens generally grow as tool results and prior messages accumulate. Cached-token counts become a large fraction of later calls, showing reuse of an existing prefix/context. The drop from response #15 to #16 indicates a boundary/reset/routing transition rather than monotonic growth across the entire log.

[INFERRED] Caching reduces the amount of repeated context that must be recomputed, which is particularly valuable because the system prompt itself warns that full history makes later turns more expensive. Cached tokens are reused input; they should not be interpreted as additional new tokens on top of the input count.

### 3. Planning

[OBSERVED] My third prompt explicitly requested a plan before execution. The next response/update said it was starting by reading `TASK.md`, then another topic update reported that it had identified the objectives. Later the topic changed to “Implementing Shipping Rules,” followed by implementation, test updates, validation, and final review.

[INFERRED] The plan was useful because the first pass had stopped after fixing only the two original failures. Re-reading `TASK.md` exposed the remaining shipping requirements and turned the second phase into a complete feature/test cycle.

### 4. Error recovery

> “429 … You exceeded your current quota … Please retry in 56…s.”

[OBSERVED] The error occurred after a Git-root check near the end. The next recorded request was about a minute later and succeeded as response #33, after which the agent continued checking Git status and concluded normally.

[INFERRED] This was good recovery because the agent did not redo the code changes or treat the transient API failure as a coding failure. It retried after the requested delay and resumed the pending workflow. Earlier, the initial invalid-API-key errors required user/environment intervention before the real coding session could start.

### 5. The tests

[OBSERVED] The first task explicitly said not to edit existing tests when fixing the original two failures, and the trace shows the agent fixed `shopcart/cart.py` and `shopcart/pricing.py` first, then ran pytest.

For the shipping feature, `TASK.md` explicitly allowed updating **only** old `Cart.total()` expected values affected by the new shipping charge and required a comment explaining why. The original expectations included, for example:

```diff
- assert cart.total() == 2160  # 2000 + 8% tax
+ # Shipping is added after tax under the new pricing rules.
+ assert cart.total() == 2759
```

and analogous shipping-adjusted totals for the discounted carts. The agent also added dedicated shipping tests, including the free-shipping threshold.

[OBSERVED] Timeline evidence: after implementing shipping, pytest exposed old-total mismatches; the agent then issued an update saying it was updating expected values and adding shipping tests, used two `replace` calls for those test changes, reran pytest, and reached 21 passing tests.

[INFERRED] Those test edits are allowed by `TASK.md` because they happened in the shipping phase and represent totals whose expected value necessarily changed. They were not used to hide the two original implementation bugs.

### 6. Models

[OBSERVED] The summary reports `gemini-3.5-flash-lite` for 21 model calls and `gemini-3.8-flash` for 14. An attempted `gemini-3.1-pro-preview` request appears only in the initial invalid-key failure and did not produce a successful response.

[OBSERVED] The early coding phase alternated from a small `gemini-3.5-flash-lite` request into `gemini-3.8-flash`, which handled the initial repository inspection and two bug fixes. The later “complete all of TASK.md” phase was handled by `gemini-3.5-flash-lite`, including planning, shipping implementation, test edits, verification, and Git review.

[INFERRED] This trace demonstrates that model identity is part of the agent architecture rather than a single fixed model call. Different calls can be routed to different models while sharing the same tool-based workflow. The trace alone does not establish that one model is more accurate or cheaper overall; it only records which model handled each call and the associated token counts.
