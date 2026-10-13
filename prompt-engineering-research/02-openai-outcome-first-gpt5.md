# 02 - OpenAI Outcome-First Prompting (GPT-5.5 / 5.6 Sol Guide)

Source: developers.openai.com/api/docs/guides/prompt-guidance + prompting guidance GPT-5.6

## 1. Simplify First
- GPT-5.5+ works best when you define OUTCOME and leave room for path. Shorter, outcome-oriented > long legacy process specs.
- Remove over-specification carried from older models. It adds noise, narrows search.
- Describe what good looks like, constraints, evidence, final shape.

## 2. Personality vs Collaboration vs Goal
- Personality = how it sounds (tone, warmth, directness).
- Collaboration = how it works (when to ask, when to assume, proactivity, checking).
- Keep both short. Neither replaces goals, success criteria, tool rules, stop conditions.
- Default is efficient/direct. For customer-facing, explicitly define both.

## 3. Preamble for Streaming
- For tool-heavy tasks, start with short visible update: "Got it, I'll do X first..." Improves perceived responsiveness.

## 4. Outcome-First + Stop Rules
- Avoid ALWAYS/NEVER/must/only for judgment calls. Reserve for true invariants (safety, required fields).
- For judgment: prefer decision rules ("Search when... Ask when...").
- Always add explicit stopping conditions: when to retry, fallback, abstain, ask, stop.
- Retrieval budget: "Stop after 5 sources or when 2 agree" - prevents endless search.

## 5. Grounding & Citations
- Define what needs support, what counts as enough evidence, behavior when missing (absence != factual no).
- Creative guardrails: tell which claims must come from sources vs may be invented.

## 6. Check Work
- Give tools to validate (run tests, lint, check JSON). "Verify before finishing against [criteria]".

## 7. Suggested Structure (use for Master Prompt)
```
Role: [1-2 sentences function + context + job]
Goal: [outcome + audience]
# Success criteria
[what must be true]
# Constraints
[policy, safety, business, evidence, side-effect limits]
# Output
[sections, length, tone]
# Stop rules
[retry, fallback, abstain, ask, stop]
```

## 8. GPT-5.6 Additions
- Be concise by default, remove "Be concise" if redundant.
- Define autonomy/approval boundaries explicitly.
- Tool routing: when to use which tool.
- Phase param: distinguish intermediate updates vs final.
- Migration: test old prompts, strip legacy CoT, keep verbosity control via `text.verbosity`.

## Takeaway
Master Prompt must be outcome-first, not step-micromanaging. Success criteria + stop rules are mandatory.
