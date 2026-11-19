# Week 6 submission: Berke Eren Akçay

Repository: https://github.com/berkekcay/habit-tracker-review

- Guardrails: black, ruff and pytest locally and in GitHub Actions. A branch with a
  deliberately failing test shows CI failing the build.
- Two features, each on its own branch and PR with the agent's one-shot commit and my review
  fixes as separate commits: validation
  ([#1](https://github.com/berkekcay/habit-tracker-review/pull/1)) and streak
  ([#2](https://github.com/berkekcay/habit-tracker-review/pull/2)).
- AI reviewer: CodeRabbit (Copilot review was out of quota). Its comments are visible on
  both PRs.

To compare fairly, I also ran CodeRabbit on the agent-only commits (closed PRs #3 and #4). It
found none of the three problems my manual review caught, but it did catch a stale README
line I missed. The comparison and what I learned are in
[writeup.md](https://github.com/berkekcay/habit-tracker-review/blob/main/writeup.md).
