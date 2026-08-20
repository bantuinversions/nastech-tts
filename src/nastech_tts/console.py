"""Self-contained browser console for the local Nastech TTS API."""

# ruff: noqa: E501

CONSOLE_FEATURES = (
    "midnight_theme",
    "sunrise_theme",
    "paper_theme",
    "persistent_theme",
    "high_contrast_mode",
    "compact_layout",
    "reduced_motion_mode",
    "font_size_control",
    "keyboard_shortcuts",
    "keyboard_help",
    "live_status_announcements",
    "draft_autosave",
    "draft_restore",
    "character_counter",
    "word_counter",
    "speech_duration_estimate",
    "whitespace_cleanup",
    "clear_draft",
    "writing_templates",
    "quick_sound_cues",
    "voice_search",
    "language_search",
    "named_voice_filter",
    "voice_favorites",
    "planned_language_guard",
    "all_expression_sounds",
    "themed_story_generation",
    "voice_preview",
    "cancel_generation",
    "request_timer",
    "audio_play_pause",
    "audio_seek_back",
    "audio_seek_forward",
    "playback_speed",
    "playback_volume",
    "audio_loop",
    "audio_visualizer",
    "local_session_history",
    "pinned_history_items",
    "history_restore",
    "history_delete",
    "download_wav",
    "download_text",
    "download_markup",
    "download_session_json",
    "copy_text",
    "copy_markup",
    "local_diagnostics",
    "activity_log",
    "serial_line_batch",
)

