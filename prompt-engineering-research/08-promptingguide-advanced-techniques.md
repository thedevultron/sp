# 08 - PromptingGuide Advanced Techniques

Source: promptingguide.ai/techniques/* + Prompt Report (Schulhoff 2024, 58 techniques) + SurePrompts 2026

## 1. Self-Consistency (Wang 2022) - +17.9% on GSM8K
- Sample multiple CoT paths (temp >0), majority vote. Best accuracy for reasoning.
- Universal Self-Consistency: LLM picks most coherent (not just vote). Multi-Chain: synthesize superior answer from multiple paths.

## 2. Tree of Thoughts (ToT) - Yao 2023
- Explore multiple reasoning branches, score, backtrack. Deliberate problem solving for planning, puzzles, architecture.
- vs CoT (single path) vs Self-Consistency (parallel vote).

## 3. ReAct (Yao 2022) - Reasoning + Acting
- Loop: Thought -> Action (tool) -> Observation until done. Foundation of agents.
- Example: Search, read file, run code, observe, reason next.

## 4. Program-Aided Language Models (PAL) / Program-of-Thoughts / Faithful CoT
- Write Python to solve (not just reason in words), run it, stdout = answer. Precise for math, data, backend logic.
- Faithful CoT: NL plan + executable code ensures logic-derived answer.

## 5. Retrieval Augmented Generation (RAG) - Lewis 2020
- Fetch docs, inject into prompt. Production surface: chunking (fixed/heading/semantic), query expansion (multi-phrasing), reranking top-K, cite sources (cuts hallucination).
- Context Injection (no retrieval, you already know needed profile/session) vs RAG.

## 6. Prompt Chaining / Least-to-Most / Plan-and-Solve / Step-Back / Self-Ask
- Chaining: sequential prompts, output feeds next. Each handles one stage.
- Least-to-Most: simplest to hardest, solve incrementally.
- Plan-and-Solve: plan first, then solve step-by-step (improves Zero-shot CoT).
- Step-Back: general principle first ("What principle?"), then specific.
- Self-Ask: generate sub-questions + solve sequentially.
- Skeleton-first: outline before body (long-form).

## 7. Automatic Prompt Engineer (APE) / Active-Prompt / Directional Stimulus (DSP) / OPRO
- APE: LLM generates/improves prompts automatically.
- Active-Prompt: pick most uncertain examples for human labeling, then CoT.
- DSP: tiny hint (keywords) guides generation.
- Meta: prompts about prompts, constitutional (principles for self-correct), emotion ("important to career" boosts effort), hypothetical.

## 8. Verification Family
- Self-Verify: re-read prompt after answer, flag violations.
- Self-Critique: list 3 weaknesses.
- Self-Refine: draft->critique->revise loop until <3 critiques.
- Chain-of-Verification (Dhuliawala 2023): generate verification Qs, answer independently, revise.
- Reflexion: store reflections from failures for next attempt.
- Verifier Model: separate cheaper model with rubric.

## 9. Other
- Generate Knowledge: generate facts first, then answer (better than vanilla CoT on commonsense).
- ART: auto reasoning + tool-use.
- Multimodal CoT: text + vision reasoning.
- Graph Prompting: graph structure reasoning.
- Tabular CoT, Chain-of-Symbol, Analogical (self-generate examples), Thread-of-Thought (chaotic context -> summarize/filter), Meta-Cognitive (reflect on strategy), Rephrase-and-Respond, Translation-first for multilingual.

## 10. Structured Output
- Demand strict JSON with schema, TypeScript type, format lock ("return ONLY JSON, no preamble").

## Takeaway
Advanced = Decomposition + Retrieval + Agent + Verification + Meta. Every production Master Prompt needs at least 3 families.
