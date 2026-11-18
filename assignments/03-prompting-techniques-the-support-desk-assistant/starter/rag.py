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


# TODO: return the subset of chunks relevant to `question` (simple keyword overlap is fine).

def YOUR_RETRIEVER(question: str, chunks: list[str]) -> list[str]:
    import re

    stop_words = {
        "a", "an", "the", "is", "are", "do", "does",
        "i", "you", "your", "my", "me", "we", "to",
        "for", "of", "in", "on", "and", "or", "what",
        "how", "long", "have", "can", "it", "our"
    }

    def keywords(text):
        words = re.findall(r"[a-z]+", text.lower())
        return {
            word for word in words
            if word not in stop_words and len(word) > 2
        }

    question_words = keywords(question)
    results = []

    for chunk in chunks:
        chunk_words = keywords(chunk)
        score = len(question_words & chunk_words)

        if score > 0:
            results.append((score, chunk))

    results.sort(key=lambda item: item[0], reverse=True)
    return [chunk for score, chunk in results[:3]]



# TODO: Fill this in! Force the model to answer only from the provided context.

YOUR_SYSTEM_PROMPT = """
You are a helpful customer support assistant for an online store.

Your task is to answer customer questions using ONLY the information
provided in the Context section.

Follow these rules:
1. Read the provided Context carefully.
2. Answer the customer's question using only facts explicitly
   stated in the Context.
3. Do not use outside knowledge or make assumptions.
4. Never invent policies, personal information, or missing details.
5. If the Context does not contain enough information to answer
   the question, politely say:
   "I don't know based on the available help-center information."
6. If the Context is empty, use the same response.
7. Keep answers short, clear, accurate, and friendly.
8. Do not mention information that is unrelated to the question.

Remember: The Context is your only source of information.
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
