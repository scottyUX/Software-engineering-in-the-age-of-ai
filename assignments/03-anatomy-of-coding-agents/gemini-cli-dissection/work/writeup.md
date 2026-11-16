# Week 3 Writeup — Inside a Coding Agent

**Name:** Simra Baig
**Gemini CLI version (`gemini --version`):** 0.64.0
**OS / shell:** Windows WSL with bash terminal)
**Model(s) seen in trace:** gemini-3.5-flash-lite (all 14 calls)
**Session commit:** `c535879`

> Evidence tags: `[OBSERVED]` = cite a timeline line, call number, or diff hunk.
> `[INFERRED]` = say what you're reasoning from.

---

## Part I — Session

**Narrative (one paragraph):** 
During the session, I copy pasted the prompt into gemini flash lite and it correctly read the task.md in thw work folder, not the starter. It ran pytest before coding and gave a summary, showing 2 failed and 12 passed. It asked permission to implement fixes, then gave me a summary saying task.md has been completed. It added two additional tests alongside the existing 14 that were in shopcart. I never needed to step in besides giving it permission to act on the files in shopcart.

| Metric | Value |
|---|---|
| User prompts | I only added the one required prompt and tested with pytest|
| Model calls | 14 | <!-- This is found in session calls.csv -->
| Tool calls (failed) | 0|
| Final `pytest` result | All 16 tests pass |
| Did you step in? When / what? | I only stepped in when it asked for permission to run certain tools such |

---

## Part II — System prompt annotation

### Outline
1. Core mandates: standards the agent must follow for various cases
2. Available Sub Agents: When and how to delegate agents, acceptable practices
3. Hook context - A hook is a piece of code that runs automatically when X occurs. Used inside agent loops. This is guidelines on how to interact and understand hooks.
4. Workflow guidelines: Typical workflow patterns for users and what to do.
5. Operational Guidelines: Interacting with the user, how to maintain tone and handle user tools, info.

### Annotations (≥6)
#### Section: Operational Guidelines(tone and verbosity)
> quote
- **Behavior it produces:** An agent that talks in the most efficient, professional way. 
- **Failure it prevents:** An agent who is repeititive, pushy, or provides more information than needed.

#### Section: Operational Guidelines (when not to act / confirm)
> quote
- **Behavior it produces:** Properly ensures it asks for user permission and doesn't do something it does not have authorization for.
- **Failure it prevents:** Empty responses, calling tools without authorization, running critical commands without guidance.

#### Section: Workflow guidelines (workflow)
> quote
- **Behavior it produces:** Given a workflow, it will follow a structure and a certain set of steps. -> research -> strategy -> exceution
- **Failure it prevents:** Jumping from step to step, no concrete cycle, unrelated too calling or code changes.

#### Section: Operatinal Guidelines (tool usage)
> quote
- **Behavior it produces:** User facing response or another tool call, parallel sequencing without collsion
- **Failure it prevents:** Empty responses, unsafe command calling, unseequenced tasks, no update to memory.

#### Section: Sub Agents
> quote
- **Behavior it produces:** Using subagents appropiately to protect context window and limit permanent session history
- **Failure it prevents:** Using sub multiple sub agents on the same task or file, using them for tasks that have less than three steps or small volume.

#### Section: Hook Context
> quote
- **Behavior it produces:** Appropiately using hooks without altering and using them at the correct tikme
- **Failure it prevents:** interpreting hooks as system level commands or safety guidelines, editing hooks.

### Context injection (`GEMINI.md`)
`GEMINI.md`'s content does **not** appear in `submission/session_system.md`. The exported system prompt contains only the static agent instructions — there is no GEMINI.md text embedded in it. Instead, Gemini CLI loads `GEMINI.md` at runtime and injects it as additional context into the first user-turn request, not as part of the system prompt. Evidence: `session_system.md` ends after the Git Repository section with no project-specific content from `work/run/GEMINI.md`. The CLI source confirms this pattern — `GEMINI.md` files are read separately and prepended to the conversation context rather than baked into the system prompt (`packages/core/src/geminiClient.ts`). [INFERRED from session_system.md contents; source: Gemini CLI repo]

---

## Part III — Tool design

### Inventory
| Category | Tools | Used in session (count) |
|---|---|---|
| File | read_file, write_file, replace | x6 read_file , x4 replace|
| Search | glob, grep_search, list_directory | 0 (none called) |
| Shell | run_shell_command, list_background_processes, read_background_output | x4 run_shell_command |
| Web | google_web_search, web_fetch| not called |
| Memory / other | update_topic, enter_plan_mode, ask_user, invoke_agent, activate_skill | x4 update_topic|

