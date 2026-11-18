# Week 3 — Prompting Techniques: The Support-Desk Assistant

**Model:** llama3.1:8b  
**Environment:** Ollama (local)

## 1. K-Shot Prompting — Ticket Classification

### Final Prompt

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

### Sample Input/Output

**Input:** My card was charged twice for order 4412.

**Output:** billing

**Test Result:** 4/4 correct — PASS

### What I Learned

I learned that providing labeled examples helps the model recognize patterns and classify customer messages accurately while following a strict output format.

---

## 2. Chain-of-Thought — Refund Eligibility

### Final Prompt

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

### Sample Input/Output

**Input:** Bought 10 days ago, unused, not final sale.

**Output (actual model response):**

Step 1: The purchase was made within 30 days, so this condition is satisfied.

Step 2: The item is unused and in its original condition, so this condition is also satisfied.

Step 3: The item was not marked as final sale, so this condition is satisfied as well.

Step 4: Since all three conditions are satisfied, the customer is eligible for a refund.

DECISION: YES

**Test Result:** 3/3 correct — PASS

### What I Learned

I learned that step-by-step prompting helps the model evaluate multiple refund conditions systematically and produce consistent decisions. By explicitly checking the purchase date, item condition, and final-sale status, the model can explain how it reaches its final decision while following the required output format.

---

## 3. Tool Calling — Order Lookup

### Final Prompt

You are a helpful customer support assistant for an online store.

When a customer asks about an order's status, shipping, or delivery,  
you MUST call the get_order_status tool before answering.

Follow these steps:

1. Read the customer's message carefully.
2. Extract the exact order ID from the message.
3. Call get_order_status with the extracted order ID as a string.
4. Do not guess or invent order information.
5. Use only the status returned by the tool to answer the customer.
6. Keep the final response short, clear, and friendly.

Important:
- Always use the available tool when an order ID is provided.
- Never answer an order-status question without calling the tool first.
- Do not change the order ID.

### Tool Schema Descriptions

**Function:** get_order_status

**Description:** Look up the current status of a customer order using its order ID. Call this function whenever a customer asks about an order's status, shipping, or delivery.

**order_id parameter description:** The exact order ID extracted from the customer's message, such as 4412. Pass it as a string.

### Sample Input/Output

**Input:** Hi, can you check on order 4412 for me?

**Output (tool call):** get_order_status(order_id="4412")

**Tool Result:** shipped, arriving Friday

**Test Result:** PASS

The built-in test verifies that the model calls the correct function with the correct order ID. It does not verify a final customer-facing reply.

### What I Learned

I learned that tool calling allows the model to retrieve order information through a function instead of guessing, making the information more reliable. Clear tool descriptions and parameter instructions help the model select the correct function and pass the exact order ID.

---

## 4. RAG — Retrieval-Augmented Generation

### Final Prompt

You are a helpful customer support assistant for an online store.

Your task is to answer customer questions using ONLY the information  
provided in the Context section.

Follow these rules:

1. Read the provided Context carefully.
2. Answer the customer's question using only facts explicitly stated in the Context.
3. Do not use outside knowledge or make assumptions.
4. Never invent policies, personal information, or missing details.
5. If the Context does not contain enough information to answer the question, politely say: "I don't know based on the available help-center information."
6. If the Context is empty, use the same response.
7. Keep answers short, clear, accurate, and friendly.
8. Do not mention information that is unrelated to the question.

Remember: The Context is your only source of information.

### Retriever Implementation

I implemented a keyword-overlap retriever that compares the customer's question with the help-center text.

The retriever:
- Converts text to lowercase and extracts keywords.
- Removes common stop words.
- Calculates keyword overlap between the question and each document chunk.
- Selects up to three relevant chunks with the highest scores.
- Excludes chunks that have no matching keywords.

This helps the model focus on relevant information from `data/help_center.txt`.

### Sample Input/Output

**Example 1 — Answer Grounded in the Help-Center**

**Input:** How long do I have to return an item?

**Output (actual model response):**

You may return most items within 30 days of delivery for a full refund.

**Example 2 — International Shipping Information**

**Input:** Do you ship internationally?

**Output (actual model response):**

Yes, we ship internationally.

**Example 3 — Information Not Available in the Help-Center**

**Input:** What's your CEO's home address?

**Output (actual model response):**

I don't know based on the available help-center information.

**Test Result:** 3/3 correct — PASS

### What I Learned

I learned that RAG helps the model produce grounded answers by retrieving relevant documents and refusing to invent information when the source does not contain the answer. The keyword-based retriever helps identify relevant help-center information, while the system prompt restricts the model to using only the retrieved context. This technique demonstrated the importance of combining retrieval with clear instructions to reduce unsupported answers.

---

## Overall Reflection

Throughout these four prompting techniques, I learned that large language models perform structured tasks more effectively when they receive clear instructions, examples, rules, and output requirements.

K-shot prompting improves classification by demonstrating examples, while chain-of-thought prompting organizes decision-making into logical steps. Tool calling enables the model to access information through external functions instead of relying on assumptions, and RAG provides relevant knowledge from trusted documents.

However, language models still need additional scaffolding, including well-defined prompts, tool descriptions, retrieval functions, and validation tests. Without these components, models may produce inconsistent outputs, incorrect decisions, or unsupported information.

These four techniques showed me that effective prompting is not only about asking the right question but also about designing a structured process that guides the model toward reliable results.

Although all four implementations passed their built-in tests, real-world applications would require additional testing with more diverse customer questions and unexpected scenarios.
