# 07 - PromptingGuide.ai Core Techniques

Source: promptingguide.ai/techniques/zeroshot, fewshot, cot + dair-ai GitHub

## 1. Zero-Shot Prompting
- No examples, direct instruction. Works because models instruction-tuned + RLHF (Wei et al 2022).
- Example: `Classify sentiment: "I love headphones" -> ?` Model knows "sentiment".
- When fails -> go few-shot.

## 2. Few-Shot Prompting (In-Context Learning)
- Provide demonstrations as conditioning. Emerges at scale (Kaplan 2020, Touvron 2023).
- 1-shot, 3-shot, 5-shot, 10-shot. Harder task = more shots.
- Min et al 2022 tips: label space + input distribution matter (even random labels > no labels), format matters hugely, true label distribution > uniform.
- Limitation: fails on multi-step reasoning. Example math word problem still wrong with few-shot -> need CoT.

## 3. Chain-of-Thought (CoT) - Wei et al 2022
- Enable complex reasoning via intermediate steps. Combine with few-shot for best results on arithmetic/commonsense/symbolic.
- Show reasoning chain in examples, not just answer.

Few-shot CoT example pattern:
```
Q: Roger has 5 balls, buys 2 cans of 3... How many?
A: Roger started 5. 2 cans *3 =6. 5+6=11. Answer 11.
```

## 4. Zero-Shot CoT - Kojima et al 2022
- Just add `"Let's think step by step."` No examples needed. Surprisingly effective.
- Useful when few examples available.

## 5. Auto-CoT - Zhang et al 2022
- Automate demonstration creation: cluster questions (diversity), sample representative per cluster, generate chain via Zero-Shot-CoT.
- Heuristics: ~60 tokens length, ~5 reasoning steps. Simple + accurate demos.
- Mitigates manual hand-crafting bias/errors.

## When to use (for Master Prompt)
- Zero-shot: simple classification, Q&A, formatting.
- Few-shot: style/format/tone cloning, edge-case behavior.
- CoT: math, logic, planning, debugging, architecture tradeoffs.
- Zero-shot-CoT: quick reasoning boost without tokens for examples.
- Auto-CoT: generating UI variations or test cases at scale.

## Papers to cite
- Language Models are Few-Shot Learners (Brown 2020)
- CoT Elicits Reasoning (Wei 2022)
- Large Models are Zero-Shot Reasoners (Kojima 2022)
- Self-Consistency Improves CoT (Wang 2022)
