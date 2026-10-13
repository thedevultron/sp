# Gemini Live API — Official Docs Archive

**Source:** Google AI for Developers (ai.google.dev) + Google Cloud docs
**Retrieved:** 2026-09-18 (UTC)
**Models covered:** `gemini-3.8-live`, `gemini-3.8-live-extended-thinking`, `gemini-3.1-flash-live-preview`, `gemini-2.5-flash-live`

All files below are direct extractions of the official markdown source (`*.md.txt`) — i.e. the full page content, not summaries.
Full HTML snapshots are included where noted for “entire page” fidelity.

## Files

| # | File | Official URL | What it contains |
|---|------|--------------|------------------|
| 00 | `00-live-api-overview.md` | https://ai.google.dev/gemini-api/docs/live-api | Live API overview: use-cases, key features (multilingual 70 langs, barge-in, tool use, transcriptions, proactive audio, affective dialog, Live Transcription, Live Translation), tech specs (PCM 16kHz in / 24kHz out, JPEG ≤1FPS, WSS), server-to-server vs client-to-server + ephemeral tokens note, GenAI SDK / WebSocket / ADK tutorials, partner integrations (LiveKit, Pipecat, Fishjam, Stream, Voximplant, Agora, Firebase AI) |
| 01 | `01-live-api-capabilities.md` | https://ai.google.dev/gemini-api/docs/live-api/capabilities | **Capabilities guide (comprehensive, 42KB):** connection setup, interaction modalities, audio transcriptions, streaming audio/video, voice+language change, native audio, affective dialog, VAD (automatic/manual), media resolution, languages, `send_client_content` rules (3.1 vs 2.5), token count, client auth, session limits (15 min audio-only / 2 min AV), model comparison table |
| 02 | `02-live-api-get-started-sdk.md` | https://ai.google.dev/gemini-api/docs/live-api/get-started-sdk | Get started with GenAI SDK (server): WebSocket mgmt, `send_realtime_input` / `sendRealtimeInput`, PCM audio send, video frames (JPEG/PNG ≤1FPS), receiving audio/text, tool calls |
| 03 | `03-live-api-get-started-websocket.md` | https://ai.google.dev/gemini-api/docs/live-api/get-started-websocket | Get started with raw WebSockets: endpoint `wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?key=YOUR_API_KEY`, ephemeral `v1alpha …BidiGenerateContentConstrained?access_token=…`, `BidiGenerateContentSetup`, `BidiGenerateContentRealtimeInput` (text/audio Blob+mineType/image), `BidiGenerateContentServerMessage`, `BidiGenerateContentToolResponse` |
| 04 | `04-live-api-tools.md` | https://ai.google.dev/gemini-api/docs/live-api/tools | Tool use: function calling + Google Search, support matrix (3.1 vs 2.5), manual `session.send_tool_response`, sync vs async (`behavior`, `scheduling=INTERRUPT/WHEN_IDLE/SILENT`), `tools=[{'google_search':{}}]`, combining tools |
| 05 | `05-live-api-session-management.md` | https://ai.google.dev/gemini-api/docs/live-api/session-management | Session mgmt: persistent streaming session, context-window compression (`contextWindowCompression`, sliding-window, trigger tokens) for unlimited length, resumption (`sessionResumption`, `SessionResumptionUpdate`, handle token valid 2hr), `GoAway(timeLeft)`, `generationComplete`, 10-min connection limit |
| 06 | `06-live-api-ephemeral-tokens.md` | https://ai.google.dev/gemini-api/docs/live-api/ephemeral-tokens | Ephemeral tokens (Preview, Live-API-only): client→backend→provision→short-lived token flow, `newSessionExpireTime` (1 min) / `expireTime` (30 min), lock configs, use as API key on `v1beta`, `access_token` query or `Authorization: Token`, best practices |
| 07 | `07-live-api-best-practices.md` | https://ai.google.dev/gemini-api/docs/live-api/best-practices | Best practices: precise tool defs (career-coach JSON example with 5 functions), context mgmt, compression (25 tok/sec), resumption, GoAway, generationComplete, billing = compounding per-turn re-billing of context window, cost control via `contextWindowCompression` (e.g. trigger 25k / window 8k) |
| 08 | `08-live-api-thinking.md` | https://ai.google.dev/gemini-api/docs/live-api/thinking | **Thinking in Live API (`gemini-3.8-live-extended-thinking`):** background reasoning + async tools while streaming fillers (“Checking flights…”), `thinkingConfig.thinkingLevel=LOW/MEDIUM/HIGH (MINIMAL unsupported)`, `interaction_status=IN_PROGRESS/IDLE`, `behavior: NON_BLOCKING` required, `turnComplete:true` = end-of-utterance only, SDK examples, side-by-side vs `gemini-3.8-live` |
| 08H | `08-live-api-thinking.FULL-PAGE.html` | same as above | Full HTML snapshot of Thinking guide page (entire page) |
| 09 | `09-gemini-3.8-live.md` | https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live | **Gemini 3.8 Live model page (whole page):** default low-latency voice agent, interleaved reasoning (no `thinking_level`), async fn calling default NON_BLOCKING (BLOCKING for compat), `send_client_content` full-lifecycle, proactive audio permanently on, no affective dialog, `TURN_INCLUDES_AUDIO_ACTIVITY_AND_ALL_VIDEO`, AUDIO modality |
| 10 | `10-gemini-3.8-live-extended-thinking.md` | https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live-extended-thinking | **Gemini 3.8 Live Extended Thinking model page (whole page, markdown source):** high-reasoning audio-to-audio, 131072 in / 65536 out, Function calling Async-only, Search grounding Supported, full property table + Upgrading section (async protocol, interaction_status, NON_BLOCKING only, thinking_config low/med/high, client updates, proactive on) |
| 10H | `10-gemini-3.8-live-extended-thinking.FULL-PAGE.html` | same as above | Full HTML snapshot — the **entire page** as served (109KB) |
| 10C | `10-gemini-3.8-live-extended-thinking-COMPLETE.md` | same + thinking guide + announcement | **COMPLETE merged doc:** markdown source + full visible-text extraction + spec tables + setup JSON + response-flow + SDK notes + comparison + links (see below) |
| 11 | `11-gemini-3.1-flash-live-preview.md` | https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-live-preview | 3.1 Flash Live Preview page: 131072 / 65536, migration notes from 2.5 Flash Live |
| 12 | `12-live-websocket-api-reference.md` | https://ai.google.dev/api/live | **WebSockets API reference:** `BidiGenerateContentSetup`, `BidiGenerateContentClientContent`, `BidiGenerateContentRealtimeInput`, `BidiGenerateContentToolResponse`, server messages (`ServerContent`, `Setup`, `ToolCall`, `SessionResumptionUpdate`, `GoAway`, `generationComplete`), ephemeral auth |
| 13 | `13-live-guide.md` | https://ai.google.dev/gemini-api/docs/live-guide | Live guide (comprehensive, 32KB): same family as capabilities — modalities, transcription flags (`input_transcription`), cookbook links, voice/lang, VAD, resolution, languages |

## Focus: Gemini 3.8 Live Extended Thinking — entire page

> Start here: `10-gemini-3.8-live-extended-thinking-COMPLETE.md` (merged) + `10-gemini-3.8-live-extended-thinking.md` (pure official markdown) + `10-gemini-3.8-live-extended-thinking.FULL-PAGE.html` (raw HTML).
> Companion protocol: `08-live-api-thinking.md`.
> Announcement (Sep 15 2026): “Introducing Gemini 3.8 Live and 3.8 Live Extended Thinking” — https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-live-gemini-3-8-live-extended-thinking/

Model string: `models/gemini-3.8-live-extended-thinking`
AI Studio: https://aistudio.google.com/live?model=gemini-3.8-live-extended-thinking
Model card: https://deepmind.google/models/model-cards/gemini-3-8-audio/

## License note (from footers)

> Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies.
> Last updated 2026-09-15 UTC (model pages).
