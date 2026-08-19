"""Self-contained browser console for the local Nastech TTS API."""

# ruff: noqa: E501

CONSOLE_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark light">
  <title>Nastech TTS — Local Voice Console</title>
  <style>
    :root {
      --ink: #e9edff;
      --muted: #aeb8dc;
      --surface: rgba(19, 27, 55, .82);
      --surface-2: rgba(31, 42, 79, .9);
      --line: rgba(174, 193, 255, .18);
      --accent: #92f6d0;
      --accent-2: #8fa9ff;
      --danger: #ff9fa7;
      --bg: #0a1026;
      --glow: rgba(104, 168, 255, .38);
    }
    [data-theme="sunrise"] {
      --ink: #2b1931;
      --muted: #765a6a;
      --surface: rgba(255, 249, 244, .88);
      --surface-2: rgba(255, 237, 226, .94);
      --line: rgba(115, 62, 83, .15);
      --accent: #af4567;
      --accent-2: #d07a48;
      --danger: #b4233e;
      --bg: #ffe6d5;
      --glow: rgba(255, 143, 106, .32);
    }
    [data-theme="paper"] {
      --ink: #15221c;
      --muted: #53665a;
      --surface: rgba(253, 254, 250, .92);
      --surface-2: rgba(237, 244, 234, .96);
      --line: rgba(28, 69, 44, .16);
      --accent: #18754a;
      --accent-2: #3d7d98;
      --danger: #b3373f;
      --bg: #e7eee5;
      --glow: rgba(71, 141, 87, .22);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0; min-height: 100vh; color: var(--ink); background:
        radial-gradient(circle at 15% 5%, var(--glow), transparent 31rem),
        radial-gradient(circle at 95% 100%, rgba(133, 92, 255, .16), transparent 32rem), var(--bg);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .shell { width: min(1180px, calc(100% - 32px)); margin: 0 auto; padding: 30px 0 48px; }
    header { display: flex; align-items: center; justify-content: space-between; gap: 18px; margin-bottom: 24px; }
    .brand { display: flex; align-items: center; gap: 14px; }
    .mark { width: 46px; height: 46px; border-radius: 16px; display: grid; place-items: center;
      color: var(--bg); background: linear-gradient(135deg, var(--accent), var(--accent-2)); font-weight: 900; font-size: 22px; }
    h1 { font-size: clamp(1.25rem, 2.8vw, 1.8rem); margin: 0; letter-spacing: -.04em; }
    .eyebrow, .note { color: var(--muted); font-size: .84rem; }
    .themes { display: flex; flex-wrap: wrap; gap: 8px; justify-content: end; }
    button, select, textarea, input { font: inherit; }
    button { border: 1px solid var(--line); background: var(--surface-2); color: var(--ink); border-radius: 10px; cursor: pointer; padding: 9px 12px; }
    button:hover { border-color: var(--accent); transform: translateY(-1px); }
    button:focus-visible, select:focus-visible, textarea:focus-visible, input:focus-visible { outline: 3px solid var(--glow); outline-offset: 2px; }
    button.active, .primary { color: var(--bg); border-color: transparent; background: linear-gradient(135deg, var(--accent), var(--accent-2)); font-weight: 750; }
    button:disabled { opacity: .56; cursor: wait; transform: none; }
    .grid { display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(300px, .75fr); gap: 18px; }
    .card { background: var(--surface); border: 1px solid var(--line); border-radius: 20px; padding: 20px; box-shadow: 0 18px 45px rgba(0, 0, 0, .11); backdrop-filter: blur(16px); }
    .card h2 { font-size: 1rem; margin: 0 0 14px; letter-spacing: -.02em; }
    .stack { display: grid; gap: 13px; }
    label { display: grid; gap: 7px; font-size: .86rem; color: var(--muted); }
    select, textarea, input { color: var(--ink); background: color-mix(in srgb, var(--surface-2) 85%, transparent); border: 1px solid var(--line); border-radius: 10px; padding: 10px 11px; width: 100%; }
    textarea { resize: vertical; min-height: 172px; line-height: 1.5; }
    .controls { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
    .sounds { display: flex; flex-wrap: wrap; gap: 8px; }
    .sounds label { display: flex; align-items: center; gap: 6px; padding: 7px 9px; border: 1px solid var(--line); border-radius: 999px; color: var(--ink); cursor: pointer; }
    .sounds input { accent-color: var(--accent); width: auto; }
    .actions { display: flex; flex-wrap: wrap; gap: 9px; padding-top: 2px; }
    .status { min-height: 24px; color: var(--muted); font-size: .88rem; }
    .status.error { color: var(--danger); }
    .status.ok { color: var(--accent); }
    .audio-wrap { display: grid; gap: 10px; }
    audio { width: 100%; accent-color: var(--accent); }
    .download { color: var(--accent); font-size: .88rem; text-decoration: none; display: none; }
    .metric { display: grid; grid-template-columns: 1fr auto; border-top: 1px solid var(--line); padding: 12px 0; gap: 12px; font-size: .9rem; }
    .metric:last-child { border-bottom: 1px solid var(--line); }
    .metric b { font-weight: 700; text-align: right; }
    .tips { margin: 14px 0 0; padding-left: 18px; color: var(--muted); font-size: .86rem; line-height: 1.55; }
    .auth { margin-top: 18px; }
    .hidden { display: none; }
    @media (max-width: 760px) { header { align-items: flex-start; flex-direction: column; } .themes { justify-content: start; } .grid { grid-template-columns: 1fr; } .controls { grid-template-columns: 1fr; } }
  </style>
</head>
<body data-theme="midnight">
  <main class="shell">
    <header>
      <div class="brand"><div class="mark">N</div><div><div class="eyebrow">NASTECH RESEARCH · LOCAL-FIRST</div><h1>Voice Console</h1></div></div>
      <div class="themes" aria-label="Choose console theme">
        <button class="theme active" data-theme-choice="midnight">Midnight</button>
        <button class="theme" data-theme-choice="sunrise">Sunrise</button>
        <button class="theme" data-theme-choice="paper">Paper</button>
      </div>
    </header>

    <section class="grid">
      <section class="card" aria-label="Create local speech">
        <h2>Create voice</h2>
        <div class="stack">
          <label>Text to speak<textarea id="text">Welcome to Nastech Research. Your voice stays local, clear, and ready to be heard.</textarea></label>
          <div class="controls">
            <label>Language<select id="language"><option value="en">en - English</option></select></label>
            <label>Voice profile<select id="voice"><option value="siya">Siya · F1</option></select></label>
            <label>Emotion<select id="emotion"><option value="neutral">Neutral</option><option value="calm">Calm</option><option value="happy">Happy</option><option value="excited">Excited</option><option value="surprised">Surprised</option><option value="sad">Sad</option><option value="angry">Angry</option><option value="fearful">Fearful</option></select></label>
            <label>Delivery<select id="rate"><option value="normal">Normal</option><option value="slow">Soft / slow</option><option value="fast">Dynamic / fast</option></select></label>
          </div>
          <div><div class="eyebrow" style="margin-bottom:8px">Optional sound cues</div><div class="sounds" id="sounds"></div></div>
          <div class="actions"><button id="synthesize" class="primary">Generate & play</button><button id="makeStory">Make themed story</button><button id="clearAudio">Clear audio</button></div>
          <div id="status" class="status" role="status">Ready. Your first synthesis may load the selected local model.</div>
          <div class="audio-wrap"><audio id="audio" controls preload="none"></audio><a id="download" class="download" download="nastech-local-voice.wav">Download local WAV</a></div>
        </div>
      </section>

      <aside class="card" aria-label="Local runtime details">
        <h2>Local runtime</h2>
        <div class="metric"><span>Voice profiles</span><b id="profileCount">Loading…</b></div>
        <div class="metric"><span>Language catalog</span><b id="languageCount">Loading…</b></div>
        <div class="metric"><span>Output</span><b>WAV · local delivery</b></div>
        <div class="metric"><span>Connection</span><b id="health">Checking…</b></div>
        <div class="auth"><label>Optional API key <input id="apiKey" type="password" autocomplete="off" placeholder="Needed only if you started the API with NASTECH_API_KEY"></label></div>
        <ul class="tips"><li>Choose a named profile such as Siya, Nasi, Jafta, Della, Axam, Alicia, Shanice, Adam, Shakira, or Shimah.</li><li>For a Bantu language, select an exact `lazy-downloadable` pack first. Planned languages are never substituted.</li><li>The player receives a real WAV response from this device and never sends your text to a cloud proxy.</li></ul>
      </aside>
    </section>
  </main>
  <script>
    const $ = (id) => document.getElementById(id);
    const themes = document.querySelectorAll('.theme');
    const soundNames = ['laugh', 'chuckle', 'sigh', 'cough', 'gasp', 'cry', 'scream', 'throatclear'];
    let audioUrl = null;

    function headers() {
      const key = $('apiKey').value.trim();
      return key ? { 'Authorization': `Bearer ${key}` } : {};
    }
    function setStatus(text, kind = '') { const node = $('status'); node.textContent = text; node.className = `status ${kind}`; }
    function escapeText(value) { const node = document.createElement('span'); node.textContent = value; return node.innerHTML; }
    function selectedSounds() { return [...document.querySelectorAll('[data-sound]:checked')].map(item => item.dataset.sound); }
    function markup() {
      const text = escapeText($('text').value.trim());
      const voice = $('voice').value;
      const emotion = $('emotion').value;
      const rate = $('rate').value;
      const cues = selectedSounds().map(name => `<sound type="${name}" />`).join('');
      const spoken = emotion === 'neutral' ? text : `<emotion name="${emotion}">${text}</emotion>`;
      return `<speak voice="${voice}"><prosody rate="${rate}">${spoken}${cues}</prosody></speak>`;
    }
    function receiveAudio(response, label) {
      if (!response.ok) return response.json().catch(() => ({})).then(data => { throw new Error(data.detail || `Request failed (${response.status})`); });
      return response.blob().then(blob => {
        if (audioUrl) URL.revokeObjectURL(audioUrl);
        audioUrl = URL.createObjectURL(blob);
        $('audio').src = audioUrl;
        $('download').href = audioUrl;
        $('download').style.display = 'inline';
        $('audio').play().catch(() => {});
        const duration = response.headers.get('X-Nastech-Duration-Seconds');
        setStatus(`${label} is ready${duration ? ` · ${duration}s` : ''}.`, 'ok');
      });
    }
    async function synthesize() {
      const text = $('text').value.trim();
      if (!text) { setStatus('Write text before generating audio.', 'error'); return; }
      const button = $('synthesize'); button.disabled = true; setStatus('Generating locally…');
      try {
        const language = $('language').value;
        const body = { markup: markup(), voice: $('voice').value, language, cleanup: true };
        if (language === 'en') body.provider_id = 'nastech-native-onnx';
        const response = await fetch('/v1/agent/speech', { method: 'POST', headers: { 'Content-Type': 'application/json', ...headers() }, body: JSON.stringify(body) });
        await receiveAudio(response, 'Local WAV');
      } catch (error) { setStatus(error.message, 'error'); } finally { button.disabled = false; }
    }
    async function story() {
      const button = $('makeStory'); button.disabled = true; setStatus('Composing and generating locally…');
      try {
        const response = await fetch('/v1/agent/story', { method: 'POST', headers: { 'Content-Type': 'application/json', ...headers() }, body: JSON.stringify({ theme: 'innovation', emotion: $('emotion').value, sounds: selectedSounds().slice(0, 3), voice: $('voice').value, render: true, cleanup: true }) });
        await receiveAudio(response, 'Themed Nastech story');
      } catch (error) { setStatus(error.message, 'error'); } finally { button.disabled = false; }
    }
    async function loadConsole() {
      soundNames.forEach(name => { const label = document.createElement('label'); label.innerHTML = `<input type="checkbox" data-sound="${name}"> ${name}`; $('sounds').append(label); });
      try {
        const [voicesResponse, languagesResponse, healthResponse] = await Promise.all([
          fetch('/v1/voices', { headers: headers() }), fetch('/v1/languages', { headers: headers() }), fetch('/v1/health')
        ]);
        const voices = await voicesResponse.json(); const languages = await languagesResponse.json(); const health = await healthResponse.json();
        if (voicesResponse.ok) { $('voice').replaceChildren(); voices.profiles.forEach(profile => { const option = document.createElement('option'); option.value = profile.profile_id; option.textContent = `${profile.label} · ${profile.base_voice}`; $('voice').append(option); }); $('profileCount').textContent = `${voices.summary.selectable_profiles} profiles`; }
        if (languagesResponse.ok) { $('language').replaceChildren(); languages.languages.forEach(language => { const option = document.createElement('option'); option.value = language.code; option.textContent = language.display_label; option.disabled = language.code !== 'en' && language.state === 'planned'; $('language').append(option); }); $('languageCount').textContent = `${languages.language_registry_size} targets`; }
        $('health').textContent = health.status === 'ok' ? 'Ready' : 'Check status';
      } catch (_) { $('health').textContent = 'API unavailable'; setStatus('The console could not reach the local API. Start `nastech-tts serve` and refresh.', 'error'); }
    }
    document.querySelectorAll('.theme').forEach(button => button.addEventListener('click', () => { document.body.dataset.theme = button.dataset.themeChoice; localStorage.setItem('nastech-theme', button.dataset.themeChoice); themes.forEach(item => item.classList.toggle('active', item === button)); }));
    const savedTheme = localStorage.getItem('nastech-theme'); if (savedTheme) { const button = document.querySelector(`[data-theme-choice="${savedTheme}"]`); if (button) button.click(); }
    $('synthesize').addEventListener('click', synthesize); $('makeStory').addEventListener('click', story); $('clearAudio').addEventListener('click', () => { $('audio').pause(); $('audio').removeAttribute('src'); $('audio').load(); $('download').style.display = 'none'; if (audioUrl) URL.revokeObjectURL(audioUrl); audioUrl = null; setStatus('Audio cleared.'); });
    loadConsole();
  </script>
</body>
</html>"""


def render_console() -> str:
    """Return the static local console document without external assets."""

    return CONSOLE_HTML
