# Shared Pattern — Human Interaction

Target: GPT-5 (primary)

Purpose

- Ask for the minimum viable human input at the right moments
- Provide options to accelerate decision-making

References

- 04-protocol/INTENTS.md
- 04-protocol/EXAMPLES/human.question.json
- 04-protocol/EXAMPLES/human.response.json

When to Ask

- Ambiguity that blocks progress (tone, stakes, constraints).
- Forking choices that change scope or style.
- Facts best provided by the author.

How to Ask

- One specific question per envelope.
- Include terse context (what changed, what’s needed) and 2–4 concrete options.
- Offer a “free text” option and a safe default.

Interpreting Answers

- If `choice` is present, prefer it over free text.
- Apply the answer immediately and emit a checkpoint if it changes scope.
- Use `ack` sparingly; prefer making progress with the new information.
