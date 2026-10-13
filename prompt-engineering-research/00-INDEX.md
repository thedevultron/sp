# Prompt Engineering Research Library - INDEX

> Built from: OpenAI Docs (developers.openai.com), Anthropic Claude Docs (platform.claude.com + claude.com/blog), Google Gemini Docs (ai.google.dev + cloud.google.com), PromptingGuide.ai (dair-ai), plus 2026 syntheses.
> Date: Sept 2026
> Purpose: Feed the final `10-ULTIMATE-MASTER-PROMPT-ARCHITECT.md` - an AI instruction file that turns any user idea into a 3-part Ultimate Master Prompt.

## Files in this folder

- `00-INDEX.md` - this file
- `01-openai-prompt-engineering.md` - Message roles, Markdown+XML, few-shot, RAG, caching, GPT vs Reasoning models, agentic + frontend prompts
- `02-openai-outcome-first-gpt5.md` - GPT-5.5 / 5.6 outcome-first, personality vs collaboration, preamble, stop rules, grounding, verbosity
- `03-claude-prompting-best-practices.md` - Be clear, context/motivation, XML tags, role, examples, long-context, output formatting
- `04-claude-thinking-agents.md` - Extended/adaptive thinking, effort param, parallel tools, subagents, multi-window state, autonomy vs safety
- `05-google-gemini-prompting-strategies.md` - Clear instructions, zero vs few-shot, context, break-down, parameters, Gemini 3 core principles
- `06-google-vertex-prompt-components.md` - Prompt components table (Goal, Persona, Tone, Safeguards, Context, Examples, Constraints, Output Format, Triggers), System Instructions, health checklist
- `07-promptingguide-core-techniques.md` - Zero-shot, Few-shot, Chain-of-Thought, Zero-shot-CoT, Auto-CoT
- `08-promptingguide-advanced-techniques.md` - Self-Consistency, ToT, ReAct, PAL, RAG, Prompt Chaining, APE, Active-Prompt, DSP, Reflexion, Multimodal CoT, Graph
- `09-synthesis-technique-selector.md` - All 60 techniques in 10 families + WHEN to use which for Main vs UI vs Backend prompts
- `10-ULTIMATE-MASTER-PROMPT-ARCHITECT.md` - **THE FINAL FILE**: Paste this into any AI. It interviews user, picks techniques, outputs 3 prompts in paste order.

## Paste Order (decided for you)

After testing all sources, best order is:

1. **PART 2 - Backend Architecture Prompt** FIRST (data models, APIs, auth, DB schema)
2. **PART 1 - Main App Prompt** SECOND (app vision, user flows, global rules - references backend)
3. **PART 3 - UI/Frontend Prompt** LAST (design system, pages, components - builds on 1+2)

Why: Backend = foundation. Main = brain. UI = face. AI builders (v0, Lovable, Bolt, Cursor) perform best when schema exists before UI. This is documented in OpenAI frontend + Claude document-creation guidance.

## How to use

1. Read 01-09 if you want to learn.
2. Just want results? Open `10-ULTIMATE-MASTER-PROMPT-ARCHITECT.md`, copy entire file as system prompt into ChatGPT / Claude / Gemini, then type your app idea.
