const modal = document.createElement("div");
modal.id = "models-modal";
modal.className = "models-modal";
modal.setAttribute("role", "dialog");
modal.setAttribute("aria-modal", "true");
modal.setAttribute("aria-label", "Models list");
modal.innerHTML = `
  <div class="models-modal-overlay"></div>
  <div class="models-modal-content">
    <div class="models-modal-header">
      <h3 class="models-modal-title">All Models</h3>
      <button class="models-modal-close" aria-label="Close">&times;</button>
    </div>
    <p class="models-modal-note">Click any model to copy its ID. Sorting may not be exact. Pricing, context window, and other metadata show only official provider data.</p>
    <input type="text" class="models-modal-search" placeholder="Search models…" autocomplete="off" spellcheck="false">
    <div class="models-modal-filters"></div>
    <div class="models-modal-grid" aria-live="polite" aria-relevant="additions removals"></div>
  </div>
`;
document.body.appendChild(modal);

const overlay = modal.querySelector(".models-modal-overlay");
const closeBtn = modal.querySelector(".models-modal-close");
const grid = modal.querySelector(".models-modal-grid");
const title = modal.querySelector(".models-modal-title");
const filtersContainer = modal.querySelector(".models-modal-filters");
const searchInput = modal.querySelector(".models-modal-search");

const CAPABILITY_ICONS = {
  "reasoning": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#ce93d8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v.5"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v.5"/><path d="M8 8a4 4 0 0 1 8 0c0 1.5-.5 2.8-1.3 3.8A2 2 0 0 1 14 14a2 2 0 0 1-4 0 2 2 0 0 1-.7-2.2C8.5 10.8 8 9.5 8 8"/><path d="M9 14.5a3.5 3.5 0 1 0 6 0"/></svg>',
  "tool_call": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#ffb74d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
  "attachment": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#64b5f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>',
  "temperature": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#ef9a9a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>',
  "open_weights": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#81c784" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/><path d="M21 16v2a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-2"/></svg>',
};

const CAPABILITY_LABELS = {
  "reasoning": "Supports reasoning",
  "tool_call": "Supports tool calling",
  "attachment": "Supports file attachments",
  "temperature": "Supports temperature control",
  "open_weights": "Open weights model",
};

let modelsData = {};
let currentProvider = null;
let currentFamily = "all";
let sortedModelsCache = {};
let searchQuery = "";

const FAMILY_LABELS = {
  "claude": "Claude",
  "claude-opus": "Claude Opus",
  "claude-sonnet": "Claude Sonnet",
  "claude-haiku": "Claude Haiku",
  "opus": "Claude",
  "sonnet": "Claude",
  "haiku": "Claude",
  "gpt": "GPT",
  "gpt-mini": "GPT Mini",
  "gpt-codex": "GPT Codex",
  "gemini": "Gemini",
  "gemini-pro": "Gemini Pro",
  "gemini-flash": "Gemini Flash",
  "deepseek": "DeepSeek",
  "deepseek-chat": "DeepSeek Chat",
  "deepseek-reasoner": "DeepSeek Reasoner",
  "deepseek-coder": "DeepSeek Coder",
  "glm": "GLM",
  "kimi": "Kimi",
  "qwen": "Qwen",
  "qwen-coder": "Qwen Coder",
  "qwen-vl": "Qwen VL",
  "qwen3": "Qwen",
  "minimax": "MiniMax",
  "grok": "Grok",
  "llama": "Llama",
  "mistral": "Mistral",
  "mistral-large": "Mistral Large",
  "codestral": "Mistral",
  "devstral": "Mistral",
  "command": "Command",
  "jamba": "Jamba",
  "mixtral": "Mistral",
  "phi": "Phi",
  "yi": "Yi",
  "dolphin": "Dolphin",
  "hermes": "Hermes",
  "gpt-oss-120b": "GPT-OSS",
  "gpt-oss-20b": "GPT-OSS",
  "gpt-oss": "GPT-OSS",
  "instruct": "Instruct",
  "falcon": "Falcon",
  "granite": "Granite",
  "nemotron": "Nemotron",
  "sabiya": "Sabiya",
  "aya": "Aya",
  "olmo": "OLMo",
  "smol": "Smol",
  "mamba": "Mamba",
  "bloom": "Bloom",
  "stablelm": "StableLM",
  "pythia": "Pythia",
  "redpajama": "RedPajama",
  "mpt": "MPT",
  "dolly": "Dolly",
  "openchat": "OpenChat",
  "vicuna": "Vicuna",
  "alpaca": "Alpaca",
  "wizardlm": "WizardLM",
  "openbuddy": "OpenBuddy",
  "tulu": "Tulu",
  "koala": "Koala",
  "orca": "Orca",
  "starcoder": "StarCoder",
  "codegemma": "CodeGemma",
  "codellama": "CodeLlama",
  "stable-code": "Stable Code",
  "other": "Other",
};

