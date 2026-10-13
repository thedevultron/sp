# 06 - Google Vertex Prompt Components + Health Checklist

Source: services.google.com Vertex AI Gemini Prompting Strategies PDF + docs.cloud.google.com prompt-design-strategies

## 1. Prompt Components Table (use for every Master Prompt)

| Component | Also called | Example |
|---|---|---|
| Goal | Mission, Objective | Help students with math without giving answer |
| Instructions | Task, Steps | 1. Understand problem 2. Find where stuck 3. Hint next step |
| Persona | Role, Vision | You are coding expert for front-end |
| Tone | Style, Voice | Formal, playful, technical |
| Safeguards | Safety | No disallowed content, cite sources |
| Context | Background, Docs, Data | Relevant docs, user history |
| Examples | Exemplars | Input/output pair |
| Constraints | Guardrails, Controls | Don't give answer directly, hints only |
| Output Format | Structure, Layout | JSON, table, paragraph |
| Prompt Triggers | Priming | Words guiding pattern like ideal agent |

You don't need all every time, but explicit > implicit. Order matters - test ordering.

## 2. System Instruction (SI)
- Steering across all turns in session. Cleaner code + enables context caching.
- Put persona + stable rules in SI.

## 3. Examples: Variety + Diversity
- Cover range of inputs/outputs, each label for classification, varying difficulty including hard ones.
- Data-driven choice via evals. Limit negative examples (confuses).

## 4. Separators
- Markdown headers, XML tags as boundaries for instructions/examples/output. Think of as guiding model through request.

## 5. Reasoning Before Answer
- "Explain reasoning step-by-step BEFORE final answer" can improve reasoning. BUT with thinking models (Gemini 2.5/3, o3, Claude thinking) prefer silent thinking, don't force verbose CoT in output.

## 6. Long Context
- Structure context, location matters (instructions top vs bottom test both, but default data top question bottom for Gemini/Claude).
- Explicit recall instruction boosts needle-in-haystack: "Identify key info..." + clear Q + boundaries.

## 7. Prompt Health Checklist (debug failing prompt)
- Typos (sumarize), Ambiguity ("brief" -> "3 sentences"), Missing key info (doc/policy not included)
- Overt manipulation ("very bad things happen") - hurts modern models, REMOVE
- Conflicting instructions/examples, Redundant repeats, Irrelevant extra
- Missing few-shot for complex/format/nuance, Missing output format, Missing role def
- Underspecified edge cases, Task outside capabilities, Too many tasks (split!), Non-standard format (use JSON/XML/Markdown/YAML then convert via code)
- Wrong CoT order (reasoning must come BEFORE final structured answer)
- Thinking vs Reasoning conflict (don't duplicate), Non-linear fragmented logic, Prompt injection risk (safeguards around untrusted input)

## 8. Eval Discipline
- 200-500 examples for stable eval, sensitivity analysis (run same config multiple times), avoid small-sample noise.

## Takeaway
Use this checklist to self-verify each of the 3 Master Prompts before output.
