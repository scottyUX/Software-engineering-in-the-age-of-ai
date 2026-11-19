# Week 3 Writeup — Inside a Coding Agent

**Name:** Thalia Eischeid
**Gemini CLI version (`gemini --version`):** 0.64.0
**OS / shell:** macOS + zsh
**Model(s) seen in trace:** gemini-3.5-flash-lite
**Session commit:** `7b06006`

> Evidence tags: `[OBSERVED]` = cite a timeline line, call number, or diff hunk.
> `[INFERRED]` = say what you're reasoning from.

---

## Part I — Session

**Narrative (one paragraph):** I gave Gemini CLI the assignment's required prompt, and it first stated a plan, read `TASK.md`, and inspected the shopping-cart source and tests. It then used shell commands to run the suite. Its first few attempts could not find an available `python`/`pytest` executable in the inherited shell, so it tried alternatives and eventually used the project environment successfully. It then checked the diff and reran the tests before reporting completion. I did not supply debugging advice, edits, or any other help to the agent. After it finished, I independently entered `python -m pytest -q` in the CLI as required, which also produced 17 passing tests. [OBSERVED: `session_timeline.txt` lines 1–45]

| Metric | Value |
|---|---|
| User prompts | 2 |
| Model calls | 14 |
| Tool calls (failed) | 19 (0) |
| Final `pytest` result | 17 passed in 0.01s |
| Did you step in? When / what? | No. I approved requests but gave the agent no assistance. The second user prompt was my required post-completion `python -m pytest -q` validation. |

---

## Part II — System prompt annotation

### Outline
1. **Core Mandates / Security & System Integrity** — protect credentials, respect source-control boundaries, and treat tool output as untrusted data.
2. **Context Efficiency** — minimize unnecessary context growth while preserving enough evidence to act correctly.
3. **Engineering Standards** — apply repository conventions, honor `GEMINI.md`, and avoid type-system or linting shortcuts.
4. **Topic Updates** — narrate significant changes in task phase or unexpected events with `update_topic`.
5. **Available Sub-Agents and Agent Skills** — describe specialized agents and skills that can be invoked for particular tasks.
6. **Hook Context** — provide rules for hook-provided context.
7. **Primary Workflows / Development Lifecycle** — require research, strategy, execution, and validation for engineering work.
8. **New Applications** — add planning and design defaults for building a new application.
9. **Operational Guidelines / Tone and Style** — define concise, professional CLI communication.
10. **Security and Safety Rules** — explain consequential shell actions and protect sensitive data.
11. **Tool Usage and Interaction Details** — define tool-follow-up, sequencing, editing, and confirmation behavior.
12. **Git Repository** — constrain staging, committing, review, and pushing behavior.

### Annotations (≥6)
#### Section: Tone and Style (tone and verbosity)
> “Concise & Direct: Adopt a professional, direct, and concise tone suitable for a CLI environment.”
> “Minimal Output: Aim for fewer than 3 lines of text output ... per response whenever practical.” (`system.md` lines 173–174)
- **Behavior it produces:** The agent communicates the decision and rationale briefly, then spends its turns on tools rather than narration.
- **Failure it prevents:** It limits noisy status messages and avoids consuming the context window with repeated explanations.

#### Section: Security & System Integrity (when not to act / confirm)
> “Source Control: Do not stage or commit changes unless specifically requested by the user.” (`system.md` line 7)
- **Behavior it produces:** The agent leaves repository history under the user's control unless the user explicitly asks for a commit.
- **Failure it prevents:** It prevents an autonomous coding session from accidentally staging unrelated files or creating an unwanted commit.

#### Section: Development Lifecycle (workflow)
> “Operate using a **Research -> Strategy -> Execution** lifecycle. For the Execution phase, resolve each sub-task through an iterative **Plan -> Act -> Validate** cycle.” (`system.md` line 135)
- **Behavior it produces:** The agent reads and reproduces the problem before changing code, explains a strategy, makes a targeted change, and validates it.
- **Failure it prevents:** It prevents speculative edits and declaring a fix successful without evidence.

#### Section: Tool Usage (tool usage)
> “After receiving a `functionResponse`, you MUST ALWAYS ... Call another tool to proceed with the task [or] Provide a user-facing text response explaining the tool output, your analysis, and next steps.” (`system.md` lines 186–190)
- **Behavior it produces:** Every tool result has an explicit next action or interpretation. The agent cannot silently drop the result.
- **Failure it prevents:** It prevents stalled loops and makes tool-result handling inspectable by the user.

