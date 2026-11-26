# Assignment 3 Writeup: Anatomy of Coding Agents

## 1. K-Shot Prompting (`k_shot_prompting.py`)

* **Final Prompt:**
YOUR_SYSTEM_PROMPT = """Classify the customer message into exactly one of these labels: billing, shipping, returns, technical, or other.
Output ONLY the lowercase label name with no additional words, prefixes, or punctuation.

Input: Where is my order?
shipping

Input: My card was charged twice.
billing

Input: The app crashes when opening settings.
technical

Input: I want to return this shirt for a refund.
returns

Input: What time is your store open?
other
"""

Sample Input/Output:

Input: "My card was charged twice for order 4412."

Output: billing

What I Learned: I noticed that adding concrete examples makes a huge difference. Instead of the model giving me full conversational sentences or weird formatting, giving it few-shot examples forced it to output just the clean, raw label name every single time.

2. Chain-of-Thought (chain_of_thought.py)
Final Prompt:

Plaintext
You are a helpful customer support assistant evaluating refund requests against the policy.

Follow these instructions strictly:
1. Think step-by-step to evaluate if the customer request meets all refund policy criteria.
2. Provide your step-by-step reasoning first.
3. Conclude your response on a new line with exactly 'DECISION: YES' or 'DECISION: NO'.

Example:
Reasoning: The item was purchased 15 days ago, is unused, and was not a final-sale item. This satisfies all policy requirements.
DECISION: YES
Sample Input/Output:

Input: "Bought 10 days ago, unused, not final sale."

Output:

Plaintext
Reasoning: The item was purchased 10 days ago, which is within the 30-day window, is unused, and is not a final-sale item.
DECISION: YES
What I Learned: Making the LLM "think out loud" before jumping to a final answer completely changes its performance. When I forced it to lay out its reasoning step-by-step first, it stopped making quick, buggy assumptions on policy evaluation cases.

3. Tool Calling (tool_calling.py)
Final Prompt & Tool Definition:

Plaintext
YOUR_SYSTEM_PROMPT = """You are a customer support assistant with access to tools.
When a user asks about an order status, call the 'get_order_status' tool with their order ID.
Once you receive the status, provide a short reply to the user."""

Tool Parameters:
"order_id": {"type": "string", "description": "The order ID string."}
"required": ["order_id"]
Sample Input/Output:

Input: "What is the status of order 4412?"

Output: Executed get_order_status(order_id='4412') returning "shipped, arriving Friday".

What I Learned: Defining clear JSON parameters and tool descriptions gives the model a explicit operational boundary. It stops the model from hallucinating fake order data and forces it to execute the defined function to retrieve facts.

4. Retrieval-Augmented Generation (rag.py)
Final Prompt:

Plaintext
You are a helpful customer support assistant.
Answer the user's question using ONLY the provided retrieved context below.

Rules:
1. Base your answer strictly on facts present in the retrieved context.
2. If the answer cannot be determined from the provided context, reply exactly with: "I do not know"
Sample Input/Output:

Input: "What's your CEO's home address?"

Output: "I do not know"

What I Learned: Without strict grounding instructions and exact fallback rules, LLMs will attempt to answer missing information using outside pre-trained knowledge or guesses. Dictating a strict fallback string prevents hallucinations entirely.
