import { spawnSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const dir = dirname(fileURLToPath(import.meta.url));
// ffmpeg from temp install (no system ffmpeg needed)
const FFMPEG = "C:\\Users\\Amir\\AppData\\Local\\Temp\\opencode-ffmpeg\\node_modules\\ffmpeg-static\\ffmpeg.exe";
const DUR = 32;
const OUT = join(dir, "SPEAK_Cinematic_32s.mp4");
const FILTER_FILE = join(dir, "filter_complex_cinematic.txt");

const BOLD = "fonts/segoeuib.ttf";
const REG = "fonts/segoeui.ttf";

const esc = (s) =>
  s.replace(/\\/g, "\\\\").replace(/'/g, "\\'").replace(/:/g, "\\:").replace(/,/g, "\\,");
const CX = `(w-text_w)/2`;
const btw = (a, b) => `between(t\\,${a}\\,${b})`;

// cubic ease-out slide from right
const slideX = (t0, off = 140, dur = 0.7) =>
  `${CX}+${off}-${off}*(1-pow(1-min(1\\,(t-${t0})/${dur})\\,3))`;

const dt = (text, o = {}) => {
  const { font = BOLD, size = 64, color = "#ffffff", x = null, y = 500, t0 = 0, t1 = DUR } = o;
  const xx = x === null ? slideX(t0) : x;
  const q = x === null ? "'" : "";
  return `drawtext=fontfile=${font}:text='${esc(text)}':fontsize=${size}:fontcolor=${color}:x=${q}${xx}${q}:y=${y}:enable='${btw(t0, t1)}'`;
};

const box = (o) => {
  const { x, y, w, h, c, t = "fill", t0 = 0, t1 = DUR } = o;
  return `drawbox=x=${x}:y=${y}:w=${w}:h='${h}':c=${c}:t=${t}:enable='${btw(t0, t1)}'`;
};

// ---------- base: cinematic aurora + 3 orbs + drift ----------
const base = [
  `[0:v]geq=r='14+34*(0.5+0.5*sin(2*PI*X/W+T*0.45))+22*Y/H':g='8+16*(0.5+0.5*sin(2*PI*Y/H+T*0.32))':b='26+68*Y/H+32*(0.5+0.5*sin(2*PI*X/W-T*0.38))'[base]`,
  `color=s=620x620:d=${DUR}:r=30,format=rgba,geq=r='102':g='58':b='243':a='86*(1-min(1\\,sqrt(pow(X-310\\,2)+pow(Y-310\\,2))/310))',gblur=sigma=32[orb1]`,
  `color=s=420x420:d=${DUR}:r=30,format=rgba,geq=r='34':g='211':b='238':a='64*(1-min(1\\,sqrt(pow(X-210\\,2)+pow(Y-210\\,2))/210))',gblur=sigma=26[orb2]`,
  `color=s=900x360:d=${DUR}:r=30,format=rgba,geq=r='182':g='217':b='252':a='26*(1-min(1\\,sqrt(pow(X-450\\,2)+pow(Y-180\\,2))/450))',gblur=sigma=40[orb3]`,
  `[base][orb1]overlay=x='(W-w)/2+580*sin(2*PI*t/15)':y='(H-h)/2+290*cos(2*PI*t/19)'[b1]`,
  `[b1][orb2]overlay=x='(W-w)/2-640*sin(2*PI*t/12+1.3)':y='(H-h)/2-270*cos(2*PI*t/17)'[b2]`,
  `[b2][orb3]overlay=x='(W-w)/2+120*sin(2*PI*t/23)':y='(H-h)/2-320+60*sin(2*PI*t/9)'[b3]`,
  `[b3]drawgrid=w=120:h=120:t=1:c=#ffffff@0.032[b4]`,
  `[b4]vignette=angle=PI/5[b5]`,
  `[b5]scale=2048:1152,crop=1920:1080:x='(in_w-out_w)/2+10*sin(t*0.45)':y='(in_h-out_h)/2+8*cos(t*0.32)'[cam]`,
];

const S = [];

// letterbox (cinematic 2.39:1 feel)
S.push(box({ x: 0, y: 0, w: 1920, h: 132, c: "black", t0: 0, t1: DUR }));
S.push(box({ x: 0, y: 948, w: 1920, h: 132, c: "black", t0: 0, t1: DUR }));
// cut flashes (whip-cut punctuation, SFX sync points)
for (const c of [5.0, 10.8, 16.6, 22.4, 27.2]) {
  S.push(box({ x: 0, y: 538, w: 1920, h: 3, c: "white@0.85", t0: c, t1: +(c + 0.1).toFixed(2) }));
}

// ---------- SCENE 0 : cold open (0-5) ----------
S.push(dt("AMIR BAGAWAN PRESENTS", { font: REG, size: 26, color: "#8b87a8", x: CX, y: 210, t0: 0.2, t1: 4.8 }));
S.push(dt("S P E A K", { size: 190, y: 320, t0: 0.4, t1: 4.8 }));
S.push(dt("Your Voice. Everywhere.", { size: 56, color: "#e6f1fc", y: 580, t0: 1.0, t1: 4.8 }));
S.push(dt("Voice dictation + live AI companion for Windows 11", { font: REG, size: 36, color: "#b9b4d6", y: 660, t0: 1.25, t1: 4.8 }));
S.push(box({ x: 710, y: 760, w: "'500*min(1,(t-0.5)/1.4)'", h: 6, c: "#663af3", t0: 0.5, t1: 4.8 }));
S.push(dt("VOXULA AI  v2.1  -  FREE", { font: REG, size: 26, color: "#a78bfa", x: CX, y: 800, t0: 1.6, t1: 4.8 }));

// ---------- SCENE 1 : dictation (5-10.8) ----------
S.push(dt("01  -  LIVE VOICE DICTATION", { size: 28, color: "#a78bfa", x: CX, y: 165, t0: 5.2, t1: 10.6 }));
S.push(dt("Press Ctrl + Space. Just speak.", { size: 68, y: 215, t0: 5.3, t1: 10.6 }));
S.push(dt("16 kHz streaming  -  types at your cursor  -  multilingual", { font: REG, size: 32, color: "#b9b4d6", y: 305, t0: 5.6, t1: 10.6 }));
// keycaps
S.push(box({ x: 770, y: 375, w: 130, h: 62, c: "#171a26", t0: 5.8, t1: 10.6 }));
S.push(box({ x: 770, y: 375, w: 130, h: 62, c: "#663af3@0.9", t: 2, t0: 5.8, t1: 10.6 }));
S.push(box({ x: 970, y: 375, w: 170, h: 62, c: "#171a26", t0: 5.8, t1: 10.6 }));
S.push(box({ x: 970, y: 375, w: 170, h: 62, c: "#663af3@0.9", t: 2, t0: 5.8, t1: 10.6 }));
S.push(dt("Ctrl", { size: 32, x: "'770+(130-text_w)/2'", y: 388, t0: 5.8, t1: 10.6 }));
S.push(dt("+", { font: REG, size: 38, color: "#8b87a8", x: 922, y: 382, t0: 5.8, t1: 10.6 }));
S.push(dt("Space", { size: 32, x: "'970+(170-text_w)/2'", y: 388, t0: 5.8, t1: 10.6 }));
// capsule mock
S.push(box({ x: 440, y: 490, w: 1040, h: 250, c: "#0b0d17@0.90", t0: 6.0, t1: 10.6 }));
S.push(box({ x: 440, y: 490, w: 1040, h: 250, c: "#663af3@0.85", t: 2, t0: 6.0, t1: 10.6 }));
S.push(dt("VOXULA  -  Listening", { size: 28, color: "#22d3ee", x: 500, y: 510, t0: 6.2, t1: 10.4 }));
for (let i = 0; i < 12; i++) {
  S.push(
    `drawbox=x=${500 + i * 36}:y=556:w=18:h='44+64*(0.5+0.5*sin(2*PI*t*2.6+${(i * 0.9).toFixed(1)}))':c=#22d3ee@0.95:t=fill:enable='${btw(6.2, 10.4)}'`
  );
}
S.push(dt("Could we schedule", { font: REG, size: 32, x: 500, y: 668, t0: 7.0, t1: 7.9 }));
S.push(dt("Could we schedule the meeting", { font: REG, size: 32, x: 500, y: 668, t0: 7.9, t1: 8.7 }));
S.push(dt("Could we schedule the meeting for 5:00 PM?", { font: REG, size: 32, x: 500, y: 668, t0: 8.7, t1: 10.4 }));
S.push(box({ x: 620, y: 790, w: 680, h: 10, c: "#23263a", t0: 6.4, t1: 10.6 }));
S.push(box({ x: 620, y: 790, w: "'680*min(1,(t-6.4)/3.6)'", h: 10, c: "#22c55e", t0: 6.4, t1: 10.6 }));

// ---------- SCENE 2 : companion (10.8-16.6) ----------
S.push(dt("02  -  MULTIMODAL LIVE COMPANION", { size: 28, color: "#a78bfa", x: CX, y: 160, t0: 11.0, t1: 16.4 }));
S.push(dt("Win + Shift. Talk + share screen.", { size: 64, y: 210, t0: 11.1, t1: 16.4 }));
S.push(box({ x: 500, y: 330, w: 920, h: 440, c: "#0a0c16@0.93", t0: 11.3, t1: 16.4 }));
S.push(box({ x: 500, y: 330, w: 920, h: 440, c: "#663af3@0.8", t: 2, t0: 11.3, t1: 16.4 }));
S.push(box({ x: 545, y: 372, w: 300, h: 32, c: "#ff3b30", t0: 11.4, t1: 16.4 }));
S.push(dt("LIVE SCREEN  -  1 fps", { size: 22, x: "'545+(300-text_w)/2'", y: 377, t0: 11.4, t1: 16.4 }));
for (let i = 0; i < 5; i++) {
  S.push(box({ x: 545, y: 432 + i * 54, w: 830 - i * 115, h: 17, c: "#ffffff@0.17", t0: 11.5, t1: 16.4 }));
}
// scanline sweep
S.push(box({ x: 545, y: "'432+280*min(1,(t-11.6)/4.2)'", w: 830, h: 4, c: "#22d3ee@0.9", t0: 11.6, t1: 15.8 }));
S.push(dt("Speaking...", { size: 38, color: "#22d3ee", x: CX, y: 800, t0: 11.8, t1: 14.0 }));
S.push(dt("Listening...", { size: 38, x: CX, y: 800, t0: 14.0, t1: 16.4 }));
S.push(dt("Screen-off = voice-only companion", { font: REG, size: 30, color: "#b9b4d6", y: 856, t0: 12.2, t1: 16.4 }));

// ---------- SCENE 3 : refine (16.6-22.4) ----------
S.push(dt("03  -  REFINE  -  POLISH  -  ELABORATE", { size: 28, color: "#a78bfa", x: CX, y: 160, t0: 16.8, t1: 22.2 }));
S.push(dt("Messy in. Perfect out.", { size: 66, y: 210, t0: 16.9, t1: 22.2 }));
S.push(box({ x: 240, y: 360, w: 650, h: 230, c: "#101322@0.92", t0: 17.2, t1: 22.2 }));
S.push(box({ x: 240, y: 360, w: 650, h: 230, c: "#8b87a8@0.6", t: 2, t0: 17.2, t1: 22.2 }));
S.push(dt("could you set meeting", { font: REG, size: 33, color: "#8b87a8", x: "'565-text_w/2'", y: 415, t0: 17.4, t1: 22.2 }));
S.push(dt("at 9pm actually 5pm", { font: REG, size: 33, color: "#8b87a8", x: "'565-text_w/2'", y: 470, t0: 17.4, t1: 22.2 }));
S.push(dt(">>>", { size: 52, color: "#663af3", x: CX, y: 438, t0: 17.8, t1: 22.2 }));
S.push(box({ x: 1030, y: 360, w: 650, h: 230, c: "#141126@0.96", t0: 17.2, t1: 22.2 }));
S.push(box({ x: 1030, y: 360, w: 650, h: 230, c: "#663af3@0.9", t: 3, t0: 17.2, t1: 22.2 }));
S.push(dt("Could we schedule the meeting", { font: REG, size: 33, x: "'1355-text_w/2'", y: 415, t0: 18.2, t1: 22.2 }));
S.push(dt("for 5:00 PM?", { font: REG, size: 33, x: "'1355-text_w/2'", y: 470, t0: 18.2, t1: 22.2 }));
S.push(dt("No clipboard. No Ctrl+A. Rewrites in place.", { font: REG, size: 30, color: "#b9b4d6", y: 640, t0: 18.6, t1: 22.2 }));
S.push(dt("Custom actions: Settings - Refine tab (up to 3)", { font: REG, size: 28, color: "#b9b4d6", y: 692, t0: 19.0, t1: 22.2 }));
S.push(box({ x: 540, y: 780, w: 270, h: 14, c: "#22c55e", t0: 19.0, t1: 22.2 }));
S.push(box({ x: 825, y: 780, w: 270, h: 14, c: "#f59e0b", t0: 19.4, t1: 22.2 }));
S.push(box({ x: 1110, y: 780, w: 270, h: 14, c: "#ef4444", t0: 19.8, t1: 22.2 }));
S.push(dt("token bar: green 0-60  orange 61-85  red 86-100", { font: REG, size: 26, color: "#8b87a8", y: 816, t0: 19.4, t1: 22.2 }));

// ---------- SCENE 4 : private (22.4-27.2) ----------
S.push(dt("PRIVATE BY DESIGN", { size: 28, color: "#a78bfa", x: CX, y: 190, t0: 22.6, t1: 27.0 }));
S.push(dt("Keys in Credential Manager.", { size: 60, y: 245, t0: 22.7, t1: 27.0 }));
S.push(dt("No analytics. No accounts.", { size: 60, y: 325, t0: 22.9, t1: 27.0 }));
S.push(box({ x: 360, y: 470, w: 380, h: 90, c: "#0b0d17@0.9", t0: 23.2, t1: 27.0 }));
S.push(box({ x: 360, y: 470, w: 380, h: 90, c: "#22c55e@0.8", t: 2, t0: 23.2, t1: 27.0 }));
S.push(dt("DPAPI ENCRYPTED", { size: 28, x: "'360+(380-text_w)/2'", y: 500, t0: 23.2, t1: 27.0 }));
S.push(box({ x: 770, y: 470, w: 380, h: 90, c: "#0b0d17@0.9", t0: 23.4, t1: 27.0 }));
S.push(box({ x: 770, y: 470, w: 380, h: 90, c: "#663af3@0.8", t: 2, t0: 23.4, t1: 27.0 }));
S.push(dt("DIRECT LINE", { size: 28, x: "'770+(380-text_w)/2'", y: 500, t0: 23.4, t1: 27.0 }));
S.push(box({ x: 1180, y: 470, w: 380, h: 90, c: "#0b0d17@0.9", t0: 23.6, t1: 27.0 }));
S.push(box({ x: 1180, y: 470, w: 380, h: 90, c: "#22d3ee@0.7", t: 2, t0: 23.6, t1: 27.0 }));
S.push(dt("TRAY-IDLE", { size: 28, x: "'1180+(380-text_w)/2'", y: 500, t0: 23.6, t1: 27.0 }));
S.push(dt("Sips CPU. No heavy local models. Cloud transcription.", { font: REG, size: 30, color: "#b9b4d6", y: 620, t0: 24.0, t1: 27.0 }));
S.push(dt("VS CODE  -  SLACK  -  NOTION  -  WORD  -  ANY APP", { font: REG, size: 28, color: "#8b87a8", x: CX, y: 700, t0: 24.4, t1: 27.0 }));

// ---------- SCENE 5 : CTA (27.2-32) ----------
S.push(dt("VOXULA AI  v2.1", { size: 30, color: "#a78bfa", x: CX, y: 200, t0: 27.4, t1: 31.4 }));
S.push(dt("Download SPEAK.", { size: 88, y: 260, t0: 27.5, t1: 31.4 }));
S.push(dt("Ship polished.", { size: 88, color: "#b6d9fc", y: 360, t0: 27.8, t1: 31.4 }));
S.push(box({ x: 680, y: 520, w: 560, h: 110, c: "#663af3", t0: 28.0, t1: 31.4 }));
S.push(dt("Download SPEAK", { size: 50, x: CX, y: 548, t0: 28.0, t1: 31.4 }));
S.push(dt("Single-file EXE  -  ~63 MB  -  by Amir Bagawan", { font: REG, size: 30, color: "#c9c4e8", y: 670, t0: 28.3, t1: 31.4 }));
S.push(dt("Ctrl + Space to dictate  -  Win + Shift to talk", { font: REG, size: 28, color: "#8b87a8", y: 722, t0: 28.6, t1: 31.4 }));
S.push(dt("Free tier included  -  bring your own key", { font: REG, size: 26, color: "#8b87a8", y: 770, t0: 28.9, t1: 31.4 }));

const filter =
  base.join(";\n") +
  ";\n[cam]" +
  S.join(",") +
  `,noise=alls=6:allf=t,fade=t=in:st=0:d=0.6,fade=t=out:st=${DUR - 0.7}:d=0.7,format=yuv420p[vout]`;

writeFileSync(FILTER_FILE, filter);
console.log("filter written, length:", filter.length);

const args = [
  "-y",
  "-f", "lavfi", "-i", `nullsrc=s=1920x1080:r=30:d=${DUR}`,
  "-filter_complex_script", FILTER_FILE,
  "-map", "[vout]",
  "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", "30",
  "-an",
  "-t", `${DUR}`, "-movflags", "+faststart",
  OUT,
];
console.log("rendering cinematic...");
const r = spawnSync(FFMPEG, args, { stdio: "inherit", cwd: dir });
if (r.status !== 0) {
  console.error("ffmpeg failed with code", r.status);
  process.exit(1);
}
console.log("DONE:", OUT);