let hideOutdated = false;
const OUTDATED_MONTHS = 6;
let showOnlyFree = false;

const canonical = document.querySelector('link[rel="canonical"]');
let jsonUrl;
if (canonical) {
  const c = canonical.href;
  jsonUrl = c.replace(/\/([^/]+\/?)?$/, '/models_data.json');
} else {
  jsonUrl = `${window.location.origin}/models_data.json`;
}

const fallbackUrls = [
  jsonUrl,
  new URL('../models_data.json', window.location.href).href
];

function tryFetch(urls, idx) {
  if (idx >= urls.length) return;
  fetch(urls[idx])
    .then((res) => {
      if (!res.ok) throw new Error("Failed");
      return res.json();
    })
    .then((data) => {
      modelsData = data;
    })
    .catch(() => {
      tryFetch(urls, idx + 1);
    });
}

tryFetch(fallbackUrls, 0);

let toastTimer = null;

function showToast(text) {
  const old = document.querySelector(".models-toast");
  if (old) old.remove();
  if (toastTimer) clearTimeout(toastTimer);

  const toast = document.createElement("div");
  toast.className = "models-toast";
  toast.textContent = text;
  document.body.appendChild(toast);

  toastTimer = setTimeout(() => {
    toast.remove();
    toastTimer = null;
  }, 1500);
}

function copyText(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast(`Copied: ${text}`);
  });
}

function getFamilyLabel(keyword) {
  return FAMILY_LABELS[keyword] || keyword.charAt(0).toUpperCase() + keyword.slice(1);
}

function _getModelMeta(modelId) {
  if (modelsData._models?.[modelId]) return modelsData._models[modelId];
  const providerData = modelsData[currentProvider];
  if (!providerData?.families) return null;
  for (const fam in providerData.families) {
    const meta = providerData.families[fam].metadata;
    if (meta?.[modelId]) return meta[modelId];
  }
  return null;
}

function _getModelFamily(modelId) {
  const providerData = modelsData[currentProvider];
  if (!providerData?.families) return null;
  for (const fam in providerData.families) {
    const famData = providerData.families[fam];
    const models = famData.models || famData;
    if (Array.isArray(models) && models.includes(modelId)) return fam;
    if (famData.metadata?.[modelId]) return fam;
  }
  return null;
}

function _isOutdated(meta) {
  if (!meta?.release_date) return true;
  const rd = meta.release_date;
  const release = new Date(rd);
  if (Number.isNaN(release.getTime())) return true;
  const now = new Date();
  const diffMonths = (now.getFullYear() - release.getFullYear()) * 12 + (now.getMonth() - release.getMonth());
  return diffMonths > OUTDATED_MONTHS;
}

function _sortByReleaseDate(a, b) {
  const ma = _getModelMeta(a);
  const mb = _getModelMeta(b);
  const ra = ma?.release_date ? new Date(ma.release_date) : new Date(0);
  const rb = mb?.release_date ? new Date(mb.release_date) : new Date(0);
  return rb - ra;
}

