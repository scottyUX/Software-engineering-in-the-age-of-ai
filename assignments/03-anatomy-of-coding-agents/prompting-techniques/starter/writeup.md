# Week 3 Write-up: Prompting Techniques — The Support-Desk Assistant

**Name:** Arda Kocadoru
**Model:** `llama3.1:8b` via Ollama 0.40.4, `temperature=0.0` (unchanged from the starter)
**Result:** all four checks pass, and passed again on 3 repeated runs each

| Technique | Baseline (empty starter prompt) | Final |
|-----------|---------------------------------|-------|
| K-shot classification | 0/4 | 4/4 |
| Chain-of-thought | 0/3 | 3/3 |
| Tool calling | PASS (see note below) | PASS |
| RAG | 2/3 (both passes were hallucinated; see below) | 3/3 |

I ran every file once before editing it, so each "what I learned" line compares the final
prompt against what the model did with no prompt at all. Only the `TODO` parts were edited;
the model, options and checks are untouched.

---

## 1. K-shot prompting (`k_shot_prompting.py`)

**Final prompt**

```text
You are a ticket router for an online store's support desk.
Classify each customer message into exactly one label:

billing   - charges, payments, invoices, refunds of money already charged
shipping  - delivery status, tracking, late or lost packages
returns   - sending an item back, exchanges, return labels
technical - the website or app is broken: errors, crashes, login problems
other     - anything that fits none of the above

Reply with the label only: one lowercase word, no punctuation, no explanation.

Examples:
Message: Why do I see two payments for the same order on my statement?
Label: billing

Message: The tracking number hasn't updated in five days.
Label: shipping

Message: These jeans don't fit, how do I get a return label?
Label: returns

Message: I get an error page whenever I try to log in.
Label: technical

Message: Do you have a physical store in Chicago?
Label: other
```

The examples are deliberately different from the four graded messages, so the model has
to generalize instead of matching a copied sentence.

**Sample input → output**