### Tool A: replace
- **Source file:** gemini/packages/core/src/tools/definitions/base-declarations.ts
- **Schema:**
  ```
  replace: {
    name: EDIT_TOOL_NAME,
    description: `Replaces text within a file. By default, the tool expects to find and replace exactly ONE occurrence of \`old_string\`. If you want to replace multiple occurrences of the exact same string, set \`allow_multiple\` to true. This tool is preferred for surgical edits to existing files as it minimizes token usage, simplifies code reviews, and avoids accidental deletions. This tool requires providing significant context around the change to ensure precise targeting.
The user has the ability to modify the \`new_string\` content. If modified, this will be stated in the response.`,
    parametersJsonSchema: {
      type: 'object',
      properties: {
        [PARAM_FILE_PATH]: {
          description: 'The path to the file to modify.',
          type: 'string',
        },
        [EDIT_PARAM_INSTRUCTION]: {
          description: `A clear, semantic instruction for the code change, acting as a high-quality prompt for an expert LLM assistant. It must be self-contained and explain the goal of the change.`,
          type: 'string',
        },
        [EDIT_PARAM_OLD_STRING]: {
          description:
            'The exact literal text to replace, unescaped. If this string is not the exact literal text (i.e. you escaped it) or does not match exactly, the tool will fail.',
          type: 'string',
        },
        [EDIT_PARAM_NEW_STRING]: {
          description:
            "The exact literal text to replace `old_string` with, unescaped. Provide the EXACT text. Ensure the resulting code is correct and idiomatic. Do not use omission placeholders like '(rest of methods ...)', '...', or 'unchanged code'; provide exact literal code.",
          type: 'string',
        },
        [EDIT_PARAM_ALLOW_MULTIPLE]: {
          type: 'boolean',
          description:
            'If true, the tool will replace all occurrences of `old_string`. If false (default), it will only succeed if exactly one occurrence is found.',
        },
      },
      required: [
        PARAM_FILE_PATH,
        EDIT_PARAM_INSTRUCTION,
        EDIT_PARAM_OLD_STRING,
        EDIT_PARAM_NEW_STRING,
      ],
    },
  },
  ```
  ```
- **Why each parameter:**
  - `file_path` — identifies the target file.
  - `instruction` — semantic label shown in approval dialogs; helps the model self-check the intent.
  - `old_string` — exact literal anchor; fails safely if the file changed since last read.
  - `new_string` — exact replacement text; prevents `...` stubs from being written verbatim.
  - `allow_multiple` (optional) — safety gate; defaults to rejecting ambiguous multi-match edits.
- **Description line that corrects a model mistake:** `"Do not use omission placeholders like '(rest of methods ...)', '...', or 'unchanged code'; provide exact literal code."` **Mistake prevented:** models abbreviate long replacements with `...`, which gets written into the file as-is.
- **Deliberately does not:** Edit when `old_string` matches zero or more than one location — forces a re-read rather than silently corrupting the file.

### Tool B: run_shell_command
- **Source file:** gemini-cli/packages/core/src/tools/definitions/dynamic-declaration-helpers.ts
- **Schema:**
  ```
  export function getShellDeclaration(
  enableInteractiveShell: boolean,
  enableEfficiency: boolean,
  enableToolSandboxing: boolean = false,
): FunctionDeclaration {
  return {
    name: SHELL_TOOL_NAME,
    description: getShellToolDescription(
      enableInteractiveShell,
      enableEfficiency,
    ),
    parametersJsonSchema: {
      type: 'object',
      properties: {
        [SHELL_PARAM_COMMAND]: {
          type: 'string',
          description: getCommandDescription(),
        },
        [PARAM_DESCRIPTION]: {
          type: 'string',
          description:
            'Brief description of the command for the user. Be specific and concise. Ideally a single sentence. Can be up to 3 sentences for clarity. No line breaks.',
        },
        [PARAM_DIR_PATH]: {
          type: 'string',
          description:
            '(OPTIONAL) The path of the directory to run the command in. If not provided, the project root directory is used. Must be a directory within the workspace and must already exist.',
        },
        [SHELL_PARAM_IS_BACKGROUND]: {
          type: 'boolean',
          description:
            'Set to true if this command should be run in the background (e.g. for long-running servers or watchers). The command will be started, allowed to run for a brief moment to check for immediate errors, and then moved to the background.',
        },
        delay_ms: {
          type: 'integer',
          description:
            'Optional. Delay in milliseconds to wait after starting the process in the background. Useful to allow the process to start and generate initial output before returning.',
        },
        ...(enableToolSandboxing
          ? {
              [PARAM_ADDITIONAL_PERMISSIONS]: {
                type: 'object',
                description:
                  'Sandbox permissions for the command. Use this to request additional sandboxed filesystem or network permissions if a previous command failed with "Operation not permitted".',
                properties: {
                  network: {
                    type: 'boolean',
                    description:
                      'Set to true to enable network access for this command.',
                  },
                  fileSystem: {
                    type: 'object',
                    properties: {
                      read: {
                        type: 'array',
                        items: { type: 'string' },
                        description:
                          'List of additional absolute paths to allow reading.',
                      },
                      write: {
                        type: 'array',
                        items: { type: 'string' },
                        description:
                          'List of additional absolute paths to allow writing.',
                      },
                    },
                  },
                },
              },
            }
          : {}),
      },
      required: [SHELL_PARAM_COMMAND],
    },
  };
}

  ```
