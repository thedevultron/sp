# Too Large Files — SPEAK (thedevultron/sp)

Files excluded from this repository because they exceed GitHub's size limits (hard limit 100 MB; repo policy 50 MB).

These files existed only inside local unpushed commits (added and later deleted from the working tree during development). The unpushed history was collapsed into a single commit so none of these blobs are part of the repository. The files do not currently exist on disk; their sizes below are exact, taken from git's object database. Preventive .gitignore entries were added in case they are recreated locally.

| File | Exact size | Exact location | Importance / can the project build without it? |
|---|---|---|---|
| `speak_app/src.zip` | 465674821 bytes (444.1 MB) | C:\Users\Amir\SPEAK\speak_app/src.zip | ZIP archive containing a redundant copy of source code (byte-identical in size to the desktop file C:\Users\Amir\src.zip). NOT needed to build — the actual sources are tracked in the repository itself. Safe to exclude. |
| `speak_demo_video/SPEAK_Cinematic_32s.mp4` | 241994867 bytes (230.78 MB) | C:\Users\Amir\SPEAK\speak_demo_video/SPEAK_Cinematic_32s.mp4 | Cinematic demo video render. NOT needed to build or run any app. Regenerable with the render scripts in speak_demo_video (render_cinematic.mjs). Safe to exclude. |
| `speak_demo_video/SPEAK_Demo_30s.mp4` | 86130587 bytes (82.14 MB) | C:\Users\Amir\SPEAK\speak_demo_video/SPEAK_Demo_30s.mp4 | Demo video render. NOT needed to build or run any app. Regenerable with speak_demo_video/render.mjs. Technically under GitHub's 100 MB hard limit but excluded to match the 50 MB repo policy and keep the repo lean. Safe to exclude. |

No build or runtime dependency exists on any of these files — all three are regenerable artifacts.