CONSOLE_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark light">
  <title>Nastech TTS — Local Voice Studio</title>
  <style>
    :root {
      --ink: #e9edff; --muted: #aeb8dc; --surface: rgba(19,27,55,.83); --surface-2: rgba(31,42,79,.92);
      --line: rgba(174,193,255,.18); --accent: #92f6d0; --accent-2: #8fa9ff; --danger: #ff9fa7;
      --bg: #0a1026; --glow: rgba(104,168,255,.38); --shadow: rgba(0,0,0,.18);
    }
    [data-theme="sunrise"] { --ink:#2b1931; --muted:#765a6a; --surface:rgba(255,249,244,.90); --surface-2:rgba(255,237,226,.96); --line:rgba(115,62,83,.15); --accent:#af4567; --accent-2:#d07a48; --danger:#b4233e; --bg:#ffe6d5; --glow:rgba(255,143,106,.32); --shadow:rgba(111,48,58,.12); }
    [data-theme="paper"] { --ink:#15221c; --muted:#53665a; --surface:rgba(253,254,250,.94); --surface-2:rgba(237,244,234,.98); --line:rgba(28,69,44,.16); --accent:#18754a; --accent-2:#3d7d98; --danger:#b3373f; --bg:#e7eee5; --glow:rgba(71,141,87,.22); --shadow:rgba(28,69,44,.12); }
    [data-contrast="on"] { --ink:#fff; --muted:#d7defb; --surface:#121a34; --surface-2:#202d58; --line:#c9d6ff; --accent:#7fffd4; --danger:#ffbbc3; }
    [data-theme="sunrise"][data-contrast="on"], [data-theme="paper"][data-contrast="on"] { --ink:#101010; --muted:#292929; --surface:#fff; --surface-2:#f6f6f6; --line:#101010; --accent:#005c34; --danger:#8b0018; }
    * { box-sizing:border-box; }
    html { font-size:var(--base-font,16px); }
    body { margin:0; min-height:100vh; color:var(--ink); background:radial-gradient(circle at 15% 5%,var(--glow),transparent 31rem),radial-gradient(circle at 95% 100%,rgba(133,92,255,.16),transparent 32rem),var(--bg); font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
    body[data-motion="reduce"] *, body[data-motion="reduce"] *::before, body[data-motion="reduce"] *::after { animation-duration:.001ms!important; transition-duration:.001ms!important; scroll-behavior:auto!important; }
    .shell { width:min(1320px,calc(100% - 32px)); margin:0 auto; padding:26px 0 48px; }
    header { display:flex; align-items:center; justify-content:space-between; gap:18px; margin-bottom:18px; }
    .brand { display:flex; align-items:center; gap:14px; }.mark { width:46px;height:46px;border-radius:16px;display:grid;place-items:center;color:var(--bg);background:linear-gradient(135deg,var(--accent),var(--accent-2));font-weight:900;font-size:22px;box-shadow:0 10px 26px var(--shadow); } h1 { font-size:clamp(1.25rem,2.8vw,1.8rem);margin:0;letter-spacing:-.04em; }.eyebrow,.note,.subtle { color:var(--muted);font-size:.82rem; }.header-tools,.themes,.actions,.mini-actions,.chip-row { display:flex;flex-wrap:wrap;gap:8px;align-items:center; }
    button,select,textarea,input { font:inherit; } button { border:1px solid var(--line);background:var(--surface-2);color:var(--ink);border-radius:10px;cursor:pointer;padding:9px 12px; }button:hover { border-color:var(--accent);transform:translateY(-1px); }button:focus-visible,select:focus-visible,textarea:focus-visible,input:focus-visible { outline:3px solid var(--glow);outline-offset:2px; }button.active,.primary { color:var(--bg);border-color:transparent;background:linear-gradient(135deg,var(--accent),var(--accent-2));font-weight:750; }button.danger { color:var(--danger); }button:disabled { opacity:.56;cursor:wait;transform:none; }.icon { padding:7px 10px;min-width:39px; }.pill { border-radius:999px; }
    .workspace { display:grid;grid-template-columns:minmax(0,1.3fr) minmax(300px,.7fr);gap:18px; }.card { background:var(--surface);border:1px solid var(--line);border-radius:20px;padding:19px;box-shadow:0 18px 45px var(--shadow);backdrop-filter:blur(16px); }.card h2 { font-size:1rem;margin:0 0 13px;letter-spacing:-.02em; }.stack { display:grid;gap:13px; }.two,.three { display:grid;gap:10px; }.two { grid-template-columns:repeat(2,minmax(0,1fr)); }.three { grid-template-columns:repeat(3,minmax(0,1fr)); }label { display:grid;gap:7px;font-size:.84rem;color:var(--muted); }select,textarea,input { color:var(--ink);background:color-mix(in srgb,var(--surface-2) 86%,transparent);border:1px solid var(--line);border-radius:10px;padding:10px 11px;width:100%; }textarea { resize:vertical;min-height:180px;line-height:1.5; }.row { display:flex;justify-content:space-between;gap:10px;align-items:center; }.counter { color:var(--muted);font-size:.8rem; }.sounds { display:flex;flex-wrap:wrap;gap:7px; }.sounds label,.toggle { display:flex;align-items:center;gap:6px;padding:7px 9px;border:1px solid var(--line);border-radius:999px;color:var(--ink);cursor:pointer; }.sounds input,.toggle input { accent-color:var(--accent);width:auto; }.status { min-height:25px;color:var(--muted);font-size:.88rem; }.status.error { color:var(--danger); }.status.ok { color:var(--accent); }.audio-wrap { display:grid;gap:9px; }.download { color:var(--accent);font-size:.88rem;text-decoration:none;display:none; }.audio-tools { display:grid;grid-template-columns:auto auto auto 1fr auto auto;gap:8px;align-items:center; }.audio-tools input { padding:0; }.audio-tools select { padding:7px; }.visualizer { width:100%;height:54px;border:1px solid var(--line);border-radius:10px;background:color-mix(in srgb,var(--surface-2) 82%,transparent); }.sidebar { display:grid;gap:18px;align-content:start; }.metric { display:grid;grid-template-columns:1fr auto;border-top:1px solid var(--line);padding:10px 0;gap:12px;font-size:.88rem; }.metric:last-child { border-bottom:1px solid var(--line); }.metric b { font-weight:700;text-align:right; }.history { display:grid;gap:8px;max-height:285px;overflow:auto;padding-right:3px; }.history-item { display:grid;grid-template-columns:1fr auto;gap:7px;padding:9px;border:1px solid var(--line);border-radius:11px;background:color-mix(in srgb,var(--surface-2) 55%,transparent); }.history-item button:first-child { border:0;background:transparent;text-align:left;padding:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap; }.history-item small { color:var(--muted);display:block;margin-top:3px; }.history-item .mini-actions { gap:4px; }.history-item .mini-actions button { padding:4px 6px;font-size:.75rem; }.panel { border:1px solid var(--line);border-radius:13px;padding:11px; }.panel summary { cursor:pointer;font-weight:650; }.panel[open] summary { margin-bottom:11px; }.hidden { display:none!important; }.modal { position:fixed;inset:0;background:rgba(2,5,16,.5);display:grid;place-items:center;padding:20px;z-index:5; }.modal-card { width:min(560px,100%);background:var(--surface-2);border:1px solid var(--line);border-radius:18px;padding:20px;box-shadow:0 24px 80px rgba(0,0,0,.35); }.shortcut-list { display:grid;grid-template-columns:auto 1fr;gap:9px 13px; }.shortcut-list kbd { border:1px solid var(--line);border-radius:6px;padding:2px 6px;justify-self:start;background:var(--surface); }.activity { margin:0;padding-left:18px;color:var(--muted);font-size:.82rem;line-height:1.55; }.empty { color:var(--muted);font-size:.86rem;padding:7px 0; }.compact-only { display:none; }body[data-compact="on"] .compact-only { display:block; }body[data-compact="on"] .card { padding:14px;border-radius:15px; }body[data-compact="on"] textarea { min-height:120px; }body[data-compact="on"] .sidebar { gap:12px; }
    @media (max-width:960px) { .workspace { grid-template-columns:1fr; }.sidebar { grid-template-columns:repeat(2,minmax(0,1fr)); }.sidebar .wide { grid-column:1/-1; } }@media (max-width:680px) { .shell { width:min(100% - 20px,1320px);padding-top:16px; }header { align-items:flex-start;flex-direction:column; }.two,.three { grid-template-columns:1fr; }.sidebar { grid-template-columns:1fr; }.audio-tools { grid-template-columns:repeat(3,1fr); }.audio-tools input { grid-column:1/-1; }.header-tools { justify-content:flex-start; } }
  </style>
</head>
<body data-theme="midnight" data-contrast="off" data-compact="off" data-motion="full">
  <main class="shell">
    <header>
      <div class="brand"><div class="mark">N</div><div><div class="eyebrow">NASTECH RESEARCH · LOCAL-FIRST</div><h1>Voice Studio</h1></div></div>
      <div class="header-tools">
        <div class="themes" aria-label="Choose console theme"><button class="theme active" data-theme-choice="midnight">Midnight</button><button class="theme" data-theme-choice="sunrise">Sunrise</button><button class="theme" data-theme-choice="paper">Paper</button></div>
        <button id="fontDown" class="icon" title="Decrease font size" aria-label="Decrease font size">A−</button><button id="fontUp" class="icon" title="Increase font size" aria-label="Increase font size">A+</button><button id="help" class="icon" title="Keyboard shortcuts" aria-label="Keyboard shortcuts">?</button>
      </div>
    </header>
    <section class="workspace">
      <section class="card" aria-label="Create local speech">
        <div class="row"><h2>Create voice</h2><div class="chip-row"><button id="normalize" class="pill">Clean text</button><button id="clearText" class="pill danger">Clear</button></div></div>
        <div class="stack">
          <label>Text to speak<textarea id="text" spellcheck="true">Welcome to Nastech Research. Your voice stays local, clear, and ready to be heard.</textarea></label>
          <div class="row counter"><span id="counters">0 characters · 0 words · ≈ 0s speech</span><span id="draftState">Draft saved locally</span></div>
          <div class="row"><span class="eyebrow">Writing templates</span><div class="chip-row"><button data-template="welcome" class="template pill">Welcome</button><button data-template="narration" class="template pill">Narration</button><button data-template="announcement" class="template pill">Announcement</button><button data-template="lesson" class="template pill">Lesson</button><button data-template="story" class="template pill">Story</button></div></div>
          <div class="two">
            <label>Language search<input id="languageSearch" type="search" placeholder="Find lg - Luganda…"></label>
            <label>Voice search<input id="voiceSearch" type="search" placeholder="Find Siya, F1, soft…"></label>
            <label>Language<select id="language"><option value="en">en - English</option></select></label>
            <label>Voice profile<select id="voice"><option value="siya">Siya · F1</option></select></label>
            <label>Emotion<select id="emotion"><option value="neutral">Neutral</option><option value="calm">Calm</option><option value="happy">Happy</option><option value="excited">Excited</option><option value="surprised">Surprised</option><option value="sad">Sad</option><option value="angry">Angry</option><option value="frustrated">Frustrated</option><option value="fearful">Fearful</option><option value="disgusted">Disgusted</option></select></label>
            <label>Delivery<select id="rate"><option value="normal">Normal</option><option value="slow">Soft / slow</option><option value="fast">Dynamic / fast</option></select></label>
          </div>
          <div class="chip-row"><label class="toggle"><input id="namedOnly" type="checkbox"> Named voices only</label><label class="toggle"><input id="favoriteVoice" type="checkbox"> Favourite this voice</label><label class="toggle"><input id="showPlans" type="checkbox"> Show planned languages</label></div>
          <div><div class="row"><span class="eyebrow">Optional expression sounds</span><button id="clearSounds" class="pill">Clear sounds</button></div><div class="sounds" id="sounds"></div></div>
          <details class="panel"><summary>Production tools</summary><div class="stack"><div class="two"><label>Story theme<select id="storyTheme"><option value="innovation">Innovation</option><option value="heritage">Heritage</option><option value="education">Education</option><option value="community">Community</option></select></label><label>Batch limit<select id="batchLimit"><option value="2">2 lines</option><option value="4" selected>4 lines</option><option value="8">8 lines</option></select></label></div><div class="chip-row"><button id="previewVoice">Preview voice</button><button id="makeStory">Make themed story</button><button id="queueLines">Render lines in order</button><button id="copyText">Copy text</button><button id="copyMarkup">Copy markup</button></div><p class="subtle">Batch rendering uses non-empty lines from the editor, one local request at a time. The latest result stays in the player and each line is kept in local history.</p></div></details>
          <div class="actions"><button id="synthesize" class="primary">Generate &amp; play</button><button id="cancel" class="hidden danger">Cancel</button><button id="clearAudio">Clear audio</button><button id="replayLast">Replay last</button></div>
          <div id="status" class="status" role="status" aria-live="polite">Ready. Your first synthesis may load the selected local model.</div>
          <div class="audio-wrap"><audio id="audio" controls preload="metadata"></audio><canvas id="visualizer" class="visualizer" aria-label="Audio level visualizer"></canvas><div class="audio-tools"><button id="seekBack" class="icon" title="Back five seconds">−5s</button><button id="playPause" class="icon" title="Play or pause">Play</button><button id="seekForward" class="icon" title="Forward five seconds">+5s</button><label>Speed<select id="playbackRate"><option value="0.75">0.75×</option><option value="1" selected>1×</option><option value="1.25">1.25×</option><option value="1.5">1.5×</option></select></label><label>Volume<input id="playbackVolume" type="range" min="0" max="1" step="0.05" value="1"></label><label class="toggle"><input id="loopAudio" type="checkbox"> Loop</label></div><a id="download" class="download" download="nastech-local-voice.wav">Download local WAV</a><div class="mini-actions"><button id="downloadText">Download text</button><button id="downloadMarkup">Download markup</button><button id="downloadSession">Download session JSON</button></div></div>
        </div>
      </section>
      <aside class="sidebar" aria-label="Studio details and history">
        <section class="card"><h2>Local runtime</h2><div class="metric"><span>Voice profiles</span><b id="profileCount">Loading…</b></div><div class="metric"><span>Language catalog</span><b id="languageCount">Loading…</b></div><div class="metric"><span>Output</span><b>WAV · local delivery</b></div><div class="metric"><span>Connection</span><b id="health">Checking…</b></div><div class="metric"><span>Last request</span><b id="requestTime">—</b></div><div class="metric"><span>Saved sessions</span><b id="historyCount">0</b></div><div class="auth"><label>Optional API key <input id="apiKey" type="password" autocomplete="off" placeholder="Needed only if you started the API with NASTECH_API_KEY"></label></div></section>
        <section class="card wide"><div class="row"><h2>Local session history</h2><button id="clearHistory" class="pill danger">Clear history</button></div><div id="history" class="history"><div class="empty">No local sessions yet.</div></div><p class="subtle">History saves text and settings in this browser only. WAV blobs are not persisted.</p></section>
        <section class="card"><div class="row"><h2>Studio preferences</h2><button id="resetPrefs" class="pill">Reset</button></div><div class="stack"><label class="toggle"><input id="highContrast" type="checkbox"> High contrast</label><label class="toggle"><input id="compactMode" type="checkbox"> Compact layout</label><label class="toggle"><input id="reduceMotion" type="checkbox"> Reduce motion</label><button id="showDiagnostics">Show local diagnostics</button><div id="diagnostics" class="subtle hidden"></div></div></section>
        <section class="card wide"><h2>Activity</h2><ul id="activity" class="activity"><li>Studio loaded locally.</li></ul></section>
      </aside>
    </section>
  </main>
  <div id="helpModal" class="modal hidden" role="dialog" aria-modal="true" aria-labelledby="helpTitle"><section class="modal-card"><div class="row"><h2 id="helpTitle">Keyboard shortcuts</h2><button id="closeHelp" class="icon" aria-label="Close help">×</button></div><div class="shortcut-list"><kbd>Ctrl / Cmd + Enter</kbd><span>Generate and play local speech</span><kbd>Ctrl / Cmd + Shift + C</kbd><span>Copy the generated markup</span><kbd>Ctrl / Cmd + Shift + V</kbd><span>Preview the selected voice</span><kbd>Escape</kbd><span>Close this help window or cancel a request</span></div><p class="subtle">All drafts, preferences, favourites, and history remain in this browser. Clearing browser site data removes them.</p></section></div>
  <script>
    const $ = (id) => document.getElementById(id);
    const STORE = 'nastech-studio-v2';
    const templates = {
      welcome: 'Welcome to Nastech Research. Your voice stays local, clear, and ready to be heard.',
      narration: 'At first light, the team gathered the ideas that would become a practical local voice system. Every sentence was shaped with care.',
      announcement: 'Attention, everyone. The local voice studio is ready. Choose your voice, review your text, and generate your audio on this device.',
      lesson: 'Today we will learn one clear idea. Read the sentence slowly, listen closely, and repeat the important words with confidence.',
      story: 'The rain softened over the hills. A small lamp glowed in the window, and the storyteller began with a warm and hopeful voice.'
    };
    const soundNames = ['laugh','chuckle','sigh','cough','sniffle','groan','yawn','gasp','cry','scream','throatclear'];
    let audioUrl = null, controller = null, voices = [], languages = [], audioContext = null, analyser = null, animationId = null;
    let state = { theme:'midnight', contrast:false, compact:false, motion:false, fontSize:16, draft:'', favorites:[], history:[], activity:[] };
    function safeLoad() { try { return { ...state, ...JSON.parse(localStorage.getItem(STORE) || '{}') }; } catch (_) { return state; } }
    function save() { localStorage.setItem(STORE, JSON.stringify(state)); }
    function clip(value, length=68) { return value.length > length ? `${value.slice(0,length - 1)}…` : value; }
    function now() { return new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}); }
    function log(message) { state.activity = [{time:now(),message}, ...state.activity].slice(0,6); save(); renderActivity(); }
    function setStatus(text, kind='') { const node=$('status'); node.textContent=text; node.className=`status ${kind}`; }
    function headers() { const key=$('apiKey').value.trim(); return key ? {'Authorization':`Bearer ${key}`} : {}; }
    function textValue() { return $('text').value.trim(); }
    function escapeText(value) { const node=document.createElement('span'); node.textContent=value; return node.innerHTML; }
    function selectedSounds() { return [...document.querySelectorAll('[data-sound]:checked')].map(item=>item.dataset.sound); }
    function markup(text=textValue()) { const cues=selectedSounds().map(name=>`<sound type="${name}" />`).join(''); const emotion=$('emotion').value; const spoken=emotion==='neutral' ? escapeText(text) : `<emotion name="${emotion}">${escapeText(text)}</emotion>`; return `<speak voice="${$('voice').value}"><prosody rate="${$('rate').value}">${spoken}${cues}</prosody></speak>`; }
    function applyPrefs() { document.body.dataset.theme=state.theme; document.body.dataset.contrast=state.contrast?'on':'off'; document.body.dataset.compact=state.compact?'on':'off'; document.body.dataset.motion=state.motion?'reduce':'full'; document.documentElement.style.setProperty('--base-font', `${state.fontSize}px`); document.querySelectorAll('.theme').forEach(button=>button.classList.toggle('active',button.dataset.themeChoice===state.theme)); $('highContrast').checked=state.contrast; $('compactMode').checked=state.compact; $('reduceMotion').checked=state.motion; }
    function updateCounters() { const value=$('text').value; const words=value.trim()?value.trim().split(/\s+/).length:0; const seconds=Math.max(0,Math.round(words/2.5)); $('counters').textContent=`${value.length.toLocaleString()} characters · ${words.toLocaleString()} words · ≈ ${seconds}s speech`; state.draft=value; save(); }
    function downloadBlob(body, type, name) { const url=URL.createObjectURL(new Blob([body],{type})); const a=document.createElement('a'); a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000); }
    async function copy(value, label) { try { await navigator.clipboard.writeText(value); setStatus(`${label} copied locally.`, 'ok'); log(`${label} copied.`); } catch (_) { setStatus(`Could not copy ${label.toLowerCase()}. Select it manually.`, 'error'); } }
    function currentSession(duration=null) { return { id:crypto.randomUUID(), created_at:new Date().toISOString(), text:textValue(), voice:$('voice').value, language:$('language').value, emotion:$('emotion').value, rate:$('rate').value, sounds:selectedSounds(), markup:markup(), duration, pinned:false }; }
    function persistSession(session) { const existing=state.history.findIndex(item=>item.text===session.text && item.voice===session.voice && item.language===session.language); if(existing>=0) state.history.splice(existing,1); state.history.unshift(session); state.history=state.history.slice(0,14); save(); renderHistory(); }
    function restoreSession(id) { const item=state.history.find(entry=>entry.id===id); if(!item) return; $('text').value=item.text; $('emotion').value=item.emotion; $('rate').value=item.rate; populateOptions(); $('voice').value=item.voice; $('language').value=item.language; document.querySelectorAll('[data-sound]').forEach(box=>box.checked=item.sounds.includes(box.dataset.sound)); updateCounters(); setStatus('Session restored. Generate to create a fresh local WAV.', 'ok'); log('History session restored.'); }
    function renderHistory() { const root=$('history'); root.replaceChildren(); $('historyCount').textContent=String(state.history.length); if(!state.history.length) { root.innerHTML='<div class="empty">No local sessions yet.</div>'; return; } state.history.sort((a,b)=>Number(b.pinned)-Number(a.pinned)).forEach(item=>{ const row=document.createElement('div');row.className='history-item'; const load=document.createElement('button');load.textContent=`${item.pinned?'★ ':''}${clip(item.text)}`;load.title='Restore this session';load.addEventListener('click',()=>restoreSession(item.id)); const meta=document.createElement('small');meta.textContent=`${item.language} · ${item.voice} · ${new Date(item.created_at).toLocaleString()}`;const left=document.createElement('div');left.append(load,meta); const actions=document.createElement('div');actions.className='mini-actions'; const pin=document.createElement('button');pin.textContent=item.pinned?'Unpin':'Pin';pin.addEventListener('click',()=>{item.pinned=!item.pinned;save();renderHistory();}); const remove=document.createElement('button');remove.textContent='Delete';remove.addEventListener('click',()=>{state.history=state.history.filter(entry=>entry.id!==item.id);save();renderHistory();});actions.append(pin,remove);row.append(left,actions);root.append(row);}); }
    function renderActivity() { const root=$('activity');root.replaceChildren();state.activity.forEach(entry=>{const li=document.createElement('li');li.textContent=`${entry.time} — ${entry.message}`;root.append(li);}); }
    function updateFavoriteControl() { $('favoriteVoice').checked=state.favorites.includes($('voice').value); }
    function filteredVoices() { const query=$('voiceSearch').value.toLowerCase().trim();return voices.filter(profile=>{const value=`${profile.profile_id} ${profile.label} ${profile.base_voice} ${profile.kind||''}`.toLowerCase();return (!query||value.includes(query))&&(!$('namedOnly').checked||profile.kind==='named');}).sort((a,b)=>Number(state.favorites.includes(b.profile_id))-Number(state.favorites.includes(a.profile_id))); }
    function filteredLanguages() { const query=$('languageSearch').value.toLowerCase().trim();return languages.filter(language=>{const value=`${language.code} ${language.display_label}`.toLowerCase();return (!query||value.includes(query))&&($('showPlans').checked||language.code==='en'||language.state!=='planned');}); }
    function populateOptions() { const priorVoice=$('voice').value, priorLanguage=$('language').value; $('voice').replaceChildren();filteredVoices().forEach(profile=>{const option=document.createElement('option');option.value=profile.profile_id;option.textContent=`${state.favorites.includes(profile.profile_id)?'★ ':''}${profile.label} · ${profile.base_voice}`;$('voice').append(option);});$('language').replaceChildren();filteredLanguages().forEach(language=>{const option=document.createElement('option');option.value=language.code;option.textContent=language.display_label;option.disabled=language.code!=='en'&&language.state==='planned';$('language').append(option);}); if([...$('voice').options].some(option=>option.value===priorVoice)) $('voice').value=priorVoice;if([...$('language').options].some(option=>option.value===priorLanguage)) $('language').value=priorLanguage;updateFavoriteControl(); }
    function clearAudio() { $('audio').pause();$('audio').removeAttribute('src');$('audio').load();$('download').style.display='none';if(audioUrl)URL.revokeObjectURL(audioUrl);audioUrl=null;$('playPause').textContent='Play';stopVisualizer();setStatus('Audio cleared.');log('Audio player cleared.'); }
    function receiveAudio(response,label,session) { if(!response.ok)return response.json().catch(()=>({})).then(data=>{throw new Error(data.detail||`Request failed (${response.status})`);});return response.blob().then(blob=>{if(audioUrl)URL.revokeObjectURL(audioUrl);audioUrl=URL.createObjectURL(blob);$('audio').src=audioUrl;$('download').href=audioUrl;$('download').style.display='inline';$('audio').play().catch(()=>{});const duration=response.headers.get('X-Nastech-Duration-Seconds');session.duration=duration?Number(duration):null;persistSession(session);setStatus(`${label} is ready${duration?` · ${duration}s`:''}.`,'ok');log(`${label} created locally.`);}); }
    async function synthesize(textOverride=null,label='Local WAV') { const text=(textOverride ?? textValue()).trim();if(!text){setStatus('Write text before generating audio.','error');return false;}const button=$('synthesize');button.disabled=true;$('cancel').classList.remove('hidden');const started=performance.now();setStatus('Generating locally…');controller=new AbortController();try{const language=$('language').value;const body={markup:markup(text),voice:$('voice').value,language,cleanup:true};if(language==='en')body.provider_id='nastech-native-onnx';await receiveAudio(await fetch('/v1/agent/speech',{method:'POST',headers:{'Content-Type':'application/json',...headers()},body:JSON.stringify(body),signal:controller.signal}),label,currentSession());$('requestTime').textContent=`${((performance.now()-started)/1000).toFixed(2)}s`;return true;}catch(error){setStatus(error.name==='AbortError'?'Generation cancelled.':error.message,'error');log(error.name==='AbortError'?'Generation cancelled.':'Generation needs attention.');return false;}finally{button.disabled=false;$('cancel').classList.add('hidden');controller=null;}}
    async function story() { const button=$('makeStory');button.disabled=true;$('cancel').classList.remove('hidden');const started=performance.now();setStatus('Composing and generating locally…');controller=new AbortController();try{const response=await fetch('/v1/agent/story',{method:'POST',headers:{'Content-Type':'application/json',...headers()},body:JSON.stringify({theme:$('storyTheme').value,emotion:$('emotion').value,sounds:selectedSounds().slice(0,3),voice:$('voice').value,render:true,cleanup:true}),signal:controller.signal});await receiveAudio(response,'Themed Nastech story',currentSession());$('requestTime').textContent=`${((performance.now()-started)/1000).toFixed(2)}s`;}catch(error){setStatus(error.name==='AbortError'?'Story generation cancelled.':error.message,'error');}finally{button.disabled=false;$('cancel').classList.add('hidden');controller=null;}}
    async function batch() { const lines=$('text').value.split(/\n+/).map(line=>line.trim()).filter(Boolean).slice(0,Number($('batchLimit').value));if(lines.length<2){setStatus('Add at least two non-empty lines for batch rendering.','error');return;}for(let index=0;index<lines.length;index++){setStatus(`Rendering line ${index+1} of ${lines.length} locally…`);const ok=await synthesize(lines[index],`Batch line ${index+1}`);if(!ok)break;}log(`Batch workflow finished for ${lines.length} line(s).`);}
    function setupVisualizer(){ if(audioContext||!$('audio').src)return;try{audioContext=new (window.AudioContext||window.webkitAudioContext)();const source=audioContext.createMediaElementSource($('audio'));analyser=audioContext.createAnalyser();analyser.fftSize=64;source.connect(analyser);analyser.connect(audioContext.destination);drawVisualizer();}catch(_){/* Native audio playback remains available if visualisation is unavailable. */}}
    function drawVisualizer(){ if(!analyser)return;const canvas=$('visualizer'),ctx=canvas.getContext('2d'),width=canvas.width=canvas.clientWidth*devicePixelRatio,height=canvas.height=canvas.clientHeight*devicePixelRatio,data=new Uint8Array(analyser.frequencyBinCount);const frame=()=>{analyser.getByteFrequencyData(data);ctx.clearRect(0,0,width,height);ctx.fillStyle=getComputedStyle(document.body).getPropertyValue('--accent');const gap=3*devicePixelRatio,bar=(width-gap*(data.length-1))/data.length;data.forEach((value,index)=>{const h=Math.max(2,(value/255)*height);ctx.fillRect(index*(bar+gap),height-h,bar,h);});animationId=requestAnimationFrame(frame);};frame();}
    function stopVisualizer(){if(animationId)cancelAnimationFrame(animationId);animationId=null;}
    async function loadConsole(){ soundNames.forEach(name=>{const label=document.createElement('label');label.innerHTML=`<input type="checkbox" data-sound="${name}"> ${name}`;$('sounds').append(label);});try{const [voicesResponse,languagesResponse,healthResponse]=await Promise.all([fetch('/v1/voices',{headers:headers()}),fetch('/v1/languages',{headers:headers()}),fetch('/v1/health')]);const voiceData=await voicesResponse.json(),languageData=await languagesResponse.json(),health=await healthResponse.json();voices=voiceData.profiles||[];languages=languageData.languages||[];populateOptions();$('profileCount').textContent=`${voiceData.summary.selectable_profiles} profiles`;$('languageCount').textContent=`${languageData.language_registry_size} targets`;$('health').textContent=health.status==='ok'?'Ready':'Check status';log('Local API connection ready.');}catch(_){$('health').textContent='API unavailable';setStatus('The studio could not reach the local API. Start `nastech-tts serve` and refresh.','error');}}
    function diagnostics(){const payload={theme:state.theme,voice:$('voice').value,language:$('language').value,history:state.history.length,storage_bytes:new Blob([JSON.stringify(state)]).size,online:navigator.onLine,agent:'local browser console'};$('diagnostics').textContent=JSON.stringify(payload,null,2);$('diagnostics').classList.remove('hidden');}
    function resetPreferences(){state={...state,theme:'midnight',contrast:false,compact:false,motion:false,fontSize:16,favorites:[]};save();applyPrefs();populateOptions();setStatus('Studio preferences reset.','ok');}
    state=safeLoad();$('text').value=state.draft||$('text').value;applyPrefs();updateCounters();renderHistory();renderActivity();
    document.querySelectorAll('.theme').forEach(button=>button.addEventListener('click',()=>{state.theme=button.dataset.themeChoice;save();applyPrefs();log(`Theme changed to ${state.theme}.`);}));
    $('fontDown').addEventListener('click',()=>{state.fontSize=Math.max(13,state.fontSize-1);save();applyPrefs();});$('fontUp').addEventListener('click',()=>{state.fontSize=Math.min(21,state.fontSize+1);save();applyPrefs();});
    [['highContrast','contrast'],['compactMode','compact'],['reduceMotion','motion']].forEach(([id,key])=>$ (id).addEventListener('change',event=>{state[key]=event.target.checked;save();applyPrefs();}));
    $('resetPrefs').addEventListener('click',resetPreferences);$('text').addEventListener('input',updateCounters);$('normalize').addEventListener('click',()=>{$('text').value=$('text').value.replace(/[ \t]+/g,' ').replace(/ *\n */g,'\n').replace(/\n{3,}/g,'\n\n').trim();updateCounters();setStatus('Text cleaned locally.','ok');log('Text cleaned.');});$('clearText').addEventListener('click',()=>{if(confirm('Clear the current text draft?')){$('text').value='';updateCounters();setStatus('Draft cleared.');}});document.querySelectorAll('.template').forEach(button=>button.addEventListener('click',()=>{$('text').value=templates[button.dataset.template];updateCounters();setStatus(`${button.textContent} template loaded locally.`,'ok');}));
    ['voiceSearch','languageSearch','namedOnly','showPlans'].forEach(id=>$ (id).addEventListener(id.includes('Search')?'input':'change',populateOptions));$('voice').addEventListener('change',updateFavoriteControl);$('favoriteVoice').addEventListener('change',event=>{const voice=$('voice').value;if(event.target.checked&&!state.favorites.includes(voice))state.favorites.push(voice);if(!event.target.checked)state.favorites=state.favorites.filter(item=>item!==voice);save();populateOptions();log('Voice favourites updated.');});$('clearSounds').addEventListener('click',()=>document.querySelectorAll('[data-sound]').forEach(box=>box.checked=false));
    $('synthesize').addEventListener('click',()=>synthesize());$('previewVoice').addEventListener('click',()=>synthesize(`Hello. This is ${$('voice').selectedOptions[0]?.textContent||'the selected voice'} in the Nastech local voice studio.`,'Voice preview'));$('makeStory').addEventListener('click',story);$('queueLines').addEventListener('click',batch);$('cancel').addEventListener('click',()=>controller?.abort());$('clearAudio').addEventListener('click',clearAudio);$('replayLast').addEventListener('click',()=>{$('audio').play().catch(()=>setStatus('Generate audio before replaying.','error'));});
    $('copyText').addEventListener('click',()=>copy(textValue(),'Text'));$('copyMarkup').addEventListener('click',()=>copy(markup(),'Markup'));$('downloadText').addEventListener('click',()=>downloadBlob(textValue(),'text/plain','nastech-script.txt'));$('downloadMarkup').addEventListener('click',()=>downloadBlob(markup(),'application/xml','nastech-markup.xml'));$('downloadSession').addEventListener('click',()=>downloadBlob(JSON.stringify(currentSession(),null,2),'application/json','nastech-session.json'));
    $('clearHistory').addEventListener('click',()=>{if(confirm('Delete local session history?')){state.history=[];save();renderHistory();setStatus('Local history cleared.');}});$('showDiagnostics').addEventListener('click',diagnostics);
    $('audio').addEventListener('play',()=>{setupVisualizer();audioContext?.resume();$('playPause').textContent='Pause';});$('audio').addEventListener('pause',()=>{$('playPause').textContent='Play';});$('audio').addEventListener('ended',()=>{$('playPause').textContent='Play';stopVisualizer();});$('playPause').addEventListener('click',()=>{$('audio').paused?$('audio').play().catch(()=>setStatus('Generate audio before playing.','error')):$('audio').pause();});$('seekBack').addEventListener('click',()=>{$('audio').currentTime=Math.max(0,($('audio').currentTime||0)-5);});$('seekForward').addEventListener('click',()=>{$('audio').currentTime=Math.min($('audio').duration||Infinity,($('audio').currentTime||0)+5);});$('playbackRate').addEventListener('change',event=>$('audio').playbackRate=Number(event.target.value));$('playbackVolume').addEventListener('input',event=>$('audio').volume=Number(event.target.value));$('loopAudio').addEventListener('change',event=>$('audio').loop=event.target.checked);
    $('help').addEventListener('click',()=>$('helpModal').classList.remove('hidden'));$('closeHelp').addEventListener('click',()=>$('helpModal').classList.add('hidden'));$('helpModal').addEventListener('click',event=>{if(event.target===$('helpModal'))$('helpModal').classList.add('hidden');});document.addEventListener('keydown',event=>{if((event.ctrlKey||event.metaKey)&&event.key==='Enter'){event.preventDefault();synthesize();}if((event.ctrlKey||event.metaKey)&&event.shiftKey&&event.key.toLowerCase()==='c'){event.preventDefault();copy(markup(),'Markup');}if((event.ctrlKey||event.metaKey)&&event.shiftKey&&event.key.toLowerCase()==='v'){event.preventDefault();$('previewVoice').click();}if(event.key==='Escape'){if(!$('helpModal').classList.contains('hidden'))$('helpModal').classList.add('hidden');else controller?.abort();}});
    loadConsole();
  </script>
</body>
</html>"""


def render_console() -> str:
    """Return the static local console document without external assets."""

    return CONSOLE_HTML
