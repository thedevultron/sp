# 03 - Claude Prompting Best Practices (Anthropic)

Sources: platform.claude.com/docs/en/build-with-claude/prompt-engineering/* + claude.com/blog/best-practices-for-prompt-engineering + GitHub prompt-eng-interactive-tutorial (9 chapters)

## 1. Be Clear & Direct (Golden Rule)
- Show prompt to colleague with minimal context. If they'd be confused, Claude will be too.
- Tell exactly what you want. "Include as many relevant features as possible. Go beyond basics" > "Create dashboard".
- Use numbered steps when order matters. Use action verbs: Generate, Analyze, Create.
- Skip preamble: get straight to request. Say what to INCLUDE, not just exclude.

## 2. Provide Context & Motivation
- Explain WHY: "Never use ellipses BECAUSE TTS engine can't pronounce them" > "NEVER use ellipses".
- Claude generalizes from explanation.
- Give permission to say "I don't know" -> reduces hallucinations.

## 3. Use Examples Effectively (Few-shot / Multishot)
- Most reliable steering for format/tone/structure.
- Relevant (mirror real use), Diverse (edge cases), Structured (`<example>` inside `<examples>`, 3-5 examples).
- Ask Claude to evaluate/generate more examples from initial set.
- Format matters even with random labels.

## 4. Structure with XML Tags
- Claude treats `<tag>` like parser element. Essential when mixing instructions/context/examples/inputs.
- Use consistent descriptive names: `<instructions>`, `<context>`, `<input>`, `<output>`.
- Nest: `<documents><document index="1"><source>...</source><document_content>...</document_content></document></documents>`
- Same idea works with Markdown H2 + lists, triple backticks, JSON schema. Pick one, be consistent.

## 5. Give Role (1 sentence matters)
`You are a helpful coding assistant specializing in Python.` focuses behavior + tone.

## 6. Long Context (20k+ tokens)
- Put longform data AT TOP, query/instructions/examples AT END. +30% quality on multidoc.
- Ground in quotes first: ask to quote relevant parts in `<quotes>` before task in `<info>`.
- After large block, anchor: "Based on information above..."

## 7. Output & Formatting Control
- Tell what TO do: "Compose smoothly flowing prose paragraphs" > "Do not use markdown".
- XML format indicators: "Write prose in <smoothly_flowing_prose_paragraphs> tags".
- Match prompt style to desired output (no markdown in prompt = less markdown out).
- LaTeX default for math - explicitly forbid if you want plain text.
- Document creation: Claude is strong one-shot for presentations/animations. Just ask with design intent.

## 8. Prefill Migration (Claude 4.6+)
- Prefill (partial assistant message) deprecated -> 400 error. Use instead:
  - JSON/YAML -> Structured Outputs / tools with enum
  - Skip preamble -> "Respond directly without preamble" + XML tags
  - Continuations -> put in user message: "Previous response ended with [...] Continue"
  - Context hydration -> inject into user turn or via tools

## 9. Tool Use
- Be explicit: "Change this function" (will act) > "Can you suggest changes?" (will only suggest).
- Default-to-action block vs do-not-act block to tune proactivity.
- Dial back aggressive MUST language on Opus 4.5+ (overtriggers now).

## 10. Tutorial Chapters (Anthropic)
1. Basic Prompt Structure 2. Being Clear/Direct 3. Assigning Roles 4. Separating Data from Instructions 5. Formatting Output & Speaking for Claude 6. Precognition (Think Step by Step) 7. Using Examples 8. Avoiding Hallucinations 9. Building Complex Prompts (chatbot, legal, finance, coding) + Appendix: Chaining, Tool Use, Retrieval.

## Takeaway
Claude = XML + Why + Examples. Put data first, question last.
