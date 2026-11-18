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

# TODO: Fill this in! Include a few labeled examples (k-shot) in the system prompt.

YOUR_SYSTEM_PROMPT = """
You are a customer support ticket classifier for an online store.

Classify each customer message into exactly one category:
- billing: payments, charges, invoices, or payment problems.
- shipping: delivery, tracking, packages, or shipping delays.
- returns: refunds, returning items, or exchanges.
- technical: app errors, website bugs, or login problems.
- other: messages that do not match any category.

Examples:
Customer: I was charged twice for my purchase.
Category: billing

Customer: My package has not arrived yet.
Category: shipping

Customer: I need to return a jacket and get my money back.
Category: returns

Customer: The website freezes when I try to check out.
Category: technical

Customer: Do you have any job openings?
Category: other

Now classify the customer's message.

Important rules:
- Respond with only one category label.
- Use lowercase letters.
- Do not include explanations, punctuation, or extra words.
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
