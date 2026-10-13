/* SPEAK — crazy-motion product demo (30s, silent for SFX pass).
 * Full-frame <html> motion graphics driven by one paused anime.js timeline
 * seeked from the playhead: same playhead, same picture, export-accurate.
 * Beats cut every 5s with high-velocity in/out (outIn whip feel).
 * Entrances: expoOut / outElastic / outBack. Exits: expoIn. Holds: inOutSine drift.
 */
import { createEffect } from "solid-js";
import { createStore } from "solid-js/store";
import { createTimeline, type Timeline } from "animejs";
import { useTicker } from "@diffusionstudio/jsx";

const BEATS = [
  { key: "open" },
  { key: "dictation" },
  { key: "companion" },
  { key: "refine" },
  { key: "private" },
  { key: "cta" },
] as const;

type BeatState = { y: number; o: number };

export default function CrazyCut() {
  const { time } = useTicker();
  const [v, setV] = createStore({
    b0: { y: 90, o: 0 } as BeatState,
    b1: { y: 90, o: 0 } as BeatState,
    b2: { y: 90, o: 0 } as BeatState,
    b3: { y: 90, o: 0 } as BeatState,
    b4: { y: 90, o: 0 } as BeatState,
    b5: { y: 90, o: 0 } as BeatState,
    l0: { y: 120, o: 0 },
    l1: { y: 120, o: 0 },
    l2: { y: 120, o: 0 },
    l3: { y: 120, o: 0 },
    l4: { y: 120, o: 0 },
    hue: 265,
    scan: 0,
    flash: 0,
  });

  const s = {
    b0: { y: 90, o: 0 },
    b1: { y: 90, o: 0 },
    b2: { y: 90, o: 0 },
    b3: { y: 90, o: 0 },
    b4: { y: 90, o: 0 },
    b5: { y: 90, o: 0 },
    l0: { y: 120, o: 0 },
    l1: { y: 120, o: 0 },
    l2: { y: 120, o: 0 },
    l3: { y: 120, o: 0 },
    l4: { y: 120, o: 0 },
    hue: 265,
    scan: 0,
    flash: 0,
  };

  // Plain-object targets: build the timeline inline (cf. examples/05-anime-timeline),
  // not in onMount — onMount ordering breaks capture/export re-execution.
  const tl = createTimeline({ autoplay: false });
  {
    // ---- hue drift across whole cut (linear energy bed) ----
    tl.add(s, { hue: 625, duration: 30000, ease: "linear" }, 0);
    // ---- cold open letters: elastic pop, staggered ----
    const letters = [s.l0, s.l1, s.l2, s.l3, s.l4];
    letters.forEach((L, i) => {
      tl.add(L, { y: 0, o: 1, duration: 900, ease: "outElastic(1, .55)" }, 150 + i * 80);
    });
    // ---- beats: in (expoOut) / drift (inOutSine) / out (expoIn) ----
    const cuts: [keyof typeof s, number, number][] = [
      ["b0", 0, 5000],
      ["b1", 5000, 10000],
      ["b2", 10000, 15000],
      ["b3", 15000, 20000],
      ["b4", 20000, 25000],
      ["b5", 25000, 30000],
    ];
    for (const [key, cin, cout] of cuts) {
      const B = s[key] as BeatState;
      const isLast = key === "b5";
      tl.add(B, { y: 0, o: 1, duration: 800, ease: "outExpo" }, cin);
      tl.add(B, { y: -16, duration: cout - cin - 1600, ease: "inOutSine" }, cin + 800);
      if (!isLast) tl.add(B, { y: -70, o: 0, duration: 700, ease: "inExpo" }, cout - 800);
      else tl.add(B, { y: -16, o: 1, duration: 4200, ease: "inOutSine" }, cin + 800);
    }
    // ---- scanline sweep inside companion beat ----
    tl.add(s, { scan: 1, duration: 3400, ease: "inOutSine" }, 11200);
    // ---- whip-flash blips on cuts ----
    for (const c of [5000, 10000, 15000, 20000, 25000]) {
      tl.add(s, { flash: 1, duration: 60, ease: "linear" }, c);
      tl.add(s, { flash: 0, duration: 140, ease: "linear" }, c + 60);
    }
  }

  createEffect(() => {
    const ms = Math.min(Math.max(time() * 1000, 0), 30000);
    tl.seek(ms);
    setV("b0", { ...s.b0 });
    setV("b1", { ...s.b1 });
    setV("b2", { ...s.b2 });
    setV("b3", { ...s.b3 });
    setV("b4", { ...s.b4 });
    setV("b5", { ...s.b5 });
    setV("l0", { ...s.l0 });
    setV("l1", { ...s.l1 });
    setV("l2", { ...s.l2 });
    setV("l3", { ...s.l3 });
    setV("l4", { ...s.l4 });
    setV({ hue: s.hue, scan: s.scan, flash: s.flash });
  });

  const t = () => time();
  const hue = () => Math.round(v.hue % 360);
  // typing cascade inside dictation beat (5-10s)
  const dictText = () => {
    const tt = t();
    if (tt < 6.6) return "Could we schedule";
    if (tt < 7.6) return "Could we schedule the meeting";
    return "Could we schedule the meeting for 5:00 PM?";
  };
  // waveform bars: deterministic sine field, frame-accurate
  const barH = (i: number) => {
    const tt = t();
    return 40 + 68 * (0.5 + 0.5 * Math.sin(2 * Math.PI * 2.6 * tt + i * 0.9));
  };
  const beatStyle = (b: BeatState) => ({
    transform: `translateY(${b.y}px)`,
    opacity: b.o,
  });

  const letters = () => [v.l0, v.l1, v.l2, v.l3, v.l4];
  const glyphs = ["S", "P", "E", "A", "K"];

  return (
    <stage background="#05060f" camera={[0.38, 0, 0, 0.38, 17.95, 22.66]} id="wy5ry4">
      <scene name="SPEAK Crazy Cut" width={1920} height={1080} fill="#05060f" active id="uayp3x">
        <html x={0} y={0} width={1920} height={1080} end={30} id="cwaeag">
          <div
            style={`position:relative;width:1920px;height:1080px;overflow:hidden;
              font-family:Inter, 'Segoe UI', sans-serif;color:#fff;
              background:
                radial-gradient(1100px 600px at 18% 8%, hsla(${hue()}, 90%, 62%, .34), transparent 70%),
                radial-gradient(900px 620px at 85% 90%, hsla(${(hue() + 140) % 360}, 90%, 60%, .30), transparent 70%),
                radial-gradient(1400px 500px at 50% 115%, hsla(265, 90%, 55%, .30), transparent 70%),
                linear-gradient(180deg, #0a0d1d 0%, #05060f 55%, #070818 100%);`}
          >
            {/* grid */}
            <div
              style={`position:absolute;inset:0;
                background-image:linear-gradient(rgba(182,217,252,.07) 1px, transparent 1px),
                  linear-gradient(90deg, rgba(182,217,252,.07) 1px, transparent 1px);
                background-size:120px 120px;
                mask-image:radial-gradient(ellipse at 50% 42%, black 30%, transparent 78%);`}
            />
            {/* BEAT 0 — cold open */}
            <div
              style={{ position: "absolute", inset: "0", display: "flex", "flex-direction": "column", "align-items": "center", "justify-content": "center", ...beatStyle(v.b0) }}
            >
              <div style={{ "font-size": "26px", "letter-spacing": "6px", color: "#8b87a8" }}>AMIR BAGAWAN PRESENTS</div>
              <div style={{ display: "flex", gap: "54px", margin: "26px 0 8px", "font-size": "190px", "font-weight": "800", "letter-spacing": "18px" }}>
                {glyphs.map((g, i) => (
                  <span style={{ display: "inline-block", transform: `translateY(${letters()[i].y}px)`, opacity: letters()[i].o }}>{g}</span>
                ))}
              </div>
              <div style={{ "font-size": "56px", "font-weight": "700", color: "#e6f1fc" }}>Your Voice. Everywhere.</div>
              <div style={{ "font-size": "34px", color: "#b9b4d6", "margin-top": "10px" }}>Voice dictation + live AI companion · Windows 11</div>
              <div style={{ width: "500px", height: "6px", "margin-top": "30px", background: "rgba(102,58,243,.25)" }}>
                <div style={{ width: `${Math.min(100, Math.max(0, (t() / 4.2) * 100))}%`, height: "100%", background: "#663af3" }} />
              </div>
              <div style={{ "font-size": "26px", color: "#a78bfa", "margin-top": "18px", "letter-spacing": "3px" }}>VOXULA AI v2.1 · FREE</div>
            </div>
            {/* BEAT 1 — dictation */}
            <div
              style={{ position: "absolute", inset: "0", display: "flex", "flex-direction": "column", "align-items": "center", "justify-content": "center", ...beatStyle(v.b1) }}
            >
              <div style={{ "font-size": "28px", color: "#a78bfa", "letter-spacing": "4px" }}>01 — LIVE VOICE DICTATION</div>
              <div style={{ "font-size": "68px", "font-weight": "800", margin: "8px 0 2px" }}>Press Ctrl + Space. Just speak.</div>
              <div style={{ "font-size": "30px", color: "#b9b4d6" }}>16 kHz streaming · types at your cursor · multilingual</div>
              <div style={{ display: "flex", gap: "18px", "align-items": "center", margin: "26px 0" }}>
                <span style={`font-size:30px;font-weight:700;padding:12px 34px;border:2px solid #663af3;background:#171a26;`}>Ctrl</span>
                <span style={{ "font-size": "34px", color: "#8b87a8" }}>+</span>
                <span style={`font-size:30px;font-weight:700;padding:12px 40px;border:2px solid #663af3;background:#171a26;`}>Space</span>
              </div>
              <div style={`width:1040px;background:rgba(11,13,23,.92);border:2px solid rgba(102,58,243,.85);padding:22px 30px 26px;`}>
                <div style={{ "font-size": "28px", color: "#22d3ee", "font-weight": "700" }}>VOXULA · Listening</div>
                <div style={{ display: "flex", gap: "14px", "align-items": "flex-end", height: "120px", margin: "14px 0 10px" }}>
                  {Array.from({ length: 12 }, (_, i) => (
                    <div style={{ width: "20px", height: `${barH(i)}px`, background: "#22d3ee" }} />
                  ))}
                </div>
                <div style={{ "font-size": "32px", color: "#fff" }}>{dictText()}</div>
              </div>
              <div style={{ width: "680px", height: "10px", "margin-top": "22px", background: "#23263a" }}>
                <div style={{ width: `${Math.min(100, Math.max(0, ((t() - 5.4) / 4) * 100))}%`, height: "100%", background: "#22c55e" }} />
              </div>
            </div>
            {/* BEAT 2 — companion */}
            <div
              style={{ position: "absolute", inset: "0", display: "flex", "flex-direction": "column", "align-items": "center", "justify-content": "center", ...beatStyle(v.b2) }}
            >
              <div style={{ "font-size": "28px", color: "#a78bfa", "letter-spacing": "4px" }}>02 — MULTIMODAL LIVE COMPANION</div>
              <div style={{ "font-size": "62px", "font-weight": "800", margin: "8px 0 18px" }}>Win + Shift. Talk + share screen.</div>
              <div style={`position:relative;width:920px;background:rgba(10,12,22,.93);border:2px solid rgba(102,58,243,.8);padding:26px 34px 30px;`}>
                <span style={`display:inline-block;font-size:22px;font-weight:800;padding:6px 26px;background:#ff3b30;color:#fff;`}>LIVE SCREEN · 1 fps</span>
                <div style={{ display: "flex", "flex-direction": "column", gap: "22px", margin: "26px 0 6px" }}>
                  {[830, 715, 600, 490, 380].map((w) => (
                    <div style={{ width: `${w}px`, height: "17px", background: "rgba(255,255,255,.17)" }} />
                  ))}
                </div>
                <div style={{ position: "absolute", left: "34px", right: "34px", top: `${100 + v.scan * 300}px`, height: "4px", background: "#22d3ee" }} />
              </div>
              <div style={{ "font-size": "38px", color: "#22d3ee", "font-weight": "800", margin: "24px 0 4px" }}>{t() < 12.6 ? "Speaking…" : "Listening…"}</div>
              <div style={{ "font-size": "30px", color: "#b9b4d6" }}>Screen-off = voice-only companion</div>
            </div>
            {/* BEAT 3 — refine */}
            <div
              style={{ position: "absolute", inset: "0", display: "flex", "flex-direction": "column", "align-items": "center", "justify-content": "center", ...beatStyle(v.b3) }}
            >
              <div style={{ "font-size": "28px", color: "#a78bfa", "letter-spacing": "4px" }}>03 — REFINE · POLISH · ELABORATE</div>
              <div style={{ "font-size": "66px", "font-weight": "800", margin: "8px 0 24px" }}>Messy in. Perfect out.</div>
              <div style={{ display: "flex", gap: "34px", "align-items": "stretch" }}>
                <div style={`width:620px;background:rgba(16,19,34,.92);border:2px solid rgba(139,135,168,.6);padding:30px;text-align:center;`}>
                  <div style={{ "font-size": "32px", color: "#8b87a8" }}>could you set meeting</div>
                  <div style={{ "font-size": "32px", color: "#8b87a8", "margin-top": "12px" }}>at 9pm actually 5pm</div>
                </div>
                <div style={{ "font-size": "52px", color: "#663af3", "font-weight": "800", display: "flex", "align-items": "center" }}>{" >>> "}</div>
                <div style={`width:620px;background:rgba(20,17,38,.96);border:3px solid rgba(102,58,243,.9);padding:30px;text-align:center;`}>
                  <div style={{ "font-size": "32px", color: "#fff" }}>Could we schedule the meeting</div>
                  <div style={{ "font-size": "32px", color: "#fff", "margin-top": "12px" }}>for 5:00 PM?</div>
                </div>
              </div>
              <div style={{ "font-size": "28px", color: "#b9b4d6", "margin-top": "26px" }}>No clipboard. No Ctrl+A. Rewrites in place.</div>
              <div style={{ display: "flex", gap: "14px", "margin-top": "20px" }}>
                <div style={{ width: "270px", height: "14px", background: "#22c55e" }} />
                <div style={{ width: "270px", height: "14px", background: "#f59e0b" }} />
                <div style={{ width: "270px", height: "14px", background: "#ef4444" }} />
              </div>
            </div>
            {/* BEAT 4 — private */}
            <div
              style={{ position: "absolute", inset: "0", display: "flex", "flex-direction": "column", "align-items": "center", "justify-content": "center", ...beatStyle(v.b4) }}
            >
              <div style={{ "font-size": "28px", color: "#a78bfa", "letter-spacing": "4px" }}>PRIVATE BY DESIGN</div>
              <div style={{ "font-size": "58px", "font-weight": "800", margin: "8px 0 2px" }}>Keys in Credential Manager.</div>
              <div style={{ "font-size": "58px", "font-weight": "800" }}>No analytics. No accounts.</div>
              <div style={{ display: "flex", gap: "26px", margin: "30px 0 22px" }}>
                <span style={`font-size:27px;font-weight:800;padding:24px 0;width:380px;text-align:center;background:rgba(11,13,23,.9);border:2px solid #22c55e;`}>DPAPI ENCRYPTED</span>
                <span style={`font-size:27px;font-weight:800;padding:24px 0;width:380px;text-align:center;background:rgba(11,13,23,.9);border:2px solid #663af3;`}>DIRECT LINE</span>
                <span style={`font-size:27px;font-weight:800;padding:24px 0;width:380px;text-align:center;background:rgba(11,13,23,.9);border:2px solid #22d3ee;`}>TRAY-IDLE</span>
              </div>
              <div style={{ "font-size": "29px", color: "#b9b4d6" }}>Sips CPU. Cloud transcription. VS Code · Slack · Notion · Word · any app.</div>
            </div>
            {/* BEAT 5 — CTA */}
            <div
              style={{ position: "absolute", inset: "0", display: "flex", "flex-direction": "column", "align-items": "center", "justify-content": "center", ...beatStyle(v.b5) }}
            >
              <div style={{ "font-size": "30px", color: "#a78bfa", "letter-spacing": "4px" }}>VOXULA AI v2.1</div>
              <div style={{ "font-size": "86px", "font-weight": "800", margin: "6px 0 0" }}>Download SPEAK.</div>
              <div style={{ "font-size": "86px", "font-weight": "800", color: "#b6d9fc" }}>Ship polished.</div>
              <div style={`margin:36px 0 24px;width:560px;padding:26px 0;text-align:center;background:#663af3;font-size:48px;font-weight:800;`}>Download SPEAK</div>
              <div style={{ "font-size": "29px", color: "#c9c4e8" }}>Single-file EXE · ~63 MB · by Amir Bagawan</div>
              <div style={{ "font-size": "27px", color: "#8b87a8", "margin-top": "10px" }}>Ctrl + Space to dictate · Win + Shift to talk</div>
            </div>
            {/* whip-flash + letterbox */}
            <div style={{ position: "absolute", left: "0", right: "0", top: "538px", height: "3px", background: "#fff", opacity: v.flash }} />
            <div style={{ position: "absolute", left: "0", right: "0", top: "0", height: "132px", background: "#000" }} />
            <div style={{ position: "absolute", left: "0", right: "0", bottom: "0", height: "132px", background: "#000" }} />
          </div>
        </html>
      </scene>
    </stage>
  );
}
