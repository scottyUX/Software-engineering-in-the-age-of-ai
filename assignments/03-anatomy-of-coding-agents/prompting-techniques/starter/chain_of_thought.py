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

YOUR_SYSTEM_PROMPT = """You are a refund eligibility checker for an online store.
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
