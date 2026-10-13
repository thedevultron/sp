# 09 - Synthesis: 60 Techniques in 10 Families + Selector for Main/UI/Backend

Source: Prompt Assay 60 techniques (2026) + Prompt Report 58 + all prior files.

## The 10 Families (Canonical in bold)

| Family | Controls | Canonical | Others |
|---|---|---|---|
| Framing | Who model is, who output for | **Role Assignment** | Persona, Audience, Emotion, Hypothetical |
| Structure | Physical layout | **XML Tagging** | Delimiters, Markdown Structure, Template, JSON Output, Schema Spec, Format Lock |
| Demonstration | Show examples? | **Few-shot** | Zero-shot, One-shot, Contrastive CoT, Analogical |
| Reasoning | How hard to think | **Chain-of-Thought** | Zero-shot-CoT, Auto-CoT, ToT, Self-Consistency, Step-Back, Least-to-Most, Tabular/Chain-of-Draft |
| Decomposition | Split big task | **Prompt Chaining** | Task Decomposition, Plan-first, Skeleton-first, Compositional |
| Retrieval | Outside knowledge | **RAG** | Chunking, Query Expansion, Rerank, Context Injection, Cite Sources |
| Agent | Tool loop | **ReAct** | Function Calling, Agent Loop, PAL, Plan-Execute, Multi-Agent |
| Verification | Check before ship | **Self-Verify** | Self-Critique, Self-Refine, Chain-of-Verification, Reflexion, Verifier Model |
| Constraint | Hard rules | **Guardrails** | Negative Instruction, Refusal Frame, Boundary, Length Limit |
| Meta | Prompts about prompts | **Meta-Prompting** | Prompt Generation, Optimize (APE/OPRO/DSPy), Constitutional |

## Selector - Which Technique for Which Master Part?

### PART 1 - MAIN APP PROMPT (vision, flows, global rules)
Best: Role + Outcome-first + Constraints + Few-shot (1 example of good user story) + Plan-first + Scope guardrails
- Why: Needs product thinking, not code. Avoid over-specifying steps (OpenAI outcome-first). Use Step-Back for vision ("What type of app is this? SaaS/marketplace/dashboard?") then specifics.
- Must include: Success criteria, Stop rules, Audience, Tone, What NOT to build.

### PART 2 - BACKEND ARCHITECTURE PROMPT (DB, APIs, auth) - PASTE FIRST
Best: Schema Spec + JSON Output + ReAct/PAL mindset + Self-Verify + Split-step verification + RAG (if existing schema) + Negative constraints LAST
- Why: Precision matters. Demand ERD, REST endpoints table (Method/Path/Auth/Body/Response), auth flow, env vars, migration SQL. Use PAL ("write Prisma/SQL, validate syntax") + Chain-of-Verification ("verify every FK, every endpoint has auth").
- Must include: Tables with types, relations, indexes, RLS, API contract, auth boundaries, non-functional (latency, scale).

### PART 3 - UI/FRONTEND PROMPT (design system, pages) - PASTE LAST
Best: Role (world-class designer) + XML/Markdown structure + Few-shot style example + Format Lock + Constitutional (a11y, responsive) + Self-Refine (rubric 5-7 hidden categories)
- Why: Visual quality needs taste + constraints. Specify Tailwind/shadcn/Lucide/Motion, typography, colors, spacing, hover/empty/loading states, responsive, dark mode.
- Must include: Design tokens, component list, page templates, interaction states, a11y, no lorem ipsum.

## Universal Rules (all 3)
1. Data FIRST, question LAST (Google/Claude long-context).
2. Critical constraints LAST (Gemini 3 drops early negatives).
3. Positive > negative, but pair both.
4. System Instruction for stable persona, user message for variable task.
5. Temp 0 for backend (factual), 0.7-1.0 for UI (creative).
6. Always: Role, Goal, Context, Constraints, Examples, Output Format, Verification, Stop Rules.

## Decision Tree (Claude 2026)
1. Vague? -> Be clear + context (Why)
2. Wrong format? -> Examples + XML + Format Lock
3. Complex? -> Chain (split) + Plan-first
4. Needs reasoning? -> Thinking/CoT (or silent thinking for reasoning models)
5. Needs facts? -> RAG + Cite + Retrieval budget
6. Needs tools? -> ReAct + explicit trigger
7. Hallucinating? -> Permission to say IDK + verification
