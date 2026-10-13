# 01 - OpenAI Prompt Engineering (developers.openai.com)

Source: https://developers.openai.com/api/docs/guides/prompt-engineering + help.openai.com 6654000 + openai.com/academy/prompting

## 1. Core Mental Model
- Prompt engineering = writing effective instructions so model *consistently* meets requirements. Non-deterministic -> mix of art + science.
- Pin production to model snapshots (e.g. `gpt-4.1-2025-04-14`). Build evals.
- GPT models = junior coworker: need precise instructions. Reasoning models = senior coworker: give goal, trust details.

## 2. Message Roles & Instruction Following
- `instructions` param (or `developer` role) = high-level behavior, tone, goals. Takes priority over `input` / `user`.
- `developer` = function definition (rules, business logic). `user` = arguments (inputs, config). `assistant` = output.
- `instructions` only applies to current turn. Doesn't persist with `previous_response_id` - resend each time.

## 3. Message Formatting: Markdown + XML
Use both to show logical boundaries:
```text
# Identity
You are coding assistant that enforces snake_case...

# Instructions
* use snake_case, use var for IE6
* Do NOT return Markdown, just code

# Examples
<user_query>How declare first name?</user_query>
<assistant_response>var first_name = "Anna";</assistant_response>
```
- Order: Identity -> Instructions -> Examples -> Context (context near end, varies per request).
- XML tags for docs: `<doc id="1">...</doc>`. XML attributes for metadata.
- Prompt caching: keep stable prefix first in prompt AND first in JSON body.

## 4. Few-Shot Learning
- Include 3-5 diverse input/output examples to steer pattern without fine-tuning.
- Show edge cases. Keep formatting identical (whitespace, tags matter).
- You can remove instructions if examples are clear enough.

## 5. Context / RAG
- Add proprietary data, constrain to specific resources.
- RAG = query vector DB or use File Search tool, inject into prompt.
- Plan context window: 100k to 1M tokens. Don't exceed.

## 6. OpenAI Rules of Thumb (Help Center)
1. Use latest model
2. Put instructions at beginning, separate with ### or """
3. Be specific: context, outcome, length, format, style
4. Show output format via examples
5. Start zero-shot -> few-shot -> fine-tune
6. Reduce fluffy imprecise words ("brief" -> "3 sentences or less")
7. Say what TO DO, not just what NOT to do
8. Code: use leading words (`import`, `function`) to nudge pattern
9. Temperature 0 for factual, higher for creative. max_tokens is cutoff, not length control.

## 7. Prompting Current Models (gpt-6-astra)
### Coding:
- Define agent role + workflow, enforce structured tool use with examples, require tests (`apply_patch` may say Done even on failure), set Markdown standards (backticks for files/functions).

### Frontend:
- Stack: Tailwind, shadcn/ui, Radix, Lucide, Motion.
- Zero-to-one: ask for evaluation rubric (5-7 hidden categories), iterate internally.
- Large codebase: Principles, UI/UX (type, color, spacing, hover/empty/loading, a11y), Structure (folders), Components (wrappers), Pages (templates), Agent Instructions (confirm assumptions, scaffold, test states).

### Agentic:
- Plan + persist: "keep going until fully resolved, decompose, reflect after each tool call"
- Preamble: "Before you call a tool explain why"
- TODO tracking.

## Takeaway for Master Prompt
- Always use Identity/Instructions/Examples/Context structure.
- Positive instructions > negative.
- Examples > description for format.
- Version prompts in code, test them.