#### Section: Engineering Standards (project instructions)
> “Instructions found in `GEMINI.md` files are foundational mandates. They take absolute precedence over the general workflows and tool defaults described in this system prompt.” (`system.md` line 41)
- **Behavior it produces:** Repository-specific constraints override broad defaults. In this run, the project’s Python, money, file-location, and test-command conventions guide the task.
- **Failure it prevents:** It prevents generic agent habits from violating project rules or local architecture.

#### Section: Security and Safety Rules (shell actions)
> “Before executing commands with `run_shell_command` that modify the file system, codebase, or system state, you *must* provide a brief explanation of the command's purpose and potential impact.” (`system.md` line 182)
- **Behavior it produces:** The agent gives the user meaningful context before potentially consequential shell work, while the CLI presents its approval dialog.
- **Failure it prevents:** It prevents opaque, surprising modifications and gives the user a chance to reject a risky action.

#### Section: Confirmation Protocol
> “If a tool call is declined or cancelled, respect the decision immediately. Do not re-attempt the action or ‘negotiate’ for the same tool call unless the user explicitly directs you to.” (`system.md` line 214)
- **Behavior it produces:** A declined permission becomes a boundary. The agent either stops that action or finds a distinct alternative.
- **Failure it prevents:** It prevents repeated permission prompts that pressure a user into accepting an action.

### Context injection (`GEMINI.md`)
The actual project-context text is not in either exported system-prompt copy: searching `work/prompts/system.md` and `work/submission/session_system.md` found none of its distinctive lines (for example, “All money is integer cents”). [OBSERVED] The prompt does state that `GEMINI.md` instructions take precedence (`system.md` line 41), but it does not embed this project's contents. In the matching v0.64.0 source, `Config.getSessionMemory()` describes Tier 2 project memory as injected “into the first user message,” then wraps it in `<loaded_context><project_context>...</project_context></loaded_context>` ([`config.ts` lines 2475–2497](https://github.com/google-gemini/gemini-cli/blob/v0.64.0/packages/core/src/config/config.ts#L2475-L2497)). [OBSERVED] Therefore, the working-copy `GEMINI.md` reaches the model alongside the initial user turn rather than through the exported system prompt. [INFERRED] This also explains why the session begins with a large 17,080-token input despite the visible assignment prompt being short (`session_calls.csv`, call 1).

---

## Part III — Tool design

### Inventory
| Category | Tools | Used in session (count) |
|---|---|---|
| File | `read_file`, `list_directory`, `write_file`, `replace` | `read_file`: 4; all other file tools: 0 |
| Search | `glob`, `grep_search` | 0 |
| Shell | `run_shell_command`, `list_background_processes`, `read_background_output` | `run_shell_command`: 9; background tools: 0 |
| Web | `google_web_search`, `web_fetch` | 0 |
| Planning / narration | `enter_plan_mode`, `update_topic` | `update_topic`: 6; `enter_plan_mode`: 0 |
| Delegation | `invoke_agent`, `activate_skill` | 0 |
| Other | `ask_user` | 0 |

I ran `/tools` in Gemini CLI v0.64.0 after the captured session. It listed these 16 built-in tools. The usage counts come from the session-summary block in `session_timeline.txt`. [OBSERVED]