- **Why each parameter:**
  - `command` — the shell string to run; only required field.
  - `description` — human-readable summary shown in the approval dialog before execution.
  - `dir_path` (optional) — working directory; defaults to project root.
  - `is_background` (optional) — runs the process in the background for servers/watchers.
  - `delay_ms` (optional) — wait time after background start so initial output is readable.
  - `additional_permissions` (optional, sandboxing only) — per-call request for extra filesystem or network access.
- **Description line that corrects a model mistake:** `"Brief description of the command for the user. Be specific and concise. Ideally a single sentence. No line breaks."` **Mistake prevented:** models write vague or multi-line descriptions that break the approval UI.
- **Deliberately does not:** Persist shell state across calls — each runs in a fresh `bash -c` context. Visible in the trace: at call #3 (23:56:51) the agent passed the full `python -m pytest` command rather than relying on any prior shell state. [OBSERVED]

### Why old/new string edits?
1. **Content-anchored, not position-anchored.** Line numbers shift as soon as any earlier line is added or removed. An exact string match stays valid regardless of surrounding changes, so the tool can re-apply correctly even if the file was edited between the `read_file` and the `replace` call.
2. **Fail-safe precision.** If `old_string` is ambiguous the tool errors out rather than silently editing the wrong location. The system prompt itself warns the model about this: *"replace fails if old_string is ambiguous, causing extra turns"* (session_system.md, Context Efficiency guidelines, line 31). This pushes the model to read enough context to write an unambiguous match.

**Trace moment:** At call #6 → replace (23:59:20) the agent replaced a large block in `shopcart/cart.py`. The `old_string` spanned multiple lines including the docstring and imports, giving it enough surrounding context to be unique in the file. Had the tool used line numbers, a one-line shift from any earlier change would have caused a silent misfire. [OBSERVED: timeline 23:59:20]

### Per-model tool descriptions
**Tool compared:** `replace`  
**Files:** `gemini-3.ts` (L356) vs `default-legacy.ts` (L349) in `packages/core/src/tools/definitions/model-family-sets/`.

| | `gemini-3.ts` | `default-legacy.ts` |
|---|---|---|
| Description length | Short, concise | Longer, more explicit |
| Tone | Directive ("provide exact text") | Instructional — spells out edge cases, fuzzy-match warnings, line-ending handling |
| Token cost | Lower per call | Higher per call |

**Why the difference:** Older/legacy models need more hand-holding in the schema to prevent malformed edits (stubs, wrong context, escaped strings). Gemini 3 models have stronger native instruction-following, so the schema is trimmed — saving tokens that can instead hold file content. The session ran entirely on `gemini-3.5-flash-lite` (confirmed: every `model=` field in `session_timeline.txt`), so it received the shorter `gemini-3.ts` variant. [OBSERVED: timeline, all 14 RESPONSE lines]

---

## Part IV — Behavioral analysis

### 1. The loop
```
call#1 → update_topic + read_file(TASK.md)
call#2 → read_file(cart.py) + read_file(test_cart.py)
call#3 → run_shell_command(pytest)
call#4 → read_file(catalog.py)
call#5 → update_topic
call#6 → replace(cart.py)
call#7 → replace(pricing.py)
call#8 → read_file(test_cart.py)
call#9 → replace(test_cart.py)
call#10 → run_shell_command(pytest) — all pass
call#11 → update_topic (recap)
call#12 → [text response to user]
call#13 → run_shell_command(pytest -q)  ← second user prompt
call#14 → [text response]
```
What ended it: the agent decided it was done after call #12 (summary response). The loop restarted only because the user manually ran `python -m pytest -q` as a second prompt. [OBSERVED: timeline]

