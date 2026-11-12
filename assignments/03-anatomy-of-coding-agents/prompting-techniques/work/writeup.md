# Week 3 Prompting Techniques Writeup

Model: `llama3.1:8b` running locally with Ollama on Windows (temperature 0, which the
starter files already set). I only changed the parts marked TODO.

All four checks pass:

```text
k_shot_prompting.py   4/4 correct
chain_of_thought.py   3/3 correct
tool_calling.py       PASS, tool called with order_id='4412'
rag.py                3/3 correct
```

One thing that wasn't about prompting at all: the first time I ran these, every file
crashed with `unable to allocate CPU_REPACK buffer of size 3359637504`. My laptop has 15 GB
of RAM, but with Chrome and other things open there wasn't enough free to load the 8B
model. After closing apps and restarting Ollama, it loaded fine. So these models are pretty
heavy to run locally.

## 1. K-shot prompting (`k_shot_prompting.py`)

**Final prompt:**

```text
You classify customer support tickets for an online store.

Labels:
- billing: charges, payments, invoices, refunds of money already charged, promo codes
- shipping: delivery status, tracking, delays, lost or late packages, addresses
- returns: sending an item back, exchanges, return labels, return eligibility
- technical: the website or app not working, errors, crashes, login problems
- other: anything that fits none of the above

Reply with exactly one label in lowercase. No punctuation, no explanation, no other words.

Examples:
Ticket: I was billed $40 but my order total was $25.
Label: billing

Ticket: My tracking number hasn't updated in five days.
Label: shipping

Ticket: How do I return a jacket that doesn't fit?
Label: returns

Ticket: I get an error 500 when I click checkout.
Label: technical

Ticket: Do you have a physical store in Chicago?
Label: other

Ticket: Why did my credit card get charged before the item shipped?
Label: billing

Ticket: The courier left my parcel at the wrong address.
Label: shipping

Ticket: I'd like to exchange these boots for a bigger size.
Label: returns

Ticket: The password reset email never arrives and I can't log in.
Label: technical
```

**Sample:** `'My card was charged twice for order 4412.'` → `billing`

**What I learned:** The examples matter more than the instructions. They show the model
the exact output format (just the lowercase word), which is what the check compares
against, and they cover the confusing cases, like a charge question being billing and
not returns.

## 2. Chain of thought (`chain_of_thought.py`)

**Final prompt:**

```text
You are a support agent deciding whether an order is eligible for a refund under the policy below.

Think step by step. Check every rule in the policy, one per line, in this format:
1. Within 30 days? <how many days ago it was bought> -> PASS or FAIL
2. Unused / original condition? <what the order says> -> PASS or FAIL
3. Not a final-sale item? <what the order says> -> PASS or FAIL

If the order does not mention a detail, assume that rule passes (only a stated fact can fail a rule).
The refund is YES only if every rule passes. If any rule fails, it is NO.

After the steps, write the final line exactly as either
DECISION: YES
or
DECISION: NO
The DECISION line must be the very last line. Write nothing after it.
```

(The starter adds the refund policy after this.)

**Sample:** `'Bought 45 days ago, unused.'` → the model goes through the three rules, fails
the 30-day one, and ends with `DECISION: NO`.

**What I learned:** Making the model check each rule one by one stops it from jumping to
an answer. The fixed last line is what makes the result gradable. I also had to say what
to do when the order doesn't mention a rule (like final sale in the 45-day case), or the
model might treat "not mentioned" as a failure.

## 3. Tool calling (`tool_calling.py`)

**Tool description:** "Look up the current status of a customer's order (for example shipped, processing, or not found). Call this whenever the customer asks where an order is or what is happening with it."

**`order_id` description:** "The order number exactly as the customer wrote it, digits only, e.g. "4412"."

**Final prompt:**

```text
You are a support assistant for an online store.
You do not know the status of any order yourself. Whenever a customer mentions an order number or asks about an order, you MUST call the get_order_status tool with that order number before replying. Never guess or make up a status.
After you get the tool result, answer in one or two friendly sentences using that status.
```

**Sample:** `'Hi, can you check on order 4412 for me?'` → the model calls
`get_order_status(order_id="4412")` and gets `shipped, arriving Friday`.

**What I learned:** The model decides whether to use a tool mostly from the tool's
description, so it has to say *when* to call it, not just what it does. Saying "you do not
know the status yourself" also stops it from making up an answer instead of calling the
tool.

## 4. RAG (`rag.py`)

**Retriever:** simple keyword overlap. It lowercases everything, drops common words, and
counts how many question words match words in each help-center line, with prefix matching
so "ship" matches "shipping" and "internationally" matches "international". It returns the
top 3 lines that match at least one word.

```python
STOPWORDS = {
    "a", "an", "the", "do", "does", "did", "i", "you", "your", "we", "my", "me", "is", "are",
    "to", "of", "in", "on", "for", "and", "or", "how", "what", "what's", "when", "where",
    "can", "have", "has", "it", "item", "s",
}


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS}


def _related(a: str, b: str) -> bool:
    # Treat "ship" ~ "shipping" and "international" ~ "internationally" as matches.
    short, long_ = sorted((a, b), key=len)
    return short == long_ or (len(short) >= 4 and long_.startswith(short))


def YOUR_RETRIEVER(question: str, chunks: list[str], top_k: int = 3) -> list[str]:
    q_words = _words(question)
    scored = []
    for chunk in chunks:
        c_words = _words(chunk)
        score = sum(1 for q in q_words if any(_related(q, c) for c in c_words))
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]
```

**Final prompt:**

```text
You are a customer support assistant for an online store.
Answer the question using ONLY the information in the Context. Do not use outside knowledge and do not guess.
When the Context answers the question, reply in one or two sentences and reuse the key words and numbers from the Context.
If the Context is empty or does not contain the answer, reply exactly: I don't know. Do not add anything else in that case.
```

**Samples:**
- `'Do you ship internationally?'` → `yes, we offer international shipping to most
  countries. it takes 7-21 business days...`
- `"What's your CEO's home address?"` → the retriever finds nothing, and the model answers
  `i don't know.`

**What I learned:** Retrieval does half the work of preventing hallucination. If nothing
relevant is retrieved, the context is empty and the "say I don't know" rule kicks in. The
prompt has to give an exact refusal phrase, because "I'm not able to help with that"
wouldn't match the check even though it's a correct refusal.

## What I learned overall

LLMs are good at structured tasks when the structure is spelled out: an exact label set,
an exact last line, a tool schema with clear descriptions, or a context block to answer
from. They're basically really good at following a pattern you show them. Where they need
scaffolding is everything around that: they don't know an order's status unless you give
them a tool, they don't know the store's policy unless you retrieve it, and they'll
happily reason their way to an answer unless you force them to check each rule. Most of
the work in all four files was being very specific about the output format and about what
to do in the edge case, like a missing detail, no context, or no order info. That's the
same thing coding agents do with their system prompts and tool descriptions.
