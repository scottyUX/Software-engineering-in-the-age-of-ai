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


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": (
                "Look up the current status of a customer's order (e.g. processing, "
                "shipped, delivery date). Call this only when the customer's message "
                "contains an order number. If there is no order number, do not call this "
                "tool; ask the customer for it instead. Never guess an order's status."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": (
                            "The order number copied from the customer's message, digits "
                            "only, without '#' or the word 'order'. Only use a number the "
                            "customer actually wrote; never make one up."
                        ),
                    },
                },
                "required": ["order_id"],
            },
        },
    }
]

YOUR_SYSTEM_PROMPT = """You are a support assistant for an online store.
When a customer asks about an order, first call the get_order_status tool with the order
number from their message. Do not answer from memory and do not invent a status.
After you receive the tool result, reply in one or two friendly sentences that state the
status exactly as the tool returned it. If the customer did not give an order number, ask
for it instead of calling the tool."""


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
