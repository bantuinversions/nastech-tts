# Nastech Research Voice Studio

The local browser workspace at `http://127.0.0.1:8765/` is the **Nastech Research Voice Studio**. It calls the existing local API, receives a local WAV response, and keeps browser-only drafts, history, preferences, and favourites on the device. It does not introduce a cloud speech proxy.

## Feature map

| Area | Implemented local features |
|---|---|
| Appearance and accessibility | Midnight, Sunrise, and Paper themes; persisted theme; high-contrast mode; compact layout; reduced-motion mode; font-size decrease; font-size increase; keyboard-focus styling; live status announcements; keyboard-shortcut help. |
| Writing and composition | Local draft autosave; draft restore; character count; word count; speech-duration estimate; clean-text formatting; clear draft; Welcome template; Narration template; Announcement template; Lesson template; Story template. |
| Language and voice selection | Code-first language search; code-first language selector; planned-language guard; planned-language visibility switch; voice search; named-voice-only filter; favourite-voice toggle; favourite-first ordering; all 40 local English profiles; all 61 language targets. |
| Expressive controls | Ten emotion choices; normal, soft, and dynamic delivery; laugh, chuckle, sigh, cough, sniffle, groan, yawn, gasp, cry, scream, and throat-clear cues; clear-sounds action; themed story selection. |
| Synthesis workflow | Generate and play; cancellable generation; request timing; voice preview; themed-story generation; line-by-line serial batch rendering; local activity log; API-key field for explicitly protected local deployments. |
| Playback and exports | Native WAV player; play/pause; replay last; five-second seek back; five-second seek forward; playback speed; volume; loop; live audio visualizer when the browser allows Web Audio; WAV download; text download; markup download; session-JSON export; copy text; copy markup. |
| Local history and diagnostics | Browser-local session history; restore a session; pin a session; delete a session; clear history; saved-session count; local diagnostics; preference reset. |

## Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl` / `Cmd` + `Enter` | Generate and play local speech. |
| `Ctrl` / `Cmd` + `Shift` + `C` | Copy the generated markup. |
| `Ctrl` / `Cmd` + `Shift` + `V` | Generate a short preview in the selected voice. |
| `Escape` | Close shortcut help or cancel an active local request. |

## Production workflow

Start the local service and open the local root page.

```bash
nastech-tts serve
```

Write or paste your script, choose a code-first language label such as `lg - Luganda`, select a voice and emotion, then select **Generate & play**. To create several independent snippets, put each item on its own line and use **Render lines in order**. The studio processes one line at a time and stores each successful local request in browser-local history.

> For a Bantu language, select only a language whose local on-demand pack is available. Planned targets remain visible only when enabled and are not silently substituted with a different language.

## Local data boundary

The browser saves its draft, theme, accessibility preferences, favourite profiles, activity messages, and session metadata in browser-local storage. It does not persist generated WAV blobs. Use **Download local WAV** or the export controls to retain files outside the browser. Clearing browser site data removes browser-local studio information.