function _formatCost(meta) {
  if (!meta?.cost) return "";
  const c = meta.cost;
  const parts = [];
  if (c.input != null) parts.push(`in $${c.input}`);
  if (c.output != null) parts.push(`out $${c.output}`);
  return parts.length ? parts.join(" / ") : "";
}

function _formatLimit(meta) {
  if (!meta?.limit || meta.limit.context == null) return "";
  const ctx = meta.limit.context;
  if (ctx >= 1000000) return `${(ctx / 1000000).toFixed(1)}M ctx`;
  if (ctx >= 1000) return `${(ctx / 1000).toFixed(0)}K ctx`;
  return `${ctx} ctx`;
}

function _formatDate(meta) {
  if (!meta?.release_date) return "";
  return meta.release_date;
}

function _extractVersionScore(modelId) {
  const patterns = [
    /(?:^|[-\s])(\d+)\.(\d+)/,
    /(?:^|[-\s])v(\d+)/,
    /(?:^|[-\s])(\d{4})/,
  ];
  for (let i = 0; i < patterns.length; i++) {
    const m = modelId.match(patterns[i]);
    if (m) {
      if (m[2] !== undefined) {
        return parseInt(m[1], 10) * 1000 + parseInt(m[2], 10) * 10;
      }
      return parseInt(m[1], 10) * 1000;
    }
  }
  return 0;
}

function _familyMaxReleaseDate(familyData) {
  const models = familyData.models || familyData;
  let maxDate = 0;
  models.forEach((mid) => {
    const meta = _getModelMeta(mid);
    if (meta?.release_date) {
      const d = new Date(meta.release_date).getTime();
      if (d > maxDate) maxDate = d;
    }
  });
  return maxDate;
}

function _familyMaxVersion(familyData) {
  const models = familyData.models || familyData;
  let maxVer = 0;
  models.forEach((mid) => {
    const ver = _extractVersionScore(mid);
    if (ver > maxVer) maxVer = ver;
  });
  return maxVer;
}

const EXCLUDED_FAMILIES = ["instruct", "mini", "embed", "image"];

