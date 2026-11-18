# Week 10 Submission (AI-Native Teams): Mohanad Kadadou (2309115218)

Repository: https://github.com/mohanadkadadou/week10-llm-gateway

- **Gateway:** LiteLLM with one choke point; task-aware routing (easy to a small model, hard to a stronger one) and a one-shot fallback with a loop guard and a degrade path. All models run locally on Ollama, so no API keys exist or are committed. 6 unit tests plus a live fallback demo.
- **Measurements:** 10 inputs per task per strategy (latency, tokens, quality); dollar costs are projected with assumed hosted list prices and labelled as assumptions.
- **Policy:** hard task always on the strong model; easy task on the 3b model, because the 1b model got all three neutral reviews wrong; projected saving 12% at an 80/20 mix, with the honest note that the hard task dominates cost: [writeup.md](https://github.com/mohanadkadadou/week10-llm-gateway/blob/main/writeup.md).
