# Week 10 — AI-Native Teams: Gateway, Routing & Cost

**Estimated time: ~3 hours.**

## Overview
On an AI-native team, model calls are infrastructure. You'll route two LLM tasks through
a single **LLM gateway**, send an easy task to a cheap model and a hard task to a stronger
one with a fallback, then measure **cost and latency** and recommend a routing policy.

A skeleton is provided in [`starter/`](starter/) — you fill in the routing.

## Learning goals
- Put a gateway (LiteLLM) between your app and multiple models.
- Implement **task-aware routing** with a fallback.
- Measure cost/latency tradeoffs and justify a routing decision.

---

## Setup
```bash
cd starter && pip install -r requirements.txt
# set the keys your providers need, e.g. export OPENAI_API_KEY=...
python gateway_app.py
```
`gateway_app.py` has two tasks (sentiment = easy, bug-explanation = hard) and one
`call_model` choke point. You may point the easy model at a local **Ollama** model to
keep costs at zero.

## What to do (all three)
1. **Route.** Finish `route()` so the **easy** task uses `EASY_MODEL` and the **hard**
   task uses `HARD_MODEL`. Configure at least **two** models (a small/cheap one and a
   stronger one).
2. **Fallback.** Finish `call_model()` so a primary error/timeout falls back to
   `FALLBACK_MODEL` (guard against loops).
3. **Measure.** Run **10 inputs per task** through your routing and record, per route:
   **latency** and **cost per request** (use provider pricing; local = $0). Then state a
   routing policy that keeps quality acceptable while cutting cost, with the rough savings
   vs. "always use the strong model".

   > **Fallback measurement:** Treat a fallback as one end-to-end request.
   > Record the total latency from the primary attempt through the fallback
   > response. For cost, include the usage reported for each attempt when
   > available, and record fallback cases separately from normal routes.

## Deliverables
**Submit the GitHub repository link** for `starter/` and a `writeup.md`:
1. Your routing + fallback config (models and rules) — keys via env, **never committed**.
2. A results table: latency and cost per route across the 20 runs.
3. Your recommended routing policy and the projected savings.
4. **What you learned:** 3–5 sentences on treating model calls as team infrastructure.

## Evaluation (100 pts)
- 35 — Working task-aware routing across 2+ models through the gateway.
- 25 — Fallback on error/timeout.
- 25 — Honest latency/cost measurement with a defensible policy.
- 15 — `writeup.md`, no committed secrets, "what you learned".

## References
- LiteLLM: https://docs.litellm.ai/
