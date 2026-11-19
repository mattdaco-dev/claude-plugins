# Domain model

Objects the user knows, their relations and their lifecycles. No tables, keys or SQL types: the
technical design takes care of those.

## Objects

### Object

Definition in one sentence.

| Attribute | Business type | Required | Note | Status | Source |
|---|---|---|---|---|---|
| name | text, amount, date, reference to Other object… | yes | format, [BR-xx](features/slug.md) | Proposed | grill-me YYYY-MM-DD |

## Relations

| Object | Relation | Object | Cardinality (source → target) | Status | Source |
|---|---|---|---|---|---|
| Object | owns | Other object | 1:1 → 0:n | Proposed | … |

## Lifecycles

For each object that has a status.

### Object

| From | To | Event | Actor | Condition | Status | Source |
|---|---|---|---|---|---|---|
| (creation) | state | event | Role | [BR-xx](features/slug.md) | Proposed | … |
