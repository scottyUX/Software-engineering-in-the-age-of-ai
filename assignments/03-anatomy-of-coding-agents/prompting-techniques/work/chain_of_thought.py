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

# System prompt: step-by-step rule check, ending with DECISION: YES/NO.
YOUR_SYSTEM_PROMPT = """You are a support agent deciding whether an order is eligible for a refund under the policy below.

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
The DECISION line must be the very last line. Write nothing after it."""

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
