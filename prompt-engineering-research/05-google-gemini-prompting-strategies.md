# 05 - Google Gemini Prompting Strategies

Sources: ai.google.dev/gemini-api/docs/prompting-strategies + docs.cloud.google.com Gemini 3 prompting guide + cloud.google.com/discover/what-is-prompt-engineering

## 1. Clear & Specific Instructions
- Customize behavior via question, steps, or user mindset mapping.
- Input types: question (answer it), task (do it), entity (operate on it), completion (continue it). Model = advanced autocomplete.
- Specify constraints: length, what to do AND not do.
- Response format: table, bullets, elevator pitch, keywords, paragraph. System instruction for tone.

## 2. Zero-shot vs Few-shot
- Always include few-shot if you can. Prompts without examples are less effective. Clear examples can REPLACE instructions.
- Optimal number: few is enough, too many = overfit. Experiment.
- Consistent formatting: same structure, XML tags, whitespace, newlines, splitters across all examples.

## 3. Add Context
- Don't assume model knows. Include constraints + details needed.
- Gemini 3: Be precise/direct, no fluff/persuasion. Consistent delimiters (XML or Markdown, not both mixed). Define ambiguous terms. Control verbosity (default direct/efficient - must ASK for chatty). Critical instructions in System Instruction or top. Long context: data FIRST, question LAST + anchor phrase "Based on information above...".

## 4. Break Down Components
- For complex prompts, split into simpler components. Too many tasks in one pass (summarize+extract+translate+email) = split into separate prompts.

## 5. Model Parameters
- Temperature, topK, topP, max tokens. Gemini 3: keep temp 1.0 default! Lower (<1.0) causes looping/degraded reasoning. Use thinkingLevel LOW + "think silently" for latency.

## 6. Iteration Strategies
- Rephrase, switch to analogous task if stuck, fallback responses, grounding + code execution.
- Prompt. Test. Evaluate. Refine. Repeat. (test-driven).

## 7. Gemini 3 Specifics
- Distinguish deduction vs external info: don't say "do not guess" blanket (breaks logic). Say "Use provided context for deductions, avoid outside knowledge".
- Split-step verification: Step 1 verify info/capability exists, Step 2 answer based on it. Prevents plausible-but-fake.
- Organize constraints LAST: core request + critical negative/formatting/quantitative constraints as final lines. Model drops early negatives on complex requests.
  ```
  [Context]
  [Main task]
  [Negative, formatting, quantitative constraints] <- LAST
  ```
- Personas: model takes persona seriously, may ignore instructions to stay in character. Avoid ambiguous persona.
- Grounding: if hypothetical contradicts real world, explicitly say "Provided context is ONLY source of truth".
- Multi-source synthesis: "Based on entire document above..." prevents stopping after first match.
- Reasoning: no need to ask for plan, internal thinking automatic. "Think very hard" helps heavy reasoning at token cost.

## 8. Workspace Prompting 101 (Persona/Task/Context/Format)
- Formula: Persona + Task (verb!) + Context + Format. Avg fruitful prompt 21 words + context (people try <9 words).
- Tips: natural language full sentences, specific + iterate, concise no jargon, conversational follow-ups, use your Drive docs, "Make this a power prompt: [prompt]" to self-improve.

## Takeaway
Google adds: constraints LAST, data FIRST question LAST, split verification, temp 1.0. Critical for backend + long-context prompts.
