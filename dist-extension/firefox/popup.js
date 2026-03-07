// Content DNA OS - Extension Popup Logic

const DEFAULT_API = 'https://7i8jr6osv7.execute-api.us-east-1.amazonaws.com/prod/api';

// ─── Storage helpers ───
async function getApiUrl() {
  return new Promise((resolve) => {
    const storage = typeof browser !== 'undefined' ? browser.storage : chrome.storage;
    storage.local.get(['apiUrl'], (result) => {
      resolve(result.apiUrl || DEFAULT_API);
    });
  });
}

async function setApiUrl(url) {
  return new Promise((resolve) => {
    const storage = typeof browser !== 'undefined' ? browser.storage : chrome.storage;
    storage.local.set({ apiUrl: url }, resolve);
  });
}

// ─── API Client ───
async function apiCall(endpoint, options = {}) {
  const baseUrl = await getApiUrl();
  const url = `${baseUrl}${endpoint}`;

  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!res.ok) {
    let detail = `API error: ${res.status}`;
    try {
      const err = await res.json();
      if (err.detail) detail = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
    } catch {}
    throw new Error(detail);
  }
  return res.json();
}

// ─── Tab Navigation ───
document.querySelectorAll('.tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach((t) => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach((c) => c.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');
  });
});

// ─── Evolve ───
document.getElementById('btn-evolve').addEventListener('click', async () => {
  const content = document.getElementById('evolve-content').value.trim();
  if (!content) return;

  const btn = document.getElementById('btn-evolve');
  const resultEl = document.getElementById('evolve-result');

  btn.classList.add('loading');
  btn.disabled = true;
  resultEl.classList.add('hidden');

  try {
    const body = {
      content,
      platform: document.getElementById('evolve-platform').value,
      language: document.getElementById('evolve-language').value,
    };
    const strategy = document.getElementById('evolve-strategy').value;
    if (strategy) body.strategy = strategy;

    const data = await apiCall('/evolve', {
      method: 'POST',
      body: JSON.stringify(body),
    });

    resultEl.innerHTML = renderEvolution(data);
    resultEl.classList.remove('hidden');
  } catch (err) {
    resultEl.innerHTML = `<div class="status error">${escapeHtml(err.message)}</div>`;
    resultEl.classList.remove('hidden');
  } finally {
    btn.classList.remove('loading');
    btn.disabled = false;
  }
});

// ─── Lab ───
document.getElementById('btn-lab').addEventListener('click', async () => {
  const content = document.getElementById('lab-content').value.trim();
  if (!content) return;

  const btn = document.getElementById('btn-lab');
  const resultEl = document.getElementById('lab-result');

  btn.classList.add('loading');
  btn.disabled = true;
  resultEl.classList.add('hidden');

  try {
    const data = await apiCall('/evolve/lab', {
      method: 'POST',
      body: JSON.stringify({
        content,
        platform: document.getElementById('lab-platform').value,
        generations: parseInt(document.getElementById('lab-generations').value, 10),
      }),
    });

    resultEl.innerHTML = renderLabResult(data);
    resultEl.classList.remove('hidden');
  } catch (err) {
    resultEl.innerHTML = `<div class="status error">${escapeHtml(err.message)}</div>`;
    resultEl.classList.remove('hidden');
  } finally {
    btn.classList.remove('loading');
    btn.disabled = false;
  }
});

// ─── DNA Extract ───
document.getElementById('btn-dna').addEventListener('click', async () => {
  const content = document.getElementById('dna-content').value.trim();
  if (!content) return;

  const btn = document.getElementById('btn-dna');
  const resultEl = document.getElementById('dna-result');

  btn.classList.add('loading');
  btn.disabled = true;
  resultEl.classList.add('hidden');

  try {
    const data = await apiCall('/dna/extract', {
      method: 'POST',
      body: JSON.stringify({ content }),
    });

    resultEl.innerHTML = renderDNA(data);
    resultEl.classList.remove('hidden');
  } catch (err) {
    resultEl.innerHTML = `<div class="status error">${escapeHtml(err.message)}</div>`;
    resultEl.classList.remove('hidden');
  } finally {
    btn.classList.remove('loading');
    btn.disabled = false;
  }
});

// ─── Extract Page Content ───
document.getElementById('btn-extract-page').addEventListener('click', async () => {
  const runtime = typeof browser !== 'undefined' ? browser.runtime : chrome.runtime;
  const tabs = typeof browser !== 'undefined' ? browser.tabs : chrome.tabs;

  tabs.query({ active: true, currentWindow: true }, (activeTabs) => {
    if (!activeTabs[0]) return;

    tabs.sendMessage(activeTabs[0].id, { action: 'extractContent' }, (response) => {
      if (response && response.content) {
        // Determine which tab is active and fill the textarea
        const activeTab = document.querySelector('.tab.active').dataset.tab;
        const textareaId = activeTab === 'lab' ? 'lab-content'
          : activeTab === 'dna' ? 'dna-content'
          : 'evolve-content';
        document.getElementById(textareaId).value = response.content;
      }
    });
  });
});

