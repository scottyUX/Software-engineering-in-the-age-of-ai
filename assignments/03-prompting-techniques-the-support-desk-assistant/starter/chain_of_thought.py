"""Chain-of-thought — refund eligibility.

Task: given the refund policy and an order, decide YES or NO. Use chain-of-thought
so the model reasons step by step, but make the FINAL line exactly `DECISION: YES`
or `DECISION: NO` so it can be graded.

Only edit YOUR_SYSTEM_PROMPT.
Run:  python chain_of_thought.py
"""
from ollama import chat

MODEL = "llama3.1:8b"

POLICY = """Refund policy:
- Refunds allowed within 30 days of purchase.
- Item must be unused / in original condition.
- Final-sale items are never refundable.
"""

# TODO: Fill this in! Encourage step-by-step reasoning, ending with DECISION: YES/NO.

YOUR_SYSTEM_PROMPT = """
You are a customer support assistant for an online store.
Your task is to determine whether a customer is eligible for a refund
based strictly on the provided refund policy.

Evaluate each order step by step using these rules:

Step 1: Check whether the purchase was made within 30 days.
If more than 30 days have passed, the refund is not allowed.

Step 2: Check whether the item is unused and in its original condition.
If the item has been used or is not in its original condition,
the refund is not allowed.

Step 3: Check whether the item was marked as final sale.
Final-sale items are never eligible for a refund.

Step 4: Make the final decision.
A refund is allowed only when all three conditions are satisfied.

Explain your evaluation briefly, step by step.

Your final line must be exactly one of the following:
DECISION: YES
DECISION: NO

Do not write anything after the final decision.
"""


CASES = [
    ("Bought 10 days ago, unused, not final sale.", "YES"),
    ("Bought 45 days ago, unused.", "NO"),
    ("Bought 5 days ago but it was a final-sale item.", "NO"),
]


def decide(system_prompt: str, order: str) -> str:
    resp = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt + "\n" + POLICY},
            {"role": "user", "content": order},
        ],
        options={"temperature": 0.0},
    )
    text = resp.message.content.strip()
    last = text.splitlines()[-1].upper() if text else ""
    return "YES" if "DECISION: YES" in last else "NO" if "DECISION: NO" in last else "?"


def run() -> bool:
    passed = 0
    for order, expected in CASES:
        got = decide(YOUR_SYSTEM_PROMPT, order)
        ok = got == expected
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {order!r} -> {got}, expected {expected}")
    print(f"{passed}/{len(CASES)} correct")
    return passed == len(CASES)


if __name__ == "__main__":
    run()
