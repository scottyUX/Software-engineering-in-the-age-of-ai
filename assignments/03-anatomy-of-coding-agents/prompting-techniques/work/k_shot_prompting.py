"""K-shot prompting — ticket classification.

Task: classify a customer message into one of: billing, shipping, returns,
technical, other. Use in-context EXAMPLES (k-shot) so the model outputs exactly the
label, lowercase, with no extra text.

Only edit YOUR_SYSTEM_PROMPT.
Run:  python k_shot_prompting.py
"""
from ollama import chat

MODEL = "llama3.1:8b"
NUM_RUNS = 5

# System prompt with labeled examples (k-shot).
YOUR_SYSTEM_PROMPT = """You classify customer support tickets for an online store.

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
Label: technical"""

CASES = [
    ("My card was charged twice for order 4412.", "billing"),
    ("Where is my package? It's been two weeks.", "shipping"),
    ("I want to send the shoes back for a refund.", "returns"),
    ("The app crashes every time I open my cart.", "technical"),
]


def classify(system_prompt: str, message: str) -> str:
    resp = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
        options={"temperature": 0.0},
    )
    return resp.message.content.strip().lower()


def run() -> bool:
    passed = 0
    for message, expected in CASES:
        got = classify(YOUR_SYSTEM_PROMPT, message)
        ok = got == expected
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {message!r} -> got {got!r}, expected {expected!r}")
    print(f"{passed}/{len(CASES)} correct")
    return passed == len(CASES)


if __name__ == "__main__":
    run()
