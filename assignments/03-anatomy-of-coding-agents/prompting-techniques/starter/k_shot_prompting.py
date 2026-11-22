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

YOUR_SYSTEM_PROMPT = """You are a ticket router for an online store's support desk.
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
Label: other"""

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
