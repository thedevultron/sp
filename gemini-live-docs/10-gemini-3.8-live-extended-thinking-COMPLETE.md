# Gemini 3.8 Live Extended Thinking — COMPLETE (Entire Page + Protocol)

**Source page (official):** https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live-extended-thinking
**Retrieved:** 2026-09-18 UTC via built-in browser + `*.md.txt` markdown source
**Raw snapshots in this folder:**
- `10-gemini-3.8-live-extended-thinking.md` — pure official markdown source (this content verbatim below in §1)
- `10-gemini-3.8-live-extended-thinking.FULL-PAGE.html` (109,609 bytes) — full HTML, entire page as served
- `08-live-api-thinking.md` + `08-live-api-thinking.FULL-PAGE.html` — Thinking protocol guide (companion, required for integration)
- Announcement Sep 15 2026: https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-live-gemini-3-8-live-extended-thinking/

**Model string:** `models/gemini-3.8-live-extended-thinking`
**Try in AI Studio:** https://aistudio.google.com/live?model=gemini-3.8-live-extended-thinking
**Model card:** https://deepmind.google/models/model-cards/gemini-3-8-audio/
**Docs:** Visit the Live API guide for full coverage — https://ai.google.dev/gemini-api/docs/live-api

---

## 0. One-line definition (verbatim header)

> Gemini 3.8 Live Extended Thinking is our high-reasoning audio-to-audio model recommended when higher background reasoning is required for complex, multi-step problem solving during real-time voice interactions. It processes background reasoning and asynchronous tool calls while streaming continuous audio responses.

Use `gemini-3.8-live-extended-thinking` when your agent must evaluate data, plan multiple steps, or handle tools that take several seconds to run.
Use `gemini-3.8-live` (sibling, default) for low-latency voice agents / direct commands / fast tools without reasoning-induced delays.

---

## 1. Official markdown source — VERBATIM (entire page body)

<br />