function buildFilters(families, allModelsCount) {
  filtersContainer.innerHTML = "";

  if (!families || Object.keys(families).length === 0) {
    filtersContainer.style.display = "none";
    return;
  }

  filtersContainer.style.display = "";

  const allBtn = document.createElement("button");
  allBtn.className = `models-filter-btn${currentFamily === "all" ? " models-filter-btn--active" : ""}`;
  allBtn.setAttribute("data-family", "all");
  allBtn.textContent = `All (${allModelsCount})`;
  allBtn.title = "Show all models";
  filtersContainer.appendChild(allBtn);

  let entries = Object.entries(families);

  entries = entries.filter((e) => EXCLUDED_FAMILIES.indexOf(e[0]) === -1);

  entries.sort((a, b) => {
    const aIsOther = a[0] === "other";
    const bIsOther = b[0] === "other";
    if (aIsOther && !bIsOther) return 1;
    if (!aIsOther && bIsOther) return -1;

    const aMaxDate = _familyMaxReleaseDate(a[1]);
    const bMaxDate = _familyMaxReleaseDate(b[1]);
    if (bMaxDate !== aMaxDate) return bMaxDate - aMaxDate;

    const aMaxVer = _familyMaxVersion(a[1]);
    const bMaxVer = _familyMaxVersion(b[1]);
    if (bMaxVer !== aMaxVer) return bMaxVer - aMaxVer;

    return a[0].localeCompare(b[0]);
  });

  entries.forEach((entry) => {
    const keyword = entry[0];
    const count = entry[1].models ? entry[1].models.length : entry[1].length;
    const label = getFamilyLabel(keyword);
    const btn = document.createElement("button");
    btn.className = `models-filter-btn${currentFamily === keyword ? " models-filter-btn--active" : ""}`;
    btn.setAttribute("data-family", keyword);
    btn.textContent = `${label} (${count})`;
    btn.title = `Show only ${label}`;
    filtersContainer.appendChild(btn);
  });

  const togglesWrap = document.createElement("div");
  togglesWrap.className = "models-modal-toggles";

  const toggleWrap = document.createElement("label");
  toggleWrap.className = "models-toggle-wrap";
  const toggleCb = document.createElement("input");
  toggleCb.type = "checkbox";
  toggleCb.checked = hideOutdated;
  toggleCb.title = "Hide models older than 6 months";
  toggleCb.addEventListener("change", () => {
    hideOutdated = toggleCb.checked;
    const providerData = modelsData[currentProvider];
    if (!providerData) return;
    let modelsToRender;
    if (currentFamily === "all") {
      modelsToRender = providerData.all;
    } else {
      const fam = providerData.families ? providerData.families[currentFamily] : null;
      modelsToRender = fam ? fam.models : [];
    }
    renderModels(modelsToRender);
  });
  toggleWrap.appendChild(toggleCb);
  toggleWrap.appendChild(document.createTextNode("Hide outdated"));
  togglesWrap.appendChild(toggleWrap);

  const freeWrap = document.createElement("label");
  freeWrap.className = "models-toggle-wrap";
  const freeCb = document.createElement("input");
  freeCb.type = "checkbox";
  freeCb.checked = showOnlyFree;
  freeCb.title = "Show only models with 'free' in the name";
  freeCb.addEventListener("change", () => {
    showOnlyFree = freeCb.checked;
    const providerData = modelsData[currentProvider];
    if (!providerData) return;
    let modelsToRender;
    if (currentFamily === "all") {
      modelsToRender = providerData.all;
    } else {
      const fam = providerData.families ? providerData.families[currentFamily] : null;
      modelsToRender = fam ? fam.models : [];
    }
    renderModels(modelsToRender);
  });
  freeWrap.appendChild(freeCb);
  freeWrap.appendChild(document.createTextNode("Free only"));
  togglesWrap.appendChild(freeWrap);

  filtersContainer.appendChild(togglesWrap);
}

function getSortedModels(models) {
  const cacheKey = models.join(",");
  if (sortedModelsCache[cacheKey]) {
    return sortedModelsCache[cacheKey];
  }
  const sorted = models.slice().sort(_sortByReleaseDate);
  sortedModelsCache[cacheKey] = sorted;
  return sorted;
}

function renderModels(models) {
  grid.classList.add("models-modal-grid-loading");
  grid.innerHTML = "";

  if (!models || models.length === 0) {
    grid.innerHTML = '<p class="models-modal-empty">No models in this category</p>';
    grid.classList.remove("models-modal-grid-loading");
    return;
  }

  const sorted = getSortedModels(models);

  if (!searchQuery) {
    renderModelItems(sorted);
    grid.classList.remove("models-modal-grid-loading");
    return;
  }

  const providerData = modelsData[currentProvider];
  if (!providerData) {
    renderModelItems(sorted);
    grid.classList.remove("models-modal-grid-loading");
    return;
  }
  const allProviderModels = providerData.all || (Array.isArray(providerData) ? providerData : []);

  const normalizedQuery = searchQuery.toLowerCase().replace(/[^a-z0-9]/g, "");
  if (!normalizedQuery) {
    renderModelItems(sorted);
    grid.classList.remove("models-modal-grid-loading");
    return;
  }

  let results = [];
  const exactMatches = [];
  allProviderModels.forEach((id) => {
    const normalizedId = id.toLowerCase().replace(/[^a-z0-9]/g, "");
    if (normalizedId.includes(normalizedQuery)) {
      exactMatches.push({ id, score: 0, index: normalizedId.indexOf(normalizedQuery) });
    }
  });

  if (exactMatches.length > 0) {
    exactMatches.sort((a, b) => a.index - b.index);
    results = exactMatches.map((m) => m.id);
  } else {
    const fuzzyMatches = [];
    allProviderModels.forEach((id) => {
      const score = fuzzyMatch(normalizedQuery, id.toLowerCase().replace(/[^a-z0-9]/g, ""));
      if (score > 0) {
        fuzzyMatches.push({ id, score });
      }
    });
    fuzzyMatches.sort((a, b) => b.score - a.score);
    results = fuzzyMatches.map((m) => m.id);
  }

  if (results.length === 0) {
    grid.innerHTML = `<p class="models-modal-empty">No models match "${searchQuery}"</p>`;
    grid.classList.remove("models-modal-grid-loading");
    return;
  }

  renderModelItems(results);
  grid.classList.remove("models-modal-grid-loading");
}

