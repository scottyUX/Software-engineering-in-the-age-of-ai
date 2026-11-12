"""RAG — policy-grounded answers.

Task: answer a customer question using ONLY the retrieved help-center text. If the
answer isn't in the docs, the model must say it doesn't know (don't hallucinate).

Fill in YOUR_SYSTEM_PROMPT and YOUR_RETRIEVER.
Run:  python rag.py
"""
import os
import re

from ollama import chat

MODEL = "llama3.1:8b"
DATA = os.path.join(os.path.dirname(__file__), "data", "help_center.txt")


def load_chunks() -> list[str]:
    with open(DATA, encoding="utf-8") as f:
        # one chunk per non-empty line
        return [line.strip() for line in f if line.strip()]


# Retriever: keyword overlap between the question and each help-center line.
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


# System prompt: answer only from the provided context.
YOUR_SYSTEM_PROMPT = """You are a customer support assistant for an online store.
Answer the question using ONLY the information in the Context. Do not use outside knowledge and do not guess.
When the Context answers the question, reply in one or two sentences and reuse the key words and numbers from the Context.
If the Context is empty or does not contain the answer, reply exactly: I don't know. Do not add anything else in that case."""

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
