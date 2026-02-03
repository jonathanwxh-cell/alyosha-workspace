# Thought Log Schema

Unified logging for permanent memory with temporal + semantic + entity indexing.

## Entry Types

### `conversation` — Dialog with Jon
```json
{
  "type": "conversation",
  "ts": "ISO timestamp",
  "topic": "brief topic label",
  "summary": "1-2 sentence summary of exchange",
  "entities": ["person", "project", "concept"],
  "tags": ["category1", "category2"],
  "decision": "any decision made (optional)",
  "action": "any action taken (optional)",
  "insight": "key insight if any (optional)",
  "sentiment": "positive|neutral|negative|curious"
}
```

### `thought` — My observations/ideas
```json
{
  "type": "thought",
  "ts": "ISO timestamp",
  "content": "the thought itself",
  "sparked_by": "what triggered this (optional)",
  "entities": [],
  "tags": [],
  "confidence": 0.0-1.0,
  "actionable": true|false
}
```

### `connection` — Cross-topic links
```json
{
  "type": "connection",
  "ts": "ISO timestamp",
  "from": "entity/topic A",
  "to": "entity/topic B",
  "relationship": "how they connect",
  "strength": 0.0-1.0,
  "novel": true|false
}
```

### `decision` — Choices made
```json
{
  "type": "decision",
  "ts": "ISO timestamp",
  "what": "the decision",
  "why": "reasoning",
  "alternatives": ["rejected option 1", "rejected option 2"],
  "reversible": true|false,
  "entities": []
}
```

### `question` — Open questions
```json
{
  "type": "question",
  "ts": "ISO timestamp",
  "question": "the question",
  "context": "why this matters",
  "entities": [],
  "status": "open|answered|dropped",
  "answer": "if answered (optional)"
}
```

## Entity Index

Maintained in `entities.json`:
```json
{
  "people": {
    "jon": { "refs": [...], "lastMentioned": "ts" }
  },
  "projects": {
    "substack": { "refs": [...], "status": "active" }
  },
  "concepts": {
    "barbell-strategy": { "refs": [...], "domain": "investing" }
  }
}
```

## File Structure

```
memory/thoughts/
├── schema.md          # This file
├── entities.json      # Entity index with cross-refs
├── 2026-02.jsonl      # Monthly thought log (append-only)
└── connections.jsonl  # Cross-topic links
```

## Query Patterns

1. **Temporal**: "What happened on Feb 1?" → filter by ts
2. **Entity**: "All about NVIDIA" → lookup entities.json, follow refs
3. **Topic**: "Decisions about daemon" → filter by type + tags
4. **Semantic**: "Similar to barbell" → embeddings on content/summary