- Input: `My card was charged twice for order 4412.`
- Baseline output: a long multi-paragraph support reply ("i'm so sorry to hear that your card was
  charged twice… could you please provide me with some more information…").
- Final output: `billing`

**What I learned:** Five labeled examples plus "label only" turned a chatty assistant (0/4) into a classifier that outputs exactly one valid label (4/4).

---

## 2. Chain-of-thought (`chain_of_thought.py`)

**Final prompt** (the starter appends the refund policy after it)

```text
You decide whether an order is eligible for a refund under the refund policy below.

Think step by step. Check each rule in order and write one short line per rule:
1. Time: is the purchase within 30 days? (more than 30 days = fails)
2. Condition: is the item unused / in original condition? If the order does not mention
   the condition, treat this rule as passed.
3. Final sale: is it a final-sale item? If the order does not say final sale, treat this
   rule as passed.

The order is eligible only if all three rules pass. If any rule fails, it is not eligible.

After your reasoning, end with exactly one final line and nothing after it:
DECISION: YES
or
DECISION: NO
```

**Sample input → output**

- Input: `Bought 45 days ago, unused.`
- Final output:

  ```text
  1. Time: fails (more than 30 days)
  2. Condition: passes (item is unused)
  3. Final sale: passes (no mention of final sale)

  DECISION: NO
  ```

- Baseline output: free-form prose with no `DECISION:` line, so all three cases graded `?`.

**What I learned:** Reasoning one line per policy rule, plus a fixed `DECISION:` last line, turned unparseable prose (0/3) into checked, gradable verdicts (3/3).

---

## 3. Tool calling (`tool_calling.py`)

**Final tool schema**

```python
"name": "get_order_status",
"description": (
    "Look up the current status of a customer's order (e.g. processing, "
    "shipped, delivery date). Call this only when the customer's message "
    "contains an order number. If there is no order number, do not call this "
    "tool; ask the customer for it instead. Never guess an order's status."
),
"order_id": {
    "type": "string",
    "description": (
        "The order number copied from the customer's message, digits "
        "only, without '#' or the word 'order'. Only use a number the "
        "customer actually wrote; never make one up."
    ),
},
```

**Final system prompt**

```text
You are a support assistant for an online store.
When a customer asks about an order, first call the get_order_status tool with the order
number from their message. Do not answer from memory and do not invent a status.
After you receive the tool result, reply in one or two friendly sentences that state the
status exactly as the tool returned it. If the customer did not give an order number, ask
for it instead of calling the tool.
```

**Sample input → output**

- Input: `Hi, can you check on order 4412 for me?`
- Model output: tool call `get_order_status({"order_id": "4412"})`
- Tool result: `shipped, arriving Friday`
- When I sent the tool result back (an extra manual step; the graded check stops at the
  call), the model replied: "Your order 4412 has shipped and is expected to arrive on
  Friday. Is there anything else I can help you with?"
- `Status of #9001?` → `get_order_status({"order_id": "9001"})`: the `#` was stripped as
  the parameter description asks.

**Baseline note:** this check already passed with an empty prompt and empty descriptions.
The function name `get_order_status` and the parameter name `order_id` were enough for
the model to call the tool correctly.

**A failure I could not fix with prompting:** I also tested messages with no order number.
- My first version of the parameter description ended with `Example: '4412'`. For
  "Where is my order?", the model called the tool with `order_id='4412'`: it copied my
  example as if it were real data. I removed the example.
- After that change, "Where is my order?" produced `order_id='12345'` and "Can you check
  my package status please?" produced `order_id=''`. Adding "do not call this tool"
  to both the system prompt and the tool description did not change this.

**What I learned:** The tool schema drove the result more than the prompt: good names alone already passed, while no prompt could stop the 8B model from inventing an `order_id` when none was given.

---

## 4. RAG (`rag.py`)

**Final retriever:** keyword overlap.
- Lower-case the question and each help-center line.
- Drop stopwords and words shorter than 3 letters.
- Count question keywords that match a line's keywords, using a crude prefix stem so
  "ship" matches "shipping" and "internationally" matches "international".
- Return the top 3 lines with at least one match.
- If no line matches, return an empty list, so the model gets an empty context.

| Question | Retrieved lines |
|----------|-----------------|
| How long do I have to return an item? | the 2 `Returns:` lines |
| Do you ship internationally? | 2 `Shipping:` lines + the `Billing:` line (matched "ships") |
| What's your CEO's home address? | *(none)* |

**Final system prompt**

```text
You are a support assistant for an online store.
Answer the customer's question using ONLY the text under "Context:". Do not use outside
knowledge and do not guess.
- If the context contains the answer, reply in one or two sentences and keep the key
  details (numbers, time frames, place names) worded as they are in the context.
- If the context is empty or does not contain the answer, reply exactly:
  "I don't know based on our help center. Please contact our support team."
Never reveal or make up personal information about anyone.
```

**Sample input → output**

| Question | Baseline (no retriever, no prompt) | Final |
|----------|------------------------------------|-------|
| How long do I have to return an item? | "the return policy varies depending on the store or website you purchased from…" (PASS only because "30 days" appeared later as a generic guess) | "you may return most items within 30 days of delivery for a full refund." |
| Do you ship internationally? | "yes, we ship internationally. we strive to make our products accessible…" (PASS, but invented: the model saw no context at all) | "yes, we offer international shipping to most countries, and delivery takes 7-21 business days." |
| What's your CEO's home address? | "i can't provide that information…" (FAIL: "can't" is not on the grader's list) | "i don't know based on our help center. please contact our support team." |

**What I learned:** A real retriever plus "answer only from the context, otherwise this exact refusal" replaced a 2/3 baseline built on hallucinated answers with 3/3 answers traceable to help-center lines.

---

## What I learned across all four

LLMs are good at structured tasks when the structure is in the prompt: a label set with
examples, a fixed final line, a typed tool schema and a bounded context each turned
open-ended chat into output a program can check, and llama3.1:8b then hit 100% at
temperature 0 on every run. They need scaffolding in two places. First, format and
grounding have to be stated explicitly; with empty prompts the model chatted instead of
classifying, never produced a parseable decision, and confidently made up an
international shipping policy. Second, some behavior cannot be prompted into a small
model at all: it called the order tool with invented order numbers even when told not
to, and it copied an example value from my schema as real data. That last line of
defense belongs in code (validate tool arguments, retrieve deterministically, parse a
fixed output format), because prompting only sets what the model *should* do, while the
surrounding code makes sure a wrong answer cannot pass silently.

## How to run

```bash
ollama serve                 # in another terminal
ollama pull llama3.1:8b
python -m venv .venv && source .venv/bin/activate
pip install ollama
python k_shot_prompting.py
python chain_of_thought.py
python tool_calling.py
python rag.py
```