function fuzzyMatch(query, str) {
  if (!query || !str) return 0;
  if (query.length > str.length) return 0;

  let qi = 0;
  let lastMatchIdx = -1;
  let totalGap = 0;
  let consecutiveBonus = 0;
  let prevMatched = false;

  for (let si = 0; si < str.length && qi < query.length; si++) {
    if (str[si] === query[qi]) {
      if (lastMatchIdx >= 0) {
        totalGap += si - lastMatchIdx;
      }
      if (prevMatched) {
        consecutiveBonus++;
      }
      lastMatchIdx = si;
      qi++;
      prevMatched = true;
    } else {
      prevMatched = false;
    }
  }

  if (qi < query.length) return 0;

  return Math.max(1, 100 - totalGap + consecutiveBonus * 5);
}

function renderModelItems(ids) {
  grid.innerHTML = "";

  ids.forEach((id) => {
    const meta = _getModelMeta(id);
    if (hideOutdated && _isOutdated(meta)) return;
    if (showOnlyFree && !id.toLowerCase().includes("free")) return;

    const item = document.createElement("div");
    item.className = "models-modal-item";

    const familyKey = _getModelFamily(id);
    if (familyKey) {
      const familyLabel = document.createElement("div");
      familyLabel.className = "models-family-label";
      familyLabel.textContent = getFamilyLabel(familyKey);
      item.appendChild(familyLabel);
    }

    const code = document.createElement("code");
    code.textContent = id;
    code.title = "Click to copy";
    code.addEventListener("click", (e) => {
      e.stopPropagation();
      copyText(id);
    });
    item.appendChild(code);

    const caps = document.createElement("div");
    caps.className = "models-capabilities";
    for (const key of ["reasoning", "tool_call", "attachment", "temperature", "open_weights"]) {
      if (meta?.[key]) {
        const span = document.createElement("span");
        span.className = "models-capability-icon";
        span.setAttribute("data-tooltip", CAPABILITY_LABELS[key]);
        span.title = CAPABILITY_LABELS[key];
        span.innerHTML = CAPABILITY_ICONS[key];
        caps.appendChild(span);
      }
    }
    if (caps.children.length) item.appendChild(caps);

    const metaRow = document.createElement("div");
    metaRow.className = "models-modal-meta";
    const costStr = _formatCost(meta);
    const limitStr = _formatLimit(meta);
    const dateStr = _formatDate(meta);
    const parts = [];
    if (costStr) parts.push(`<span class="models-meta-cost">${costStr}</span>`);
    if (limitStr) parts.push(`<span class="models-meta-limit">${limitStr}</span>`);
    if (dateStr) parts.push(`<span class="models-meta-date">${dateStr}</span>`);
    if (parts.length) {
      metaRow.innerHTML = parts.join(' <span class="models-meta-sep">·</span> ');
      item.appendChild(metaRow);
    }

    grid.appendChild(item);
  });
}

