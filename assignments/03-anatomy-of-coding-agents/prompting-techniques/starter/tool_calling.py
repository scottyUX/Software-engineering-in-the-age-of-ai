"""Tool calling — order lookup.

Task: the model must decide to call the `get_order_status` tool with the order id it
finds in the user's message, then use the returned status in a short reply.

Fill in YOUR_SYSTEM_PROMPT and the tool schema TODO.
Run:  python tool_calling.py
"""
from ollama import chat

MODEL = "llama3.1:8b"

FAKE_DB = {
    "4412": "shipped, arriving Friday",
    "9001": "processing",
}


def get_order_status(order_id: str) -> str:
    return FAKE_DB.get(order_id, "not found")


# TODO: describe the tool so the model knows when and how to call it.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Look up the current status of an existing order. Call this before answering an order-status question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "The order identifier from the customer message, as a string, for example 1234."},
                },
                "required": ["order_id"],
            },
        },
    }
]

# TODO: Fill this in! Tell the model to look up the order before answering.
YOUR_SYSTEM_PROMPT = "You are an online-store order support assistant.\nFor a request about an order's status, first call get_order_status.\nExtract the order identifier from the user's message and pass it as a string\ncontaining the identifier only, without the word \"order\", a # sign, or spaces.\nNever guess an order status or invent an identifier. If the identifier is missing,\nask the customer for it.\nAfter a tool result is provided, use only that result to give a short factual reply.\nIf the result is \"not found\", say the order was not found and ask the customer\nto check its identifier. Do not claim that a lookup succeeded before calling the tool."


def run() -> bool:
    message = "Hi, can you check on order 4412 for me?"
    resp = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": YOUR_SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        tools=TOOLS,
        options={"temperature": 0.0},
    )
    calls = resp.message.tool_calls or []
    if not calls:
        print("[FAIL] model did not call the tool")
        return False
    call = calls[0]
    order_id = str(call.function.arguments.get("order_id"))
    ok = order_id == "4412"
    print(f"[{'PASS' if ok else 'FAIL'}] tool called with order_id={order_id!r}")
    if ok:
        print("tool result:", get_order_status(order_id))
    return ok


if __name__ == "__main__":
    run()

