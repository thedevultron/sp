# 04 - Claude Thinking, Parallel Tools & Agents

Source: platform.claude.com thinking + agentic systems + Opus 5 / Sonnet 5 / Fable 5 pages

## 1. Thinking Modes
- Adaptive thinking (`thinking: {type: "adaptive"}`) = default on Fable 5, Opus 5, Sonnet 5. Model decides when/how much to think based on `effort` + query complexity.
- Old extended thinking (`budget_tokens`) deprecated, 400 error on 4.7+.
- Prefer general "think thoroughly" over hand-written step plan. Claude's reasoning > human prescription.
- Multishot with `<thinking>` tags inside examples to show reasoning pattern.
- Manual CoT fallback when thinking off: `<thinking>` + `<answer>` separation. On Opus 5 prefer thinking ON low effort vs OFF (OFF leaks internal tags).
- Self-check: "Before finish, verify against [criteria]" - REMOVE on Opus 5 (it already self-verifies, extra causes over-verification waste).
- Opus 4.6 overthinks: replace "Default to using [tool]" with "Use [tool] when it would enhance understanding". Lower effort if still aggressive.
- Steering: "Thinking adds latency, only use when meaningfully improves quality" to reduce thinking.

## 2. Parallel Tool Calling
- Latest models run independent calls in parallel automatically (searches, file reads, bash).
- Boost to ~100%:
```
<use_parallel_tool_calls>
If no dependencies, call all independent tools in parallel. Never guess missing params.
</use_parallel_tool_calls>
```
- To calm: "Execute sequentially with brief pauses".

## 3. Subagent Orchestration
- Claude delegates natively if subagent tools defined. Let it orchestrate.
- Opus 4.6/5 overuses subagents (grep would suffice). Dampen:
```
Use subagents when parallel/isolated/independent workstreams. For simple tasks, act directly.
```

## 4. Long-Horizon & State Tracking
- Context awareness: Sonnet 5/4.6/4.5, Haiku 4.5 track token budget.
- Tell it not to stop early:
```
Your context will auto-compact. Do not stop early. Save progress to memory before refresh. Be persistent.
```
- Multi-window: Window 1 = framework/tests/setup scripts. Later windows = iterate todo-list.
- Tests in `tests.json`, progress in `progress.txt`, git for checkpoints. "Never remove/edit tests".
- Start fresh: "Call pwd; only read/write here. Review progress.txt, tests.json, git logs. Run integration test before new features."
- Verification tools: computer-use, browser-use for UI checks.
- Encourage full context use: "Spend entire output working systematically until complete".

## 5. Autonomy vs Safety
```
Consider reversibility. Local reversible (edit, test) = proceed. Hard-to-reverse (rm -rf, drop table, push --force, external post) = ask first. Never bypass safety (--no-verify).
```

## 6. Research Pattern
- Success criteria + verify across sources + competing hypotheses + confidence tracking + hypothesis tree file.

## Takeaway for Master Prompt
- Backend prompt needs autonomy boundaries + verification + state files.
- UI prompt needs verbosity control + formatting rules.
- Main prompt needs effort guidance (don't micromanage reasoning).