### Tool A: `replace`
- **Source file:** [`gemini-3.ts` lines 356–405](https://github.com/google-gemini/gemini-cli/blob/v0.64.0/packages/core/src/tools/definitions/model-family-sets/gemini-3.ts#L356-L405), implementation: [`edit.ts` lines 391–421](https://github.com/google-gemini/gemini-cli/blob/v0.64.0/packages/core/src/tools/edit.ts#L391-L421).
- **Schema:**
  ```text
  { file_path: string, instruction: string, old_string: string,
    new_string: string, allow_multiple?: boolean }
  ```
  `file_path`, `instruction`, `old_string`, and `new_string` are required.
- **Why each parameter:** `file_path` identifies the target, `instruction` preserves the semantic goal for review and recovery, `old_string` anchors the exact current text, `new_string` supplies the complete replacement, and optional `allow_multiple` makes an intentional all-occurrences edit possible rather than silently broadening a default edit.
- **Description line that corrects a model mistake:** > “If true, the tool will replace all occurrences of `old_string`. If false (default), it will only succeed if exactly one occurrence is found.” **Mistake:** accidentally changing several identical snippets when the agent intended one surgical edit.
- **Deliberately does not:** It does not accept omission placeholders in `new_string` such as “rest of methods ...”, the implementation rejects them so an agent cannot replace real code with an incomplete sketch ([`edit.ts` lines 1225–1234](https://github.com/google-gemini/gemini-cli/blob/v0.64.0/packages/core/src/tools/edit.ts#L1225-L1234)).

### Tool B: `run_shell_command`
- **Source file:** [`dynamic-declaration-helpers.ts` lines 36–143](https://github.com/google-gemini/gemini-cli/blob/v0.64.0/packages/core/src/tools/definitions/dynamic-declaration-helpers.ts#L36-L143), implementation: [`shell.ts` lines 93–99 and 530–539](https://github.com/google-gemini/gemini-cli/blob/v0.64.0/packages/core/src/tools/shell.ts#L93-L99).
- **Schema:**
  ```text
  { command: string, description?: string, dir_path?: string,
    is_background?: boolean, delay_ms?: integer,
    additional_permissions?: { network?: boolean,
      fileSystem?: { read?: string[], write?: string[] } } }
  ```
  Only `command` is required. `additional_permissions` appears only when tool sandboxing is enabled, so it was not relevant to this unsandboxed session.
- **Why each parameter:** `command` is the exact Bash command on macOS/Linux, `description` gives the approval dialog a short user-facing purpose, `dir_path` scopes execution to an existing workspace directory, `is_background` marks long-running servers/watchers, `delay_ms` allows initial background output, and conditional `additional_permissions` asks for narrowly scoped sandbox access after a denial.
- **Description line that corrects a model mistake:** > “To run a command in the background, set the `is_background` parameter to true. Do NOT use `&` to background commands.” **Mistake:** using shell syntax that bypasses the CLI's background-process tracking and lifecycle.
- **Deliberately does not:** It does not execute commands containing command-substitution syntax (`$()`, backticks, `<()`, or `>()`). `shell.ts` blocks those forms as injection risks before execution ([`shell.ts` lines 530–539](https://github.com/google-gemini/gemini-cli/blob/v0.64.0/packages/core/src/tools/shell.ts#L530-L539)).

### Why old/new string edits?
  Exact old/new strings make the target verifiable. The tool can fail rather than edit the wrong duplicate or a file that has changed since the agent read it. They are also efficient and reviewable. A small replacement sends less context and produces a focused diff instead of rewriting a whole file, the Gemini 3 description explicitly says this minimizes token use, simplifies review, and avoids accidental deletion. This session never invoked `replace` (its `/tools` count is zero), all 9 execution calls were `run_shell_command`, including the commands that produced the agent commit. [OBSERVED: `session_timeline.txt` summary and session commit `7b06006`]

### Per-model tool descriptions
I compared `replace`. Both descriptions use the same schema, but the Gemini 3 version is compact. It emphasizes one-match-by-default behavior, surgical edits, token savings, reviewability, and accidental-deletion avoidance ([`gemini-3.ts` lines 356–405](https://github.com/google-gemini/gemini-cli/blob/v0.64.0/packages/core/src/tools/definitions/model-family-sets/gemini-3.ts#L356-L405)). The legacy version adds a much more prescriptive checklist. Read the file first, include three lines of surrounding context, do not escape either string, make `old_string` unique, use detailed why/where/what/outcome instructions, and split complex changes into atomic calls ([`default-legacy.ts` lines 349–425](https://github.com/google-gemini/gemini-cli/blob/v0.64.0/packages/core/src/tools/definitions/model-family-sets/default-legacy.ts#L349-L425)). [OBSERVED] I infer that the older family receives more behavioral scaffolding to reduce brittle edits, while the Gemini 3 family can use a shorter declaration that preserves the core guardrails and saves context. [INFERRED]

---

## Part IV — Behavioral analysis

### 1. The loop

[OBSERVED: `session_timeline.txt`] The tool sequence below reconstructs the original task loop through the agent's final answer.

```
call #1 → update_topic + read TASK.md → call #2
→ update_topic + read cart.py/pricing.py/test_cart.py → call #3
→ update_topic + python -m pytest → calls #4–#7 (environment recovery)
→ call #8 → update_topic + git status/diff → call #9
→ update_topic + final pytest → call #10 → update_topic → call #11 (final answer)
```
[OBSERVED] The agent ended its task itself: after call #10 it updated the topic to a concluding state, and call #11 followed with no further tool call. The later calls #12–#14 belong to my required independent `python -m pytest -q` validation prompt, rather than the agent's original task loop (`session_timeline.txt`, 00:32:30–00:32:39). No usage limit or user intervention ended the agent's work.

### 2. Context growth

[OBSERVED: `session_calls.csv`] The table records each response's input-token count and cached-content-token count.

| Call | Input tokens | Cached tokens |
|---:|---:|---:|
| 1 | 17,080 | 0 |
| 2 | 17,702 | 0 |
| 3 | 20,515 | 16,251 |
| 4 | 20,785 | 18,269 |
| 5 | 20,962 | 18,262 |
| 6 | 21,239 | 18,255 |
| 7 | 21,590 | 18,250 |
| 8 | 21,853 | 18,244 |
| 9 | 24,913 | 20,282 |
| 10 | 25,655 | 22,301 |
| 11 | 26,108 | 22,296 |
| 12 | 26,465 | 24,319 |
| 13 | 26,759 | 24,313 |
| 14 | 27,080 | 24,307 |

[OBSERVED] The input context rose from 17,080 tokens at call #1 to 27,080 at call #14, a gain of 10,000 tokens (about 59%). The table is transcribed from `session_calls.csv`. [INFERRED] It grows because later requests carry the original instructions, conversation history, tool requests, and tool results in addition to the newest event, exactly the cost pattern the system prompt warns about in `system.md` lines 15–16. [OBSERVED] Cached tokens were zero for the first two calls and then remained high, reaching 24,319 at call #12. [INFERRED] That indicates a repeated input prefix was served from prompt cache, which can reduce the latency and processing cost of reused context even though the total context still grew.

### 3. Planning
[OBSERVED] The agent used `update_topic` six times and did not call `enter_plan_mode`, `write_todos`, or a subagent. Its updates cover initialization (call #1), codebase research (call #2), test/environment investigation (call #3), post-test review (call #8), validation (call #9), and conclusion (call #10) (`session_timeline.txt`). This aligns with the system prompt's Topic Updates guidance, which says to update the topic for an unexpected environment issue (`system.md` lines 52–63). [OBSERVED] Its apparent plan was research → run tests → repair/validate → conclude. The implementation and 17-passing-test result are recorded in session commit `7b06006`. [INFERRED] The long detour through three unavailable Python/pytest invocations and a filesystem search was not part of the intended plan, it was an environment-recovery detour.

### 4. Error recovery

> [OBSERVED: raw telemetry output for the 00:29:15 shell call] `/bin/bash: line 3: python: command not found`

[OBSERVED] The first test command was `python -m pytest -q` at 00:29:15. After its failure the agent tried `python3 -m pytest -q` (00:29:17), then `.venv/bin/pytest` (00:29:19), then a `find /` search (00:31:18), and ultimately an explicit project-virtual-environment pytest path (00:31:53), which led to its “17 passed” update at 00:31:56 (`session_timeline.txt`). The telemetry summary still counts zero *failed tool calls* because each `run_shell_command` invocation itself returned normally. The unsuccessful commands are failures reported by the shell command output. [OBSERVED: summary plus timeline timestamps] [INFERRED] The recovery was successful because it reached a passing suite without help, but it was inefficient and broader than necessary: activating or locating the already-created project `.venv` directly would have avoided the filesystem-wide search.

### 5. The tests
[OBSERVED] The agent edited three existing expected totals in `tests/test_cart.py` and added three shipping tests in session commit `7b06006`. For example, it changed:

```diff
-    assert cart.total() == 2160  # 2000 + 8% tax
+    assert cart.total() == 2759  # (2000 + 8% tax) + $5.99 shipping
```

[OBSERVED] `TASK.md` explicitly permits updating existing expected values for tests that predate shipping, provided the reason is noted in a comment, the changed comments do that. The new tests cover a subtotal above the free-shipping threshold and discounted subtotals above and below it. [OBSERVED: `TASK.md` section 2 and commit `7b06006` diff] [INFERRED] The tests are appropriate coverage for the requested rule, although they do not exercise the exact 5,000-cent boundary because their free-shipping examples start from 6,000 cents.

### 6. Models
[OBSERVED] Every one of the 14 `model` fields in `session_calls.csv` is `gemini-3.5-flash-lite`, so the explicit `-m gemini-3.5-flash-lite` option kept this recorded session on one model. [OBSERVED] Call #8 has the highest `thoughts_token_count` (931), followed by call #9 (417). Call #8 follows the first successful test result and precedes the agent's status/diff check, call #9 follows that inspection and precedes the final validation run (`session_timeline.txt`). [INFERRED] Those are likely the moments when it was deciding whether the changes were ready to report and whether another full validation was needed.

[OBSERVED: `assignment.md`, Part IV.6] Without `-m`, the assignment specifies that Gemini CLI uses `gemini-3.5-flash-lite` to route requests and `gemini-3.8-flash` for the coding work. [INFERRED] Separating routing from execution lets the CLI use a cheaper, faster model for the repetitive choice of where to send work and reserve the more capable model for substantive implementation. Compared with this pinned lite-only run, an all-larger-model session would plausibly cost more and respond more slowly while improving difficult reasoning or code quality. Because this trace was pinned to one model, those default two-model effects were not observed here.