function openModal(providerName) {
  currentProvider = providerName;
  currentFamily = "all";
  hideOutdated = false;
  showOnlyFree = false;
  sortedModelsCache = {};
  searchQuery = "";
  searchInput.value = "";

  const providerData = modelsData[providerName];
  const isNewFormat = providerData && typeof providerData === "object" && providerData.all && providerData.families;

  let allModels;
  let families = null;

  if (isNewFormat) {
    allModels = providerData.all;
    families = providerData.families;
  } else if (Array.isArray(providerData)) {
    allModels = providerData;
  } else {
    allModels = [];
  }

  title.textContent = `${providerName} \u2014 All Models (${allModels.length})`;

  grid.innerHTML = '<p class="models-modal-empty">Loading models…</p>';

  buildFilters(families, allModels ? allModels.length : 0);
  filterBtnIndex = 0;
  renderModels(allModels);

  modal.classList.add("models-modal--open");
  document.body.style.overflow = "hidden";

  if (searchInput !== document.activeElement) {
    setTimeout(() => searchInput.focus(), 100);
  }
}

function closeModal() {
  if (modal.classList.contains("models-modal--closing")) return;
  modal.classList.add("models-modal--closing");
  setTimeout(() => {
    modal.classList.remove("models-modal--open", "models-modal--closing");
    document.body.style.overflow = "";
    currentProvider = null;
    currentFamily = "all";
    hideOutdated = false;
    showOnlyFree = false;
    searchQuery = "";
    searchInput.value = "";
  }, 200);
}

let filterBtnIndex = 0;

filtersContainer.addEventListener("click", (e) => {
  const btn = e.target.closest(".models-filter-btn");
  if (!btn || !currentProvider) return;

  const family = btn.getAttribute("data-family");
  if (!family || family === currentFamily) return;

  currentFamily = family;

  const btns = filtersContainer.querySelectorAll(".models-filter-btn");
  btns.forEach((b, i) => {
    b.classList.toggle("models-filter-btn--active", b.getAttribute("data-family") === family);
    if (b.getAttribute("data-family") === family) filterBtnIndex = i;
  });

  const providerData = modelsData[currentProvider];
  const isNewFormat = providerData && typeof providerData === "object" && providerData.all && providerData.families;

  let modelsToRender;
  if (isNewFormat) {
    if (family === "all") {
      modelsToRender = providerData.all;
    } else {
      const fam = providerData.families[family];
      modelsToRender = fam ? fam.models : [];
    }
  } else if (Array.isArray(providerData)) {
    modelsToRender = providerData;
  } else {
    modelsToRender = [];
  }

  renderModels(modelsToRender);
});

filtersContainer.addEventListener("keydown", (e) => {
  const btns = filtersContainer.querySelectorAll(".models-filter-btn");
  if (btns.length === 0) return;

  if (e.key === "ArrowRight" || e.key === "ArrowDown") {
    e.preventDefault();
    filterBtnIndex = (filterBtnIndex + 1) % btns.length;
    btns[filterBtnIndex].focus();
  } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
    e.preventDefault();
    filterBtnIndex = (filterBtnIndex - 1 + btns.length) % btns.length;
    btns[filterBtnIndex].focus();
  } else if (e.key === "Home") {
    e.preventDefault();
    filterBtnIndex = 0;
    btns[filterBtnIndex].focus();
  } else if (e.key === "End") {
    e.preventDefault();
    filterBtnIndex = btns.length - 1;
    btns[filterBtnIndex].focus();
  }
});

document.addEventListener("click", (e) => {
  const trigger = e.target.closest(".models-show-all");
  if (trigger) {
    e.preventDefault();
    e.stopPropagation();
    const provider = trigger.getAttribute("data-provider");
    if (provider) {
      openModal(provider);
    }
  }
});

closeBtn.addEventListener("click", closeModal);
overlay.addEventListener("click", closeModal);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && modal.classList.contains("models-modal--open")) {
    closeModal();
  }
});

searchInput.addEventListener("input", (e) => {
  searchQuery = e.target.value.trim();
  const providerData = modelsData[currentProvider];
  if (!providerData) return;
  let modelsToRender;
  if (currentFamily === "all") {
    modelsToRender = providerData.all || (Array.isArray(providerData) ? providerData : []);
  } else {
    const fam = providerData.families ? providerData.families[currentFamily] : null;
    modelsToRender = fam ? fam.models : [];
  }
  renderModels(modelsToRender);
});
