# Week 3 Prompting Techniques Submission: Mehmet Emin Akkaya

**Project repository:** https://github.com/mehmeteminakkaya/week3-prompting-techniques

## Summary

All four checks pass with `llama3.1:8b` running locally on Ollama (temperature 0).

| Technique | Result |
| --- | --- |
| K-shot prompting | 4/4 checks passed |
| Chain-of-thought | 3/3 checks passed |
| Tool calling | `get_order_status` called with `order_id='4412'`; full round trip verified |
| RAG | 3/3 checks passed, including the polite refusal for the out-of-scope question |

The repository contains the four completed starter files, [`writeup.md`](https://github.com/mehmeteminakkaya/week3-prompting-techniques/blob/main/writeup.md)
(final prompts, sample input/output, a no-technique baseline for each task, and what I learned),
and the raw check output in `final_runs.txt`.

Part 1 of Week 3 (Gemini CLI dissection) is a separate pull request: #132.
