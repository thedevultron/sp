export type AppTarget = "vscode" | "slack" | "notion";

export type TransformMode = "raw" | "polish";

export type DictationStatus = "idle" | "listening" | "refining" | "done";

export interface ContentToken {
  text: string;
  cls: string;
}

export interface HotkeyDef {
  keys: { label: string; match: string }[];
  label: string;
  description: string;
}

export interface AppContent {
  raw: string;
  polished: string;
  lang: "code" | "text";
}