Gemini 3.8 Live Extended Thinking is our high-reasoning audio-to-audio model
recommended when higher background reasoning is required for complex, multi-step
problem solving during real-time voice interactions. It processes background
reasoning and asynchronous tool calls while streaming continuous audio
responses.
[Try in Google AI Studio](https://aistudio.google.com/live?model=gemini-3.8-live-extended-thinking)

## Documentation

Visit the [Live API](https://ai.google.dev/gemini-api/docs/live-api) guide for full coverage
of features and capabilities.

## gemini-3.8-live-extended-thinking

| Property | Description |
|---|---|
| Model code | `gemini-3.8-live-extended-thinking` |
| Supported data types | **Inputs** Text, images, audio, video **Output** Text and audio |
| Token limits | **Input token limit** 131,072 **Output token limit** 65,536 |
| Capabilities | **Audio generation** Supported **Caching** Not supported **Code execution** Not supported **File search** Not supported **Function calling** Supported (Async only) **Grounding with Google Maps** Not supported **Image generation** Not supported **Live API** Supported **Search grounding** Supported **Structured outputs** Not supported **Thinking** Supported **URL context** Not supported |
| Consumption options | **Batch API** Not supported |
| Versions | Stable: `gemini-3.8-live-extended-thinking` (see model version patterns) |
| Latest update | September 2026 |
| Model card | [Model card](https://deepmind.google/models/model-cards/gemini-3-8-audio/) |

## Upgrading to Gemini 3.8 Live Extended Thinking

Gemini 3.8 Live Extended Thinking introduces background reasoning during live
audio sessions. When integrating this model, update your client state management
to handle asynchronous reasoning signals:

- **Asynchronous reasoning protocol**: When interacting with models that use asynchronous reasoning, `turnComplete: true` no longer indicates that the model is idle. The server may continue processing background reasoning or tool calls. Your client must continue listening for subsequent server messages (such as tool calls or audio frames) after `turnComplete: true` arrives.
- **Monitoring `interaction_status`**: Use the `interaction_status` field on incoming server messages to determine current server state:
  - `IN_PROGRESS`: The server is actively processing user input, running background reasoning, or awaiting responses for asynchronous tool calls. Additional model output or tool calls may follow.
  - `IDLE`: The server has finished all processing, reasoning, and tool calls. The session is idle and waiting for user input.
- **Asynchronous function calling**: Only asynchronous non-blocking execution (`behavior: NON_BLOCKING`) is supported. Synchronous blocking mode is not supported and returns a hard error. Function scheduling configurations are not supported.
- **Thinking configuration**: Configure background reasoning using `thinking_config` in your setup configuration (`thinking_level`: `low`, `medium`, or `high`). Note that `MINIMAL` is not supported.
- **Client content updates**: `send_client_content` is supported throughout the entire session lifecycle with explicit roles (`user` or `model`). Setting `turn_complete=true` immediately interrupts active generation.
- **Proactive audio**: Permanently enabled. Setting `proactive_audio: false` returns an error.

For a feature comparison across all Live API models, see the
[Model comparison](https://ai.google.dev/gemini-api/docs/live-api/capabilities#model-comparison)
table.

---

## 2. Full visible-text extraction (entire page as rendered, via browser)

This is the `main` innerText dump — includes labels/icons as rendered, so nothing is skipped:

```
Gemini 3.8 Live Extended Thinking is our high-reasoning audio-to-audio model recommended when higher background reasoning is required for complex, multi-step problem solving during real-time voice interactions. It processes background reasoning and asynchronous tool calls while streaming continuous audio responses.

Try in Google AI Studio
Documentation
Visit the Live API guide for full coverage of features and capabilities.

gemini-3.8-live-extended-thinking
Property  Description
id_card Model code  gemini-3.8-live-extended-thinking
save Supported data types  Inputs Text, images, audio, video Output Text and audio
token_auto Token limits  Input token limit 131,072 Output token limit 65,536
handyman Capabilities  Audio generation Supported / Caching Not supported / Code execution Not supported / File search Not supported / Function calling Supported (Async only) / Grounding with Google Maps Not supported / Image generation Not supported / Live API Supported / Search grounding Supported / Structured outputs Not supported / Thinking Supported / URL context Not supported
speed Consumption options  Batch API Not supported
123 Versions  Stable: gemini-3.8-live-extended-thinking
calendar_month Latest update  September 2026
id_card Model card  Model card
Upgrading to Gemini 3.8 Live Extended Thinking
Asynchronous reasoning protocol / Monitoring interaction_status (IN_PROGRESS vs IDLE) / Asynchronous function calling (NON_BLOCKING only) / Thinking configuration (low, medium, high; MINIMAL not supported) / Client content updates (full lifecycle, turn_complete=true interrupts) / Proactive audio (permanently enabled)
For a feature comparison across all Live API models, see the Model comparison table.
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License.
Last updated 2026-09-15 UTC.
```

Page chrome (breadcrumb/header/footer as rendered):
- Banner: “Gemini 3.8 Flash is now available. Try it out.”
- Breadcrumb: Home / Gemini API / Docs / Gemini 3.8 Live Extended Thinking
- Title: “Gemini 3.8 Live Extended Thinking | Gemini API | Google AI for Developers”
- Footer: feedback link + CC-BY 4.0 + Apache 2.0 note + Last updated 2026-09-15 UTC

---

## 3. Thinking protocol — required integration changes (from Thinking guide)

Source: https://ai.google.dev/gemini-api/docs/live-api/thinking (see `08-live-api-thinking.md` for full 17KB guide).

Thinking adds background reasoning to real-time voice sessions. The model plans and calls async tools in the background while speaking natural conversational fillers to keep the interaction active.

### 3.1 Three integration points to adopt Thinking

1. **Track `interaction_status` instead of `turnComplete`:**
   In Thinking sessions the model can emit intermediate conversational fillers while reasoning. Inspect `interaction_status` on incoming server messages. Only return to idle when `interaction_status` is `IDLE`.
   - `turnComplete: true` + `interactionStatus: IN_PROGRESS` = end of utterance only, more output/tool calls to come.
   - `turnComplete: true` + `interactionStatus: IDLE` = turn fully done.

2. **Declare non-blocking functions:**
   Set `"behavior": "NON_BLOCKING"` on ALL function declarations. Thinking runs tools asynchronously in background while streaming verbal updates. Synchronous blocking tools return an error.

3. **Configure reasoning depth:**
   Set `thinking_config` in session setup: `low` / `medium` / `high` (`MINIMAL` not supported).

### 3.2 Setup JSON (Thinking)

```json
{
  "setup": {
    "model": "models/gemini-3.8-live-extended-thinking",
    "generationConfig": {
      "responseModalities": ["AUDIO"],
      "speechConfig": {
        "voiceConfig": {
          "prebuiltVoiceConfig": {
            "voiceName": "Puck"
          }
        }
      },
      "thinkingConfig": {
        "thinkingLevel": "LOW"
      }
    },
    "tools": [{
      "functionDeclarations": [{
        "name": "searchFlights",
        "description": "Searches for flights between cities.",
        "behavior": "NON_BLOCKING",
        "parameters": {
          "type": "OBJECT",
          "properties": {
            "destination": { "type": "STRING" }
          },
          "required": ["destination"]
        }
      }]
    }]
  }
}
```

### 3.3 Response flow (example: “search flights to Seattle”)

1. **Spoken filler:** intermediate speech e.g. “Checking flights to Seattle…” with `turnComplete: true` + `interactionStatus: IN_PROGRESS`.
2. **Async tool call:** server emits tool call while `interactionStatus` stays `IN_PROGRESS` (multi-step turn, awaiting tool response).
3. **Tool response:** client executes function, returns output via `BidiGenerateContentToolResponse` / `session.send_tool_response`.
4. **Final response:** complete answer with `turnComplete: true` + `interactionStatus: IDLE`.

Server envelope sketch:
`serverContent.modelTurn.parts[]` carries audio/text parts; separate `toolCall`, `sessionResumptionUpdate`, `goAway`, `generationComplete` messages interleave per WebSocket API ref (`12-live-websocket-api-reference.md`).

### 3.4 SDK notes

- Use GenAI SDK live session (`google-genai` async interface). Configure `thinking_config`, declare `NON_BLOCKING` tools, listen for `interaction_status` to drive UI state (speaking / thinking / idle).
- Output: AUDIO modality; enable output audio transcription if you need text transcript.
- Voices e.g. Puck, Charon, Kore, Fenrir, Aoede (per examples repo).

---

## 4. Side-by-side: 3.8 Live vs 3.8 Live Extended Thinking

| Feature | Gemini 3.8 Live | Gemini 3.8 Live Extended Thinking |
|---|---|---|
| Primary use | Low-latency voice agents, direct commands, fast tools | Multi-step problem solving, complex planning, multi-tool workflows |
| Endpoint | `gemini-3.8-live` | `gemini-3.8-live-extended-thinking` |
| Reasoning | Interleaved, fixed latency (`thinking_level` NOT supported — omit it) | Configurable background (`thinking_level`: `low`/`medium`/`high`; `MINIMAL` unsupported) |
| Turn boundary | `turnComplete:true` closes turn → idle | `turnComplete:true` = utterance done; `interaction_status` controls lifecycle (IDLE = done) |
| Tool behavior | Async default NON_BLOCKING; BLOCKING allowed for compat; scheduling SILENT/WHEN_IDLE/INTERRUPTED supported | NON_BLOCKING ONLY (sync = hard error); scheduling configs NOT supported |
| Client updates | `send_client_content` full lifecycle, explicit `user`/`model` roles; `turn_complete=true` interrupts | Same: full lifecycle + interrupt |
| Proactive audio | Permanently enabled (`false` = error) | Same: permanently enabled |
| Affective dialog | Removed (drop `enable_affective_dialog`) | n/a (background reasoning instead) |
| Turn coverage | Default `TURN_INCLUDES_AUDIO_ACTIVITY_AND_ALL_VIDEO` (send video sparingly) | Same family (manage context/cost) |
| Response | AUDIO (enable transcription if needed) | AUDIO + Text (audio-to-audio + text out per spec table) |
| Migration from 3.1 Flash Live | Update string 3.1→3.8, drop thinking_level, review async/scheduling/client-content/proactive/affective/turn-coverage/modality | Update string 3.1→3.8-extended-thinking + 3 adoption points above |

Protocol identicals: WebSocket URL + API-key auth (`wss://generativelanguage.googleapis.com/ws/...BidiGenerateContent`), ephemeral-token client-to-server flow.

---

## 5. Spec recap (from page table, normalized)

- **I/O:** In Text/images/audio/video; Out Text+audio. Audio wire: raw 16-bit PCM 16kHz LE in, 24kHz LE out. Images JPEG ≤1FPS.
- **Limits:** 131,072 in / 65,536 out.
- **Supported:** Audio gen, Function calling (Async only), Live API, Search grounding, Thinking.
- **Not supported:** Caching, Code execution, File search, Maps grounding, Image gen, Structured outputs, URL context, Batch API.
- **Rollout (Sep 15 2026 announcement):** API + AI Studio now; Enterprise private preview + soon Customer Experience + Workspace (Docs Live / Gmail Live / Keep Live); Gemini app + AI Pro/Ultra.
- **Docs links:** Live API overview, Capabilities + Model comparison, Thinking, Tools, Session mgmt, Ephemeral tokens, Best practices, WebSocket ref, 3.8 Live sibling page.

---

## 6. Links (every link on the page, resolved)

- Try in AI Studio (extended): https://aistudio.google.com/live?model=gemini-3.8-live-extended-thinking
- Live API guide: https://ai.google.dev/gemini-api/docs/live-api
- Tokens: https://ai.google.dev/gemini-api/docs/tokens
- Speech: https://ai.google.dev/gemini-api/docs/speech-generation
- Caching: https://ai.google.dev/gemini-api/docs/caching
- Code execution: https://ai.google.dev/gemini-api/docs/code-execution
- File search: https://ai.google.dev/gemini-api/docs/file-search
- Function calling: https://ai.google.dev/gemini-api/docs/function-calling
- Maps grounding: https://ai.google.dev/gemini-api/docs/maps-grounding
- Image generation: https://ai.google.dev/gemini-api/docs/image-generation
- Google Search grounding: https://ai.google.dev/gemini-api/docs/google-search
- Structured outputs: https://ai.google.dev/gemini-api/docs/structured-output
- Thinking: https://ai.google.dev/gemini-api/docs/thinking
- URL context: https://ai.google.dev/gemini-api/docs/url-context
- Batch API: https://ai.google.dev/gemini-api/docs/batch-api
- Model versions: https://ai.google.dev/gemini-api/docs/models/gemini#model-versions
- Model card (audio): https://deepmind.google/models/model-cards/gemini-3-8-audio/
- Model comparison: https://ai.google.dev/gemini-api/docs/live-api/capabilities#model-comparison
- Sibling model: https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live
- Thinking guide: https://ai.google.dev/gemini-api/docs/live-api/thinking
- Announcement: https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-live-gemini-3-8-live-extended-thinking/

License: CC-BY 4.0 (prose) + Apache 2.0 (code). Last updated 2026-09-15 UTC.
