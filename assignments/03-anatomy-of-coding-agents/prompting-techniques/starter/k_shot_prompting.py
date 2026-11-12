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

YOUR_SYSTEM_PROMPT = """You are a support ticket classifier for an online store.
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
"""

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
