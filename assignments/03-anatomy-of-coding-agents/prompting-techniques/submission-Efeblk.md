# Week 3 Prompting Techniques Submission: Efeblk

Repository: https://github.com/Efeblk/week3-prompting-techniques

- Model: `llama3.1:8b` through Ollama; only the `TODO` parts were changed.
- `k_shot_prompting.py`: 5-shot prompt (one example per label) with a bare-label output rule. 4/4 pass.
- `chain_of_thought.py`: walks the three refund-policy conditions in order and ends on `DECISION: YES` or `DECISION: NO`. 3/3 pass.
- `tool_calling.py`: tool and parameter descriptions plus a system prompt that asks for a digits-only `order_id`. The model calls `get_order_status(order_id="4412")`. Pass.
- `rag.py`: keyword retriever with stopword removal and prefix matching, and a prompt that answers only from the retrieved context or refuses. 3/3 pass.
- Program output for each script is in `outputs/`.
- `writeup.md` has each technique's final prompt, a sample input/output and the prompt iterations that failed.