### 2. Context growth

| Call | input tokens | cached tokens |
|------|-------------|--------------|
| 1 | 11,565 | 0 |
| 2 | 12,228 | 10,142 |
| 3 | 14,065 | 10,130 |
| 4 | 14,776 | 12,154 |
| 5 | 16,154 | 12,158 |
| 6 | 18,572 | 14,196 |
| 7 | 20,124 | 16,229 |
| 8 | 22,111 | 18,265 |
| 9 | 23,483 | 20,296 |
| 10 | 25,853 | 22,336 |
| 11 | 26,088 | 22,329 |
| 12 | 26,343 | 22,322 |
| 13 | 27,275 | 24,352 |
| 14 | 27,436 | 24,345 |

Input grows ~1,500–2,000 tokens per call because the full conversation history (all prior messages + tool responses) is re-sent on every request. `cached_content_token_count` shows the API already has a prefix cached — by call #14 about 89 % of input tokens hit the cache. Caching matters because cached tokens are billed at a fraction of the cost of fresh tokens and are processed faster, so a long session stays cheap even as the context window fills. [OBSERVED: session_calls.csv]

### 3. Planning
The agent used `update_topic` three times to track progress as named phases [OBSERVED: timeline]:
- **Call #1** — `update_topic` with `strategic_intent`: "Read TASK.md to understand the assignment requirements" → read TASK.md, then read source and test files.
- **Call #5** — `update_topic` title: "Implementing Fixes and Shipping Feature" → began edits to `cart.py` and `pricing.py`.
- **Call #11** — `update_topic` `strategic_intent`: "Recap completed work and finalize the task."

The plan matched what the agent actually did: research (calls 1–4) → implementation (calls 6–9) → validation (call 10) → summary (calls 11–12). It did not depart from this plan.

### 4. Error recovery
> `run_shell_command(pytest)` at call #3 returned 2 failing tests: `test_total_includes_tax` and `test_percent_discount` (values assumed no shipping). [OBSERVED: timeline 23:56:51]

After seeing the failures, the agent immediately read `shopcart/catalog.py` (call #4, 23:56:54) to check the price data, then at call #5 formed a strategy covering both the `add_item` bug and the missing shipping feature before touching any file. Recovery was good: it diagnosed both failures in one extra read rather than blind-patching, and validated with pytest again at call #10 before declaring done.

### 5. The tests
The agent edited `tests/test_cart.py` at call #9 (23:59:47). It updated three expected values in existing tests and added two new tests:

```diff
-    assert cart.total() == 2160  # 2000 + 8% tax
+    assert cart.total() == 2759  # 2000 + 8% tax + $5.99 shipping

-    assert cart.total() == 2333  # (2400 - 10%) + 8% tax
+    assert cart.total() == 2932  # (2400 - 10%) + 8% tax + $5.99 shipping

-    assert cart.total() == 3240  # (4000 - 1000) + 8% tax
+    assert cart.total() == 3839  # (4000 - 1000) + 8% tax + $5.99 shipping

+def test_free_shipping_at_or_above_threshold(): ...
+def test_shipping_not_taxed(): ...
```

**Allowed by TASK.md?** Yes. TASK.md explicitly states: *"Some existing tests check `Cart.total()` with values from before shipping existed. You may update those expected values — and only those — and note why in a comment."* The agent updated exactly those values and commented each one. [OBSERVED: diff of tests/test_cart.py]

### 6. Models
Every `RESPONSE` line in `session_timeline.txt` shows `model=gemini-3.5-flash-lite`, confirming the single-model run. [OBSERVED: all 14 RESPONSE lines]

Highest-thinking calls from `session_calls.csv`:
| Call | thoughts tokens | What the agent was deciding |
|------|----------------|-----------------------------|
| #5 | 2,167 | Forming the full implementation strategy after seeing the pytest failures and reading all source files |
| #4 | 1,157 | Deciding what else to read after seeing test output — chose `catalog.py` |
| #6 | 630 | Planning the exact `replace` for `cart.py` (largest edit) |

**Without `-m`, the default setup uses two models:** `gemini-3.5-flash-lite` routes/classifies each request and `gemini-3.8-flash` does the heavy reasoning. This split trades quality for cost: the lite model is cheap for routing decisions, while the larger model handles complex coding. Running the whole session on a bigger model would improve code quality and reduce thinking turns (fewer re-reads to diagnose failures) at higher token cost and slightly more latency per call. [INFERRED from model landscape lecture + timeline data]
