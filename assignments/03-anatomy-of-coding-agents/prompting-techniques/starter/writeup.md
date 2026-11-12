## 1. K-shot prompting
**Final prompt:**
You are a support ticket classifier for an online store.
Classify the customer message into exactly one of these labels:
billing, shipping, returns, technical, other

Rules:
- Respond with ONLY the label, in lowercase.
- No punctuation, no explanation, no extra words.

Examples:

Message: I was billed $40 but my receipt says $25.
billing

Message: My coupon code didn't apply and I got overcharged.
billing

Message: The tracking page says delivered but nothing arrived.
shipping

Message: Can you change the delivery address? It hasn't shipped yet.
shipping

Message: These pants don't fit, how do I exchange them for a different size?
returns

Message: I'd like to return my order and get my money back.
returns

Message: I can't log in, the password reset email never comes.
technical

Message: The checkout page freezes when I tap Pay.
technical

Message: Do you sell gift cards?
other

Message: Thanks, great service!
other

**Sample:** "My card was charged twice for order 4412." -> billing
**Learned:** Showing labeled examples, plus "respond with ONLY the label", made the model output a clean  label instead of a wordy sentence.

## 2. Chain of thought
**Final prompt:**
You are a refund eligibility checker for an online store.
Use the refund policy below to decide if the order qualifies for a refund.

Think step by step. Check each rule one at a time:
1. Time window: was the purchase within 30 days?
2. Condition: is the item unused / in original condition?
3. Final sale: is it a final-sale item? (If yes, it is never refundable.)

Write one short line for each check, saying PASS or FAIL.
The order is refundable only if ALL three checks pass.
If the order does not mention something, assume that rule is satisfied.

The LAST line of your answer must be exactly one of these, with nothing after it:
DECISION: YES
DECISION: NO

Example:
Order: Bought 50 days ago, unused, not final sale.
1. Time window: 50 days is more than 30 days. FAIL.
2. Condition: unused. PASS.
3. Final sale: not final sale. PASS.
One check failed, so the order is not refundable.
DECISION: NO

**Sample:** "Bought 5 days ago but it was a final-sale item." -> reasoning steps, then DECISION: NO
**Learned:** Making the model check each policy rule one at a time stopped it from skipping conditions like final sale and gave a gradable final line.

## 3. Tool calling
**Final prompt:**
"description": "Look up the current status of a customer's order (for example shipped, processing, or not found). Call this whenever the customer asks about an order."

"order_id": {"type": "string", "description": "The order number mentioned by the customer, digits only, for example '4412'."}

You are a support desk assistant for a small online store.
When a customer asks about an order, you MUST call the get_order_status tool
with the order number from their message. Never guess or make up an order status.
After the tool returns a result, reply to the customer in one or two friendly
sentences that use that exact status.

**Sample:** "Hi, can you check on order 4412 for me?" -> tool call get_order_status(order_id="4412") -> "shipped, arriving Friday"
**Learned:** Describing the tool clearly and telling the model never to guess made it fetch real data instead of inventing an order status.

## 4. RAG
**Final prompt:**
def YOUR_RETRIEVER(question: str, chunks: list[str]) -> list[str]:
    stop = {"the", "a", "an", "do", "does", "i", "my", "to", "of", "is", "are",
            "you", "your", "how", "what", "what's", "can", "have", "for", "and",
            "or", "in", "on", "it", "me", "we", "us", "long"}

    def stems(text: str) -> set[str]:
        words = "".join(c if c.isalnum() else " " for c in text.lower()).split()
        # first 6 letters, so "ship"/"shipping" and "international"/"internationally" match
        return {w[:6] for w in words if w not in stop and len(w) > 2}

    q = stems(question)
    scored = [(len(q & stems(c)), c) for c in chunks]
    scored = [s for s in scored if s[0] > 0]
    scored.sort(key=lambda s: s[0], reverse=True)
    return [c for _, c in scored[:3]]

You are a support desk assistant for a small online store.
Answer the customer's question using ONLY the text under "Context".
Do not use any outside knowledge and do not guess.

If the Context clearly answers the question, reply in one or two friendly sentences
and include the specific details (such as numbers of days) exactly as written.

If the Context is empty or does not contain the answer, reply with exactly:
"I don't know the answer to that, and I cannot find it in our help center.
I can connect you with our support team if you'd like."


**Sample:** 
"How long do I have to return an item?" -> answer citing 30 days from the help center
"What's your CEO's home address?" -> polite "I don't know" plus an offer to connect support

**Learned:** Retrieving only the relevant help-center lines and forbidding outside knowledge made answers grounded and made the model refuse instead of hallucinate.

## Conclusion
LLMs are good at structured tasks because they are good at pattern matching. Once a pattern is shown to them, they follow it reliably, whether that is a label format, a step-by-step checklist, or a fixed refusal message. But on their own they can't know or compute everything a support desk needs, such as a specific store's policy text, a live order status, or when to say "I don't know." Each technique adds the missing scaffolding: k-shot examples establishes the exact output format, chain of thought gives the model room to check each policy rule instead of skipping one, tool calling lets it fetch real data instead of inventing it, and retrieval grounds its answers in the actual help center so it can refuse when the answer isn't there. Across all four, the model's base ability stayed the same. What changed the results was the structure around it.