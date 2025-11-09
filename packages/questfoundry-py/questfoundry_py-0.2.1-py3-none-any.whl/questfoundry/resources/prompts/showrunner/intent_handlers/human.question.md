# Intent Handler — human.question

Inputs

- Envelope with `intent = human.question`, any role → SR.

Process

1. Validate payload fields: `question` (required), optional `context`, `suggestions`.
2. Present question to human (CLI/UI); capture answer or choice.
3. Emit `human.response` to original sender with `reply_to` and matching `correlation_id`.
4. `ack` the original question if transport expects ack.

Outputs

- `human.response` envelope; optional `ack`.

Notes

- Batch low-urgency questions at checkpoints; avoid chatty interaction.

References

- 04-protocol/INTENTS.md §5 Human Interaction Intents
