# Streams Table (Template)

Use this table **only for medium/complex tasks**.
For simple tasks, a streams table is **optional**.

## Streams Table

| stream_id | goal | inputs | write_zone | deps | owner (agent/template) | artifacts | verify | risk |
|---|---|---|---|---|---|---|---|---|
| S1 |  |  |  |  |  |  |  |  |

## Rules

- If two streams write to the same write_zone, they are **not parallel**; either split write zones or serialize.
- Each stream must have an explicit erify step.
- Keep streams independent; minimize shared mutable state.