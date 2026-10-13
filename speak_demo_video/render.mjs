import { spawnSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const dir = dirname(fileURLToPath(import.meta.url));
const FFMPEG =
  "C:\\Users\\Amir\\AppData\\Local\\Temp\\opencode\\ffmpeg-setup\\node_modules\\ffmpeg-static\\ffmpeg.exe";
const OUT = join(dir, "SPEAK_Demo_30s.mp4");
const FILTER_FILE = join(dir, "filter_complex.txt");

const BOLD = "fonts/segoeuib.ttf";
const REG = "fonts/segoeui.ttf";

// drawtext text must escape \ ' : , at filter level
const esc = (s) =>
  s.replace(/\\/g, "\\\\").replace(/'/g, "\\'").replace(/:/g, "\\:").replace(/,/g, "\\,");
const CX = `(w-text_w)/2`; // centered x

// ease-out slide from right, settles at center over 0.6s
const slideX = (t0, off = 120) =>
  `${CX}+${off}-${off}*min(1\\,(t-${t0})/0.6)`;
const btw = (a, b) => `between(t\\,${a}\\,${b})`;

const dt = (text, o = {}) => {
  const { font = BOLD, size = 64, color = "#ffffff", x = null, y = 500, t0 = 0, t1 = 30 } = o;
  const xx = x === null ? slideX(t0) : x;
  const q = x === null ? "'" : "";
  return `drawtext=fontfile=${font}:text='${esc(text)}':fontsize=${size}:fontcolor=${color}:x=${q}${xx}${q}:y=${y}:enable='${btw(t0, t1)}'`;
};

const box = (o) => {
  const { x, y, w, h, c, t = "fill", t0 = 0, t1 = 30 } = o;
  return `drawbox=x=${x}:y=${y}:w=${w}:h='${h}':c=${c}:t=${t}:enable='${btw(t0, t1)}'`;
};

// ---------- base: animated aurora ----------
const base = [
  `[0:v]geq=r='16+36*(0.5+0.5*sin(2*PI*X/W+T*0.5))+24*Y/H':g='10+18*(0.5+0.5*sin(2*PI*Y/H+T*0.35))':b='28+70*Y/H+34*(0.5+0.5*sin(2*PI*X/W-T*0.4))'[base]`,
  `color=s=560x560:d=30:r=30,format=rgba,geq=r='102':g='58':b='243':a='80*(1-min(1\\,sqrt(pow(X-280\\,2)+pow(Y-280\\,2))/280))',gblur=sigma=30[orb1]`,
  `color=s=360x360:d=30:r=30,format=rgba,geq=r='34':g='211':b='238':a='60*(1-min(1\\,sqrt(pow(X-180\\,2)+pow(Y-180\\,2))/180))',gblur=sigma=25[orb2]`,
  `[base][orb1]overlay=x='(W-w)/2+560*sin(2*PI*t/14)':y='(H-h)/2+280*cos(2*PI*t/18)'[b1]`,
  `[b1][orb2]overlay=x='(W-w)/2-620*sin(2*PI*t/11+1.3)':y='(H-h)/2-260*cos(2*PI*t/16)'[b2]`,
  `[b2]drawgrid=w=140:h=140:t=1:c=#ffffff@0.035[b3]`,
  `[b3]vignette=angle=PI/5[b4]`,
];

const S = [];
// ---------- SCENE 1 : hook (0-5) ----------
S.push(dt("S P E A K", { size: 200, y: 330, t0: 0.3, t1: 4.9 }));
S.push(dt("Voice dictation  and  live AI companion", { font: REG, size: 46, color: "#c9c4e8", y: 600, t0: 0.9, t1: 4.9 }));
S.push(dt("for Windows 11", { size: 46, color: "#a78bfa", y: 668, t0: 1.1, t1: 4.9 }));
S.push(dt("AMIR BAGAWAN", { font: REG, size: 28, color: "#8b87a8", x: CX, y: 220, t0: 0.5, t1: 4.9 }));
S.push(box({ x: 750, y: 780, w: "'420*min(1,(t-0.5)/1.2)'", h: 8, c: "#663af3", t0: 0.5, t1: 4.9 }));

// ---------- SCENE 2 : dictation (5-12) ----------
S.push(dt("01  -  LIVE VOICE DICTATION", { size: 30, color: "#a78bfa", x: CX, y: 140, t0: 5.2, t1: 11.8 }));
S.push(dt("Press Ctrl + Space. Just speak.", { size: 72, y: 200, t0: 5.3, t1: 11.8 }));
S.push(dt("16 kHz streaming  -  types at your cursor  -  multilingual", { font: REG, size: 34, color: "#b9b4d6", y: 300, t0: 5.6, t1: 11.8 }));
S.push(box({ x: 775, y: 390, w: 130, h: 64, c: "#171a26", t0: 5.8, t1: 11.8 }));
S.push(box({ x: 775, y: 390, w: 130, h: 64, c: "#663af3@0.9", t: 2, t0: 5.8, t1: 11.8 }));
S.push(box({ x: 975, y: 390, w: 170, h: 64, c: "#171a26", t0: 5.8, t1: 11.8 }));
S.push(box({ x: 975, y: 390, w: 170, h: 64, c: "#663af3@0.9", t: 2, t0: 5.8, t1: 11.8 }));
S.push(dt("Ctrl", { size: 34, x: "'775+(130-text_w)/2'", y: 402, t0: 5.8, t1: 11.8 }));
S.push(dt("+", { font: REG, size: 40, color: "#8b87a8", x: 925, y: 396, t0: 5.8, t1: 11.8 }));
S.push(dt("Space", { size: 34, x: "'975+(170-text_w)/2'", y: 402, t0: 5.8, t1: 11.8 }));
// capsule
S.push(box({ x: 460, y: 520, w: 1000, h: 220, c: "#0b0d17@0.88", t0: 6.0, t1: 11.8 }));
S.push(box({ x: 460, y: 520, w: 1000, h: 220, c: "#663af3@0.85", t: 2, t0: 6.0, t1: 11.8 }));
for (let i = 0; i < 5; i++) {
  S.push(
    `drawbox=x=${520 + i * 44}:y=570:w=20:h='50+70*(0.5+0.5*sin(2*PI*t*2.4+${(i * 1.1).toFixed(1)}))':c=#22d3ee@0.95:t=fill:enable='${btw(6.2, 11.6)}'`
  );
}
S.push(dt("Listening...", { size: 32, color: "#22d3ee", x: 790, y: 580, t0: 6.2, t1: 11.6 }));
S.push(dt("Could we schedule", { font: REG, size: 32, x: 520, y: 680, t0: 7.0, t1: 7.8 }));
S.push(dt("Could we schedule the meeting", { font: REG, size: 32, x: 520, y: 680, t0: 7.8, t1: 8.6 }));
S.push(dt("Could we schedule the meeting for 5:00 PM?", { font: REG, size: 32, x: 520, y: 680, t0: 8.6, t1: 11.6 }));
S.push(box({ x: 640, y: 800, w: 640, h: 10, c: "#23263a", t0: 6.4, t1: 11.8 }));
S.push(box({ x: 640, y: 800, w: "'640*min(1,(t-6.4)/5)'", h: 10, c: "#22c55e", t0: 6.4, t1: 11.8 }));

// ---------- SCENE 3 : companion (12-19) ----------
S.push(dt("02  -  MULTIMODAL LIVE COMPANION", { size: 30, color: "#a78bfa", x: CX, y: 120, t0: 12.2, t1: 18.8 }));
S.push(dt("Win + Shift. Talk and share screen.", { size: 66, y: 175, t0: 12.3, t1: 18.8 }));
S.push(box({ x: 510, y: 320, w: 900, h: 440, c: "#0a0c16@0.92", t0: 12.5, t1: 18.8 }));
S.push(box({ x: 510, y: 320, w: 900, h: 440, c: "#663af3@0.8", t: 2, t0: 12.5, t1: 18.8 }));
S.push(box({ x: 550, y: 368, w: 300, h: 30, c: "#ff3b30", t0: 12.6, t1: 18.8 }));
S.push(dt("LIVE SCREEN - 1 fps", { size: 22, x: "'550+(300-text_w)/2'", y: 372, t0: 12.6, t1: 18.8 }));
for (let i = 0; i < 5; i++) {
  S.push(box({ x: 550, y: 430 + i * 56, w: 820 - i * 110, h: 18, c: "#ffffff@0.18", t0: 12.7, t1: 18.8 }));
}
S.push(dt("Speaking...", { size: 40, color: "#22d3ee", x: CX, y: 800, t0: 13.0, t1: 15.9 }));
S.push(dt("Listening...", { size: 40, x: CX, y: 800, t0: 15.9, t1: 18.8 }));
S.push(dt("Screen-off mode  =  voice-only companion", { font: REG, size: 32, color: "#b9b4d6", y: 868, t0: 13.4, t1: 18.8 }));

// ---------- SCENE 4 : refine (19-25) ----------
S.push(dt("03  -  REFINE  -  POLISH  -  ELABORATE", { size: 30, color: "#a78bfa", x: CX, y: 140, t0: 19.2, t1: 24.8 }));
S.push(dt("Say polish. Messy in, perfect out.", { size: 66, y: 200, t0: 19.3, t1: 24.8 }));
S.push(box({ x: 260, y: 370, w: 640, h: 220, c: "#101322@0.9", t0: 19.6, t1: 24.8 }));
S.push(box({ x: 260, y: 370, w: 640, h: 220, c: "#8b87a8@0.6", t: 2, t0: 19.6, t1: 24.8 }));
S.push(dt("could you set meeting", { font: REG, size: 34, color: "#8b87a8", x: "'580-text_w/2'", y: 420, t0: 19.8, t1: 24.8 }));
S.push(dt("at 9pm actually 5pm", { font: REG, size: 34, color: "#8b87a8", x: "'580-text_w/2'", y: 476, t0: 19.8, t1: 24.8 }));
S.push(dt(">>>", { size: 54, color: "#663af3", x: CX, y: 440, t0: 20.2, t1: 24.8 }));
S.push(box({ x: 1020, y: 370, w: 640, h: 220, c: "#141126@0.95", t0: 19.6, t1: 24.8 }));
S.push(box({ x: 1020, y: 370, w: 640, h: 220, c: "#663af3@0.9", t: 3, t0: 19.6, t1: 24.8 }));
S.push(dt("Could we schedule the meeting", { font: REG, size: 34, x: "'1340-text_w/2'", y: 420, t0: 20.4, t1: 24.8 }));
S.push(dt("for 5:00 PM?", { font: REG, size: 34, x: "'1340-text_w/2'", y: 476, t0: 20.4, t1: 24.8 }));
S.push(dt("No clipboard. No Ctrl+A. Backspaces measured.", { font: REG, size: 30, color: "#b9b4d6", y: 650, t0: 20.8, t1: 24.8 }));
S.push(dt("Custom actions in Settings - Refine tab", { font: REG, size: 30, color: "#b9b4d6", y: 702, t0: 21.2, t1: 24.8 }));
S.push(box({ x: 560, y: 800, w: 260, h: 14, c: "#22c55e", t0: 21.0, t1: 24.8 }));
S.push(box({ x: 830, y: 800, w: 260, h: 14, c: "#f59e0b", t0: 21.4, t1: 24.8 }));
S.push(box({ x: 1100, y: 800, w: 260, h: 14, c: "#ef4444", t0: 21.8, t1: 24.8 }));
S.push(dt("token bar: green 0-60  orange 61-85  red 86-100", { font: REG, size: 28, color: "#b9b4d6", y: 836, t0: 21.4, t1: 24.8 }));

// ---------- SCENE 5 : CTA (25-30) ----------
S.push(dt("PRIVATE BY DESIGN", { size: 30, color: "#a78bfa", x: CX, y: 190, t0: 25.2, t1: 29.2 }));
S.push(dt("Keys in Credential Manager.", { size: 62, y: 250, t0: 25.3, t1: 29.2 }));
S.push(dt("No analytics. No accounts.", { size: 62, y: 334, t0: 25.5, t1: 29.2 }));
S.push(box({ x: 680, y: 470, w: 560, h: 110, c: "#663af3", t0: 25.8, t1: 29.2 }));
S.push(dt("Download SPEAK", { size: 52, x: CX, y: 495, t0: 25.8, t1: 29.2 }));
S.push(dt("Single-file EXE  -  installer  -  by Amir Bagawan", { font: REG, size: 32, color: "#c9c4e8", y: 630, t0: 26.2, t1: 29.2 }));
S.push(dt("Ctrl + Space to dictate  -  Win + Shift to talk", { font: REG, size: 30, color: "#8b87a8", y: 690, t0: 26.5, t1: 29.2 }));

const filter =
  base.join(";\n") +
  ";\n[b4]" +
  S.join(",") +
  ",noise=alls=5:allf=t,fade=t=in:st=0:d=0.5,fade=t=out:st=29.3:d=0.7,format=yuv420p[vout];\n" +
  "[1:a]volume=0.10[a1];[2:a]volume=0.06[a2];[3:a]volume=0.05[a3];" +
  "[a1][a2][a3]amix=inputs=3:normalize=0,afade=t=in:st=0:d=2,afade=t=out:st=27:d=3,volume=0.5[aout]\n";

writeFileSync(FILTER_FILE, filter);
console.log("filter written, length:", filter.length);

const args = [
  "-y",
  "-f", "lavfi", "-i", "nullsrc=s=1920x1080:r=30:d=30",
  "-f", "lavfi", "-i", "sine=frequency=55:duration=30",
  "-f", "lavfi", "-i", "sine=frequency=110:duration=30",
  "-f", "lavfi", "-i", "sine=frequency=82.5:duration=30",
  "-filter_complex_script", FILTER_FILE,
  "-map", "[vout]", "-map", "[aout]",
  "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-r", "30",
  "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
  "-t", "30", "-movflags", "+faststart",
  OUT,
];
console.log("rendering...");
const r = spawnSync(FFMPEG, args, { stdio: "inherit" });
if (r.status !== 0) {
  console.error("ffmpeg failed with code", r.status);
  process.exit(1);
}
console.log("DONE:", OUT);
