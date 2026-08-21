(() => {
  const root = document.documentElement;
  const themeButton = document.querySelector('#theme-toggle');
  const storedTheme = localStorage.getItem('nastech-pages-theme');
  if (storedTheme === 'night') root.dataset.theme = 'night';
  themeButton?.addEventListener('click', () => {
    const next = root.dataset.theme === 'night' ? 'day' : 'night';
    if (next === 'day') delete root.dataset.theme;
    else root.dataset.theme = 'night';
    localStorage.setItem('nastech-pages-theme', next);
  });

  const stopAudio = () => document.querySelectorAll('audio').forEach((audio) => {
    audio.pause(); audio.currentTime = 0;
  });
  document.querySelector('#stop-audio')?.addEventListener('click', stopAudio);

  const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[char]));

  const voiceGrid = document.querySelector('#voice-grid');
  const voiceCount = document.querySelector('#voice-count');
  const voiceSearch = document.querySelector('#voice-search');
  const voiceKind = document.querySelector('#voice-kind');
  let voices = [];

  const renderVoices = () => {
    const query = (voiceSearch?.value || '').trim().toLowerCase();
    const kind = voiceKind?.value || 'all';
    const visible = voices.filter((voice) => {
      const searchable = [voice.profile_id, voice.label, voice.base_voice, voice.kind, voice.description]
        .join(' ').toLowerCase();
      return (!query || searchable.includes(query)) && (kind === 'all' || voice.kind === kind);
    });
    if (voiceCount) voiceCount.textContent = `${visible.length} of ${voices.length} previews`;
    if (!voiceGrid) return;
    voiceGrid.innerHTML = visible.length ? visible.map((voice) => `
      <article class="voice-card">
        <div><span class="tag">${escapeHtml(voice.base_voice)}</span><span class="tag">${escapeHtml(voice.kind === 'named-base-profile' ? 'Named' : 'Delivery')}</span></div>
        <h3>${escapeHtml(voice.label)}</h3>
        <p class="voice-meta">${escapeHtml(voice.profile_id)} · ${escapeHtml(voice.description)}</p>
        <audio controls preload="none" src="${encodeURI(voice.preview)}" aria-label="Play ${escapeHtml(voice.label)} preview"></audio>
        <p class="voice-meta">Verified local preview · ${voice.quality.sample_rate_hz} Hz · ${voice.quality.duration_seconds.toFixed(1)} s</p>
      </article>`).join('') : '<p class="callout">No voice profile matches that filter.</p>';
    voiceGrid.querySelectorAll('audio').forEach((audio) => audio.addEventListener('play', (event) => {
      document.querySelectorAll('audio').forEach((other) => { if (other !== event.currentTarget) other.pause(); });
    }));
  };

  [voiceSearch, voiceKind].forEach((element) => element?.addEventListener('input', renderVoices));
  fetch('assets/voice-previews.json').then((response) => {
    if (!response.ok) throw new Error('Preview catalogue unavailable.');
    return response.json();
  }).then((catalog) => { voices = catalog.voices || []; renderVoices(); })
    .catch((error) => { if (voiceGrid) voiceGrid.innerHTML = `<p class="callout">${escapeHtml(error.message)}</p>`; });

  const languageTable = document.querySelector('#language-table');
  const languageSummary = document.querySelector('#language-summary');
  const languageSearch = document.querySelector('#language-search');
  const showPlanned = document.querySelector('#show-planned');
  let languages = [];

  const renderLanguages = () => {
    const query = (languageSearch?.value || '').trim().toLowerCase();
    const showAll = Boolean(showPlanned?.checked);
    const visible = languages.filter((language) => {
      const searchable = [language.code, language.label, language.display_label, language.region].join(' ').toLowerCase();
      return (showAll || language.state !== 'planned') && (!query || searchable.includes(query));
    });
    if (!languageTable) return;
    languageTable.innerHTML = visible.map((language) => {
      const available = language.state === 'adapter-available';
      const use = available
        ? `<code>nastech-tts download-language-pack ${escapeHtml(language.code)}</code>`
        : 'Visible for planning; no local pack substitution.';
      return `<tr><td><strong>${escapeHtml(language.display_label || `${language.code} - ${language.label}`)}</strong><br><small>${escapeHtml(language.iso639_3 || '')}</small></td><td>${escapeHtml(language.region || 'Regional')}</td><td><span class="state ${available ? 'available' : 'planned'}">${escapeHtml(language.state)}</span></td><td>${use}</td></tr>`;
    }).join('') || '<tr><td colspan="4">No language target matches that filter.</td></tr>';
  };

  [languageSearch, showPlanned].forEach((element) => element?.addEventListener('input', renderLanguages));
  fetch('assets/languages.json').then((response) => {
    if (!response.ok) throw new Error('Language registry unavailable.');
    return response.json();
  }).then((catalog) => {
    languages = catalog.languages || catalog;
    const packs = languages.filter((language) => language.state === 'adapter-available').length;
    if (languageSummary) languageSummary.textContent = `${languages.length} targets · ${packs} auditable on-demand local routes · code-first labels`;
    renderLanguages();
  }).catch((error) => { if (languageSummary) languageSummary.textContent = error.message; });
})();