// ─── Settings ───
document.getElementById('btn-save-settings').addEventListener('click', async () => {
  const url = document.getElementById('settings-api-url').value.trim();
  const statusEl = document.getElementById('settings-status');

  if (!url) {
    statusEl.className = 'status error';
    statusEl.textContent = 'Please enter a valid URL';
    statusEl.classList.remove('hidden');
    return;
  }

  try {
    // Validate the URL by trying to reach health endpoint
    const res = await fetch(`${url.replace(/\/api\/?$/, '')}/health`);
    if (!res.ok) throw new Error('Cannot reach server');
  } catch {
    // Save anyway but warn
    statusEl.className = 'status error';
    statusEl.textContent = 'Saved, but server appears unreachable. Check the URL.';
  }

  await setApiUrl(url);
  statusEl.className = 'status success';
  statusEl.textContent = 'Settings saved!';
  statusEl.classList.remove('hidden');
  setTimeout(() => statusEl.classList.add('hidden'), 3000);
});

// Load saved settings
(async () => {
  const url = await getApiUrl();
  document.getElementById('settings-api-url').value = url === DEFAULT_API ? '' : url;
  const linkWebapp = document.getElementById('link-webapp');
  if (linkWebapp) {
    const webappUrl = url.replace(/\/api\/?$/, '');
    linkWebapp.href = webappUrl;
  }
})();

// ─── Renderers ───

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function renderEvolution(data) {
  const mutation = data.mutation || data;
  const fitness = mutation.fitness_score || mutation.fitness || {};
  const overallFitness = typeof fitness === 'number' ? fitness : (fitness.overall || fitness.composite || 0);
  const fitnessPercent = Math.round(overallFitness * 100);
  const fitnessClass = fitnessPercent >= 70 ? 'high' : fitnessPercent >= 40 ? 'medium' : 'low';

  return `
    <h4>Evolution Result</h4>
    <div class="result-content">${escapeHtml(mutation.content || mutation.evolved_content || '')}</div>
    <div class="result-meta">
      <span class="meta-tag strategy">${escapeHtml(mutation.strategy || 'auto')}</span>
      <span class="meta-tag fitness">Fitness: ${fitnessPercent}%</span>
    </div>
    <div class="action-row">
      <button class="btn-icon" onclick="copyText(this)" data-text="${escapeHtml(mutation.content || mutation.evolved_content || '')}">📋 Copy</button>
    </div>
  `;
}

function renderLabResult(data) {
  const generations = data.generations || data.evolution_tree || [];
  if (!generations.length) return '<div class="status error">No generations returned</div>';

  let html = '<h4>Evolution Lab Results</h4>';
  generations.forEach((gen, i) => {
    const mutations = gen.mutations || gen.variants || [gen];
    mutations.forEach((m) => {
      const fitness = m.fitness_score || m.fitness || {};
      const overall = typeof fitness === 'number' ? fitness : (fitness.overall || fitness.composite || 0);
      const pct = Math.round(overall * 100);
      const cls = pct >= 70 ? 'high' : pct >= 40 ? 'medium' : 'low';

      html += `
        <div class="gen-card">
          <div class="gen-header">
            <span class="gen-label">Gen ${gen.generation || i + 1}</span>
            <span class="meta-tag strategy">${escapeHtml(m.strategy || '')}</span>
          </div>
          <div class="result-content">${escapeHtml(m.content || m.evolved_content || '')}</div>
          <div class="fitness-bar-container">
            <div class="fitness-bar"><div class="fitness-bar-fill ${cls}" style="width:${pct}%"></div></div>
          </div>
          <div class="action-row">
            <button class="btn-icon" onclick="copyText(this)" data-text="${escapeHtml(m.content || m.evolved_content || '')}">📋 Copy</button>
          </div>
        </div>
      `;
    });
  });

  return html;
}

function renderDNA(data) {
  const dna = data.dna || data;
  let html = '<h4>DNA Profile</h4>';

  if (dna.intent) html += `<div class="dna-section"><div class="dna-label">Intent</div><div class="dna-value">${escapeHtml(dna.intent)}</div></div>`;
  if (dna.tone) html += `<div class="dna-section"><div class="dna-label">Tone</div><div class="dna-value">${escapeHtml(dna.tone)}</div></div>`;
  if (dna.emotion) html += `<div class="dna-section"><div class="dna-label">Emotion</div><div class="dna-value">${escapeHtml(dna.emotion)}</div></div>`;
  if (dna.structure) html += `<div class="dna-section"><div class="dna-label">Structure</div><div class="dna-value">${escapeHtml(dna.structure)}</div></div>`;

  if (dna.keywords && dna.keywords.length) {
    html += `<div class="dna-section"><div class="dna-label">Keywords</div><div class="dna-keywords">`;
    dna.keywords.forEach((kw) => {
      html += `<span class="keyword">${escapeHtml(kw)}</span>`;
    });
    html += '</div></div>';
  }

  return html;
}

// ─── Global: Copy text ───
window.copyText = function (btn) {
  const text = btn.dataset.text;
  navigator.clipboard.writeText(text).then(() => {
    const original = btn.innerHTML;
    btn.innerHTML = '✅ Copied';
    setTimeout(() => { btn.innerHTML = original; }, 1500);
  });
};
