# SPEAK Website — Cinematic Rebuild

Backup safe. No tokens altered. `authkit-tokens.css` and `@theme` untouched.

## What changed

### Foundation
- Added `gsap 3.12.5`. `lenis` kept.
- `src/lib/motion.ts`: `ensureScrollPlugins`, `MOTION_TOKENS`, `isMotionSafe`, `isWebGPUSupported`, `tryInitWebGPU`, `refreshScrollTriggers`.
- `App.tsx`: Lenis bound into `gsap.ticker` with `lagSmoothing(0)`. `ScrollTrigger.update` on scroll. Bypass on reduced-motion / coarse / <768px. Spot beam driven by `ScrollTrigger` scrub, not raw scroll listener. `ScrollTrigger.refresh()` after mount + on load. Added `Preloader`, `ClickSpark`, `GradualBlur` boundaries.

### Cinematic primitives (React-Bits inspired, local, singlefile-safe)
- `Preloader.tsx`: progress line, `yPercent:-100 power4.inOut` handoff.
- `SplitReveal.tsx`: masked split-word reveal, `start:top 82% once:true`, `power4.out 0.95s stagger 0.05 blur 8->0`. Kept readable with JS off.
- `TextMotion.tsx`: `ScrollFloat` (scrub 1, y+blur), `TextLoop` (2400ms, blur fade), `CountUp` (ScrollTrigger once, `power3.out`).
- `Interactions.tsx`: `ClickSpark` global, `PixelCard` hover glare, `GradualBlur`, `PrimaryAction` / `GhostAction` explicit variants.
- `LightRays.tsx`: ambient canvas behind hero + download. Checks `navigator.gpu.requestAdapter({powerPreference:high-performance})`, renders lightweight 2D rays in token colors. CSS fallback always present. Disabled on reduced-motion / mobile.
- `StickyStack.tsx`: `position:sticky top:12vh`, scale to 0.92, y -24, autoAlpha 0.72. Ready for future showcase, not forced into Bento to avoid layout risk.

### Sections + editorial (stop-slop)
- Eyebrows cut from 6 to 3 (Hero, Simulator, Download). Others use `01/02/03` mono tags. Fixes eyebrow-restraint fail.
- Hero: `LightRays`, `TextLoop` subhead, 19-word subcopy, proof band with `CountUp` (142ms / 99.4% / 0), short CTA labels. No em-dash. Active voice.
- Pipeline: `You press. SPEAK delivers.` Three steps rewritten human-actor, no -ly fillers.
- Simulator: `Press it. Watch it type.` Copy active, concrete.
- Bento: `You stay in flow.` Composition fix: `PillarCard` now takes `copy` + `demo` props, no magic `splitChildren`. Small cards use `PixelCard`. Copies stripped of adverbs and em-dashes.
- Hotkeys: `You hold the keys.` Hotkey descriptions active. Pillar copies concrete.
- Download: kept single eyebrow, added `CountUp` spec line, `LightRays` behind terminal, footer copy active.
- CSS: appended cinematic layer to `globals.css` only. No `:root` changes. Motion tokens: `power3/4.out` entries, `ease:none scrub 0.8-1.4` for scrubbed, y 24-48, blur 8->0. No bounce / elastic / spring jumps (kept one small spring for neon dot only).

### Composition + perf
- Removed `window scroll` listener anti-pattern.
- `CursorGlow` disabled on touch / narrow.
- `GlassCard` boolean sprawl documented; new code uses `PixelCard` + explicit `PillarInner`. Full codemod left out to avoid regression.
- React 19: no `forwardRef`, no `useContext` misuse found.

## Commands run
```
npm install gsap@3.12.5 --save
npm run build
```

## shadcn / React-Bits note
No `components.json` in this Vite singlefile project. Equivalent shadcn flow when registry is available:
```
npx shadcn@latest info --json
npx shadcn@latest search @react-bits -q "LightRays"
npx shadcn@latest add @react-bits/LightRays-JS-CSS @react-bits/ScrollFloat-React-Tailwind @react-bits/TextLoop-React-Tailwind @react-bits/CountUp-React-Tailwind @react-bits/ClickSpark-React-Tailwind @react-bits/PixelCard-React-Tailwind @react-bits/GradualBlur-React-Tailwind
npx shadcn@latest docs button dialog select
```
Local primitives above match those APIs so swap-in is trivial.

## Verify
```
npm run build  # passes, dist/index.html 610kB inlined, gzip ~193kB
```
Check: preloader exits, hero loop runs, reveals play once, CountUp fires once, sparks on click, rays hidden on mobile / reduced-motion, no horizontal overflow, sticky cards never inside `overflow:hidden`.
