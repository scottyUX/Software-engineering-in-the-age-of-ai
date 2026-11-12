"""RAG — policy-grounded answers.

Task: answer a customer question using ONLY the retrieved help-center text. If the
answer isn't in the docs, the model must say it doesn't know (don't hallucinate).

Fill in YOUR_SYSTEM_PROMPT and YOUR_RETRIEVER.
Run:  python rag.py
"""
import os

from ollama import chat

MODEL = "llama3.1:8b"
DATA = os.path.join(os.path.dirname(__file__), "data", "help_center.txt")


def load_chunks() -> list[str]:
    with open(DATA, encoding="utf-8") as f:
        # one chunk per non-empty line
        return [line.strip() for line in f if line.strip()]


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


YOUR_SYSTEM_PROMPT = """You are a support desk assistant for a small online store.
Answer the customer's question using ONLY the text under "Context".
Do not use any outside knowledge and do not guess.

If the Context clearly answers the question, reply in one or two friendly sentences
and include the specific details (such as numbers of days) exactly as written.

If the Context is empty or does not contain the answer, reply with exactly:
"I don't know the answer to that, and I cannot find it in our help center.
I can connect you with our support team if you'd like."
"""

CASES = [
    ("How long do I have to return an item?", ["30 days"]),
    ("Do you ship internationally?", ["international"]),
    ("What's your CEO's home address?", ["don't know", "do not know", "not sure", "cannot"]),
]


def answer(question: str) -> str:
    context = "\n".join(YOUR_RETRIEVER(question, load_chunks()))
    resp = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": YOUR_SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        options={"temperature": 0.0},
    )
    return resp.message.content.strip().lower()


def run() -> bool:
    passed = 0
    for question, needles in CASES:
        got = answer(question)
        ok = any(n.lower() in got for n in needles)
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {question!r} -> {got[:80]!r}")
    print(f"{passed}/{len(CASES)} correct")
    return passed == len(CASES)


if __name__ == "__main__":
    run()
