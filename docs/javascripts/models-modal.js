const CAPABILITY_ICONS = {
  "reasoning": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#ce93d8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v.5"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v.5"/><path d="M8 8a4 4 0 0 1 8 0c0 1.5-.5 2.8-1.3 3.8A2 2 0 0 1 14 14a2 2 0 0 1-4 0 2 2 0 0 1-.7-2.2C8.5 10.8 8 9.5 8 8"/><path d="M9 14.5a3.5 3.5 0 1 0 6 0"/></svg>',
  "tool_call": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#ffb74d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
  "attachment": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#64b5f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>',
  "temperature": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#ef9a9a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>',
  "open_weights": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#81c784" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/><path d="M21 16v2a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-2"/></svg>',
  "code_specialized": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
  "supports_web_search": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#4dd0e1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="8" y1="11" x2="14" y2="11"/><line x1="11" y1="8" x2="11" y2="14"/></svg>',
};

const CAPABILITY_LABELS = {
  "reasoning": "Supports reasoning",
  "tool_call": "Supports tool calling",
  "attachment": "Supports file attachments",
  "temperature": "Supports temperature control",
  "open_weights": "Open weights model",
  "code_specialized": "Specialized for code",
  "supports_web_search": "Supports web search",
};

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

const EXCLUDED_FAMILIES = ["instruct", "mini", "embed", "image"];
const CAP_ORDER = ["reasoning", "tool_call", "attachment", "temperature", "open_weights", "code_specialized", "supports_web_search"];
const OUTDATED_MONTHS = 6;
const SEARCH_DEBOUNCE_MS = 150;

let modelsData = {};
let currentProvider = null;
let currentFamily = "all";
let sortedModelsCache = {};
let searchQuery = "";
let hideOutdated = false;
let showOnlyFree = false;
let filterBtnIndex = 0;
let toastTimer = null;

const dialog = document.createElement("dialog");
dialog.id = "models-modal";
dialog.className = "mm";
dialog.setAttribute("aria-label", "All Models");

dialog.innerHTML = `
  <div class="mm__scroller">
    <header class="mm__header">
      <h3 class="mm__title"></h3>
      <button class="mm__close" aria-label="Close">&times;</button>
    </header>
    <p class="mm__note"></p>
    <input type="text" class="mm__search" placeholder="Search models…" autocomplete="off" spellcheck="false" />
    <div class="mm__filters"></div>
    <div class="mm__body" aria-live="polite" aria-relevant="additions removals"></div>
  </div>
`;
document.body.appendChild(dialog);

// Cached DOM refs
const titleEl = dialog.querySelector(".mm__title");
const noteEl = dialog.querySelector(".mm__note");
const closeBtn = dialog.querySelector(".mm__close");
const searchInput = dialog.querySelector(".mm__search");
const filtersContainer = dialog.querySelector(".mm__filters");
const bodyEl = dialog.querySelector(".mm__body");

const canonical = document.querySelector('link[rel="canonical"]');
let jsonUrl;
if (canonical) {
  const c = canonical.href;
  jsonUrl = c.replace(/\/([^/]+\/?)?$/, "/models_data.json");
} else {
  jsonUrl = `${window.location.origin}/models_data.json`;
}

const fallbackUrls = [
  jsonUrl,
  new URL("../models_data.json", window.location.href).href,
];

function tryFetch(urls, idx) {
  if (idx >= urls.length) return;
  fetch(urls[idx])
    .then((res) => {
      if (!res.ok) throw new Error("Failed");
      return res.json();
    })
    .then((data) => { modelsData = data; })
    .catch(() => { tryFetch(urls, idx + 1); });
}

tryFetch(fallbackUrls, 0);

function showToast(text) {
  const old = document.querySelector(".models-toast");
  if (old) old.remove();
  if (toastTimer) clearTimeout(toastTimer);

  const toast = document.createElement("div");
  toast.className = "models-toast";
  toast.textContent = text;
  dialog.appendChild(toast);

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
  const providerData = modelsData[currentProvider];
  const fromProvider = providerData?.metadata?.[modelId];
  const fromGlobal = modelsData._models?.[modelId];

  if (fromProvider && fromGlobal) return { ...fromGlobal, ...fromProvider };
  if (fromProvider) return fromProvider;
  if (fromGlobal) return fromGlobal;

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
  const release = new Date(meta.release_date);
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

function _getModelPrice(modelId) {
  const providerData = modelsData[currentProvider];
  if (!providerData?.pricing?.models?.[modelId]) return null;
  return providerData.pricing.models[modelId];
}

function _formatCost(meta, modelId) {
  const priceData = modelId ? _getModelPrice(modelId) : null;
  if (priceData) {
    const parts = [];
    if (priceData.input != null) parts.push(`in $${priceData.input}`);
    if (priceData.output != null) parts.push(`out $${priceData.output}`);
    if (priceData.cache != null && priceData.cache > 0) {
      const c = priceData.cache < 1 ? priceData.cache.toFixed(2) : priceData.cache;
      parts.push(`c $${c}`);
    }
    if (parts.length) return parts.join(" / ");
  }
  if (!meta?.cost) return "";
  const c = meta.cost;
  const parts = [];
  if (c.input != null) parts.push(`in $${c.input}`);
  if (c.output != null) parts.push(`out $${c.output}`);
  if (c.cache_read != null && c.cache_read > 0) {
    const cache = c.cache_read < 1 ? c.cache_read.toFixed(2) : c.cache_read;
    parts.push(`c $${cache}`);
  }
  return parts.length ? parts.join(" / ") : "";
}

function _formatLimit(meta) {
  if (!meta?.limit) return "";
  const parts = [];
  const ctx = meta.limit.context;
  if (ctx != null) {
    if (ctx >= 1000000) parts.push(`${(ctx / 1000000).toFixed(1)}M ctx`);
    else if (ctx >= 1000) parts.push(`${(ctx / 1000).toFixed(0)}K ctx`);
    else parts.push(`${ctx} ctx`);
  }
  const out = meta.limit.output;
  if (out != null) {
    if (out >= 1000000) parts.push(`${(out / 1000000).toFixed(1)}M out`);
    else if (out >= 1000) parts.push(`${(out / 1000).toFixed(0)}K out`);
    else parts.push(`${out} out`);
  }
  return parts.join(" / ");
}

function _formatDate(meta) {
  if (!meta?.release_date) return "";
  return meta.release_date;
}

function _formatModalities(meta) {
  if (!meta?.modalities) return "";
  const input = meta.modalities.input;
  const output = meta.modalities.output;
  if (!input && !output) return "";
  const map = { text: "txt", image: "img", document: "pdf", audio: "aud", video: "vid" };
  const inStr = (input || []).map((m) => map[m] || m).join(" · ");
  const outStr = (output || []).map((m) => map[m] || m).join(" · ");
  if (inStr && outStr) return `${inStr} → ${outStr}`;
  return inStr || outStr;
}

function _formatTier(meta) {
  if (!meta?.tier) return "";
  return meta.tier;
}

function _formatDiscount(meta) {
  if (!meta?.discount?.label) return "";
  return meta.discount.label;
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
      if (m[2] !== undefined) return parseInt(m[1], 10) * 1000 + parseInt(m[2], 10) * 10;
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
      if (lastMatchIdx >= 0) totalGap += si - lastMatchIdx;
      if (prevMatched) consecutiveBonus++;
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

function getSortedModels(models) {
  const cacheKey = models.join(",");
  if (sortedModelsCache[cacheKey]) return sortedModelsCache[cacheKey];
  const sorted = models.slice().sort(_sortByReleaseDate);
  sortedModelsCache[cacheKey] = sorted;
  return sorted;
}

function groupByFamily(modelIds) {
  const families = {};
  modelIds.forEach((id) => {
    const famKey = _getModelFamily(id) || "other";
    if (!families[famKey]) families[famKey] = [];
    families[famKey].push(id);
  });
  return families;
}


function buildFilters(families, allModelsCount) {
  filtersContainer.innerHTML = "";

  const providerData = modelsData[currentProvider];
  let allModelIds = [];
  if (providerData && typeof providerData === "object" && providerData.all) {
    allModelIds = providerData.all;
  } else if (Array.isArray(providerData)) {
    allModelIds = providerData;
  }
  const hasFreeModels = allModelIds.some((id) => id.toLowerCase().includes("free"));
  const chipsWrap = document.createElement("div");
  chipsWrap.className = "mm__chips";

  const allBtn = document.createElement("button");
  allBtn.className = `mm-chip${currentFamily === "all" ? " mm-chip--active" : ""}`;
  allBtn.setAttribute("data-family", "all");
  allBtn.textContent = `All (${allModelsCount})`;
  allBtn.title = "Show all models";
  chipsWrap.appendChild(allBtn);

  if (families && Object.keys(families).length > 0) {
    const entries = Object.entries(families).filter((e) => EXCLUDED_FAMILIES.indexOf(e[0]) === -1);

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
      btn.className = `mm-chip${currentFamily === keyword ? " mm-chip--active" : ""}`;
      btn.setAttribute("data-family", keyword);
      btn.textContent = `${label} (${count})`;
      btn.title = `Show only ${label}`;
      chipsWrap.appendChild(btn);
    });
  }

  filtersContainer.appendChild(chipsWrap);

  const togglesWrap = document.createElement("div");
  togglesWrap.className = "mm__toggles";

  const toggleWrap = document.createElement("label");
  toggleWrap.className = "mm-toggle";
  const toggleCb = document.createElement("input");
  toggleCb.type = "checkbox";
  toggleCb.checked = hideOutdated;
  toggleCb.title = "Hide models older than 6 months";
  toggleCb.addEventListener("change", () => {
    hideOutdated = toggleCb.checked;
    rerenderFromFilters();
  });
  toggleWrap.appendChild(toggleCb);
  toggleWrap.appendChild(document.createTextNode("Hide outdated"));
  togglesWrap.appendChild(toggleWrap);

  if (hasFreeModels) {
    const freeWrap = document.createElement("label");
    freeWrap.className = "mm-toggle";
    const freeCb = document.createElement("input");
    freeCb.type = "checkbox";
    freeCb.checked = showOnlyFree;
    freeCb.title = "Show only models with 'free' in the name";
    freeCb.addEventListener("change", () => {
      showOnlyFree = freeCb.checked;
      rerenderFromFilters();
    });
    freeWrap.appendChild(freeCb);
    freeWrap.appendChild(document.createTextNode("Free only"));
    togglesWrap.appendChild(freeWrap);
  }

  filtersContainer.appendChild(togglesWrap);
}

function rerenderFromFilters() {
  const providerData = modelsData[currentProvider];
  if (!providerData) return;
  let modelsToRender;
  if (currentFamily === "all") {
    modelsToRender = providerData.all || (Array.isArray(providerData) ? providerData : []);
  } else {
    const fam = providerData.families ? providerData.families[currentFamily] : null;
    modelsToRender = fam ? (fam.models || fam) : [];
  }
  renderModels(modelsToRender);
}

let sectionObserver = null;

function initSectionObserver() {
  if (sectionObserver) sectionObserver.disconnect();
  sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const section = entry.target;
        const family = section.getAttribute("data-family");
        if (!section.dataset.rendered && window._pendingSections?.[family]) {
          renderSectionCards(section, window._pendingSections[family]);
          section.dataset.rendered = "true";
          delete window._pendingSections[family];
        }
      }
    });
  }, { rootMargin: "300px" });
}

function renderSectionCards(sectionEl, modelIds) {
  const grid = sectionEl.querySelector(".mm-section__grid");
  grid.innerHTML = "";

  const sorted = getSortedModels(modelIds);

  let renderedCount = 0;
  sorted.forEach((id) => {
    const meta = _getModelMeta(id);
    if (hideOutdated && _isOutdated(meta)) return;
    if (showOnlyFree && !id.toLowerCase().includes("free")) return;

    if (searchQuery) {
      const normalizedQuery = searchQuery.toLowerCase().replace(/[^a-z0-9]/g, "");
      const normalizedId = id.toLowerCase().replace(/[^a-z0-9]/g, "");
      if (!normalizedId.includes(normalizedQuery)) {
        const fuzzyScore = fuzzyMatch(normalizedQuery, normalizedId);
        if (fuzzyScore <= 0) return;
      }
    }

    grid.appendChild(renderCard(id, meta));
    renderedCount++;
  });

  if (renderedCount === 0) {
    grid.innerHTML = '<p class="mm-empty">No models match the current filters</p>';
  }
}

function renderCard(id, meta) {
  const card = document.createElement("article");
  card.className = `mm-card${meta?.featured ? " mm-card--featured" : ""}`;
  card.setAttribute("data-model", id);
  // Твоя система копирования
  card.addEventListener("click", (event) => {
    if (event.target.closest(".mm-cap")) return;
    copyText(id);
  });

  const idEl = document.createElement("div");
  idEl.className = "mm-card__id";
  idEl.textContent = id;
  card.appendChild(idEl);

  const metaEl = document.createElement("div");
  metaEl.className = "mm-card__meta";

  const costStr = _formatCost(meta, id);
  const limitStr = _formatLimit(meta);
  const modStr = _formatModalities(meta);

  if (costStr) {
    const row1 = document.createElement("div");
    row1.className = "mm-card__meta-row";
    row1.innerHTML = `<span class="mm-card__meta-label">Pricing:</span><span class="mm-card__cost">${costStr}</span>`;
    metaEl.appendChild(row1);
  }

  if (limitStr) {
    const row2 = document.createElement("div");
    row2.className = "mm-card__meta-row";
    row2.innerHTML = `<span class="mm-card__meta-label">Limits:</span><span class="mm-card__limit">${limitStr}</span>`;
    metaEl.appendChild(row2);
  }
  if (modStr) {
    const row3 = document.createElement("div");
    row3.className = "mm-card__meta-row mm-card__meta-row--modalities";
    row3.innerHTML = `<span class="mm-card__meta-label">I/O:</span><span class="mm-card__modalities">${modStr}</span>`;
    metaEl.appendChild(row3);
  }

  if (metaEl.children.length) {
    card.appendChild(metaEl);
  }

  const footer = document.createElement("div");
  footer.className = "mm-card__footer";

  const dateStr = _formatDate(meta);
  if (dateStr) {
    const dateEl = document.createElement("span");
    dateEl.className = "mm-card__date";
    dateEl.textContent = dateStr;
    footer.appendChild(dateEl);
  }

  const caps = document.createElement("div");
  caps.className = "mm-card__caps";
  caps.addEventListener("click", (event) => {
    if (event.target.closest(".mm-cap")) {
      event.stopPropagation();
    }
  });
  for (const key of CAP_ORDER) {
    if (meta?.[key]) {
      const span = document.createElement("span");
      span.className = "mm-cap";
      span.setAttribute("data-tooltip", CAPABILITY_LABELS[key]);
      span.setAttribute("aria-label", CAPABILITY_LABELS[key]);
      span.setAttribute("tabindex", "0");
      span.setAttribute("role", "button");
      span.title = CAPABILITY_LABELS[key];
      span.innerHTML = CAPABILITY_ICONS[key];
      caps.appendChild(span);
    }
  }

  if (caps.children.length) {
    footer.appendChild(caps);
  }

  if (footer.children.length) {
    card.appendChild(footer);
  }

  return card;
}

function renderModels(models) {
  bodyEl.innerHTML = "";

  if (!models || models.length === 0) {
    bodyEl.innerHTML = '<p class="mm-empty">No models in this category</p>';
    return;
  }

  const filtered = [];

  models.forEach((id) => {
    const meta = _getModelMeta(id);
    if (hideOutdated && _isOutdated(meta)) return;
    if (showOnlyFree && !id.toLowerCase().includes("free")) return;
    filtered.push(id);
  });

  if (filtered.length === 0) {
    bodyEl.innerHTML = '<p class="mm-empty">No models match the current filters</p>';
    return;
  }

  let renderList = filtered;
  if (searchQuery) {
    const normalizedQuery = searchQuery.toLowerCase().replace(/[^a-z0-9]/g, "");
    let results = [];
    const exactMatches = [];
    filtered.forEach((id) => {
      const normalizedId = id.toLowerCase().replace(/[^a-z0-9]/g, "");
      if (normalizedId.includes(normalizedQuery)) {
        exactMatches.push({ id, index: normalizedId.indexOf(normalizedQuery) });
      }
    });
    if (exactMatches.length > 0) {
      exactMatches.sort((a, b) => a.index - b.index);
      results = exactMatches.map((m) => m.id);
    } else {
      const fuzzyMatches = [];
      filtered.forEach((id) => {
        const score = fuzzyMatch(normalizedQuery, id.toLowerCase().replace(/[^a-z0-9]/g, ""));
        if (score > 0) fuzzyMatches.push({ id, score });
      });
      fuzzyMatches.sort((a, b) => b.score - a.score);
      results = fuzzyMatches.map((m) => m.id);
    }
    if (results.length === 0) {
      bodyEl.innerHTML = `<p class="mm-empty">No models match "${searchQuery}"</p>`;
      return;
    }
    renderList = results;
  }

  const families = groupByFamily(renderList);

  const famEntries = Object.entries(families).sort((a, b) => {
    const aIsOther = a[0] === "other";
    const bIsOther = b[0] === "other";
    if (aIsOther && !bIsOther) return 1;
    if (!aIsOther && bIsOther) return -1;

    const aMaxDate = Math.max(...a[1].map((id) => {
      const m = _getModelMeta(id);
      return m?.release_date ? new Date(m.release_date).getTime() : 0;
    }));
    const bMaxDate = Math.max(...b[1].map((id) => {
      const m = _getModelMeta(id);
      return m?.release_date ? new Date(m.release_date).getTime() : 0;
    }));
    return bMaxDate - aMaxDate;
  });
  initSectionObserver();
  window._pendingSections = {};

  famEntries.forEach(([famKey, famModelIds]) => {
    const label = getFamilyLabel(famKey);
    const section = document.createElement("section");
    section.className = "mm-section";
    section.setAttribute("data-family", famKey);

    const title = document.createElement("h4");
    title.className = "mm-section__title";
    title.innerHTML = `<span>${label}</span><span class="mm-section__count">${famModelIds.length}</span>`;
    section.appendChild(title);

    const grid = document.createElement("div");
    grid.className = "mm-section__grid";
    section.appendChild(grid);

    bodyEl.appendChild(section);

    if (searchQuery) {
      renderSectionCards(section, famModelIds);
      section.dataset.rendered = "true";
    } else {
      window._pendingSections[famKey] = famModelIds;
      sectionObserver.observe(section);
    }
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

  if (!providerData) {
    titleEl.innerHTML = `${providerName} — All Models`;
    noteEl.textContent = "";
    filtersContainer.innerHTML = "";
    bodyEl.innerHTML = '<p class="mm-empty">No model data available for this provider.<br><br>The model list may not have been fetched yet, or the provider was recently added.</p>';
    searchInput.style.display = "none";
    dialog.showModal();
    return;
  }

  searchInput.style.display = "";

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

  const sourceBadge = providerData?.pricing?.badge;
  const sourceUrl = providerData?.pricing?.source_url;
  const sourceReliability = providerData?.pricing?.reliability;
  let reliabilityNote = "";
  if (sourceBadge && sourceReliability === "unstable") {
    reliabilityNote = ' <span class="models-source-warn">(verify)</span>';
  }
  let sourceTooltip = "";
  if (sourceUrl) {
    sourceTooltip = `Data source: ${sourceUrl}`;
    if (sourceReliability) {
      sourceTooltip += ` (reliability: ${sourceReliability})`;
    }
  }
  titleEl.innerHTML = `${providerName} — All Models (${allModels.length})` +
    (sourceBadge ? ` <span class="models-source-badge"${sourceTooltip ? ` data-tooltip="${sourceTooltip}"` : ""}>${sourceBadge}${reliabilityNote}</span>` : "");

  noteEl.textContent = "Click any model to copy its ID. Sorting may not be exact. Pricing, context window, and other metadata show only official provider data.";

  buildFilters(families, allModels ? allModels.length : 0);
  filterBtnIndex = 0;
  renderModels(allModels);

  dialog.showModal();

  if (searchInput !== document.activeElement) {
    setTimeout(() => searchInput.focus(), 100);
  }
}

function closeModal() {
  dialog.close();
  currentProvider = null;
  currentFamily = "all";
  hideOutdated = false;
  showOnlyFree = false;
  searchQuery = "";
  searchInput.value = "";
}

closeBtn.addEventListener("click", closeModal);

dialog.addEventListener("close", () => {
  if (currentProvider) {
    currentProvider = null;
    currentFamily = "all";
    hideOutdated = false;
    showOnlyFree = false;
    searchQuery = "";
    searchInput.value = "";
  }
});

if (!("closedBy" in HTMLDialogElement.prototype)) {
  dialog.addEventListener("click", (event) => {
    if (event.target !== dialog) return;
    const rect = dialog.getBoundingClientRect();
    const isDialogContent = (
      rect.top <= event.clientY &&
      event.clientY <= rect.top + rect.height &&
      rect.left <= event.clientX &&
      event.clientX <= rect.left + rect.width
    );
    if (isDialogContent) return;
    closeModal();
  });
}

filtersContainer.addEventListener("click", (e) => {
  const btn = e.target.closest(".mm-chip");
  if (!btn || !currentProvider) return;

  const family = btn.getAttribute("data-family");
  if (!family || family === currentFamily) return;

  currentFamily = family;

  const chips = filtersContainer.querySelectorAll(".mm-chip");
  chips.forEach((b, i) => {
    b.classList.toggle("mm-chip--active", b.getAttribute("data-family") === family);
    if (b.getAttribute("data-family") === family) filterBtnIndex = i;
  });

  rerenderFromFilters();
});

filtersContainer.addEventListener("keydown", (e) => {
  const chips = filtersContainer.querySelectorAll(".mm-chip");
  if (chips.length === 0) return;

  if (e.key === "ArrowRight" || e.key === "ArrowDown") {
    e.preventDefault();
    filterBtnIndex = (filterBtnIndex + 1) % chips.length;
    chips[filterBtnIndex].focus();
  } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
    e.preventDefault();
    filterBtnIndex = (filterBtnIndex - 1 + chips.length) % chips.length;
    chips[filterBtnIndex].focus();
  } else if (e.key === "Home") {
    e.preventDefault();
    filterBtnIndex = 0;
    chips[filterBtnIndex].focus();
  } else if (e.key === "End") {
    e.preventDefault();
    filterBtnIndex = chips.length - 1;
    chips[filterBtnIndex].focus();
  }
});

let searchTimer = null;
searchInput.addEventListener("input", () => {
  const q = searchInput.value.trim();
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    searchQuery = q;
    const providerData = modelsData[currentProvider];
    if (!providerData) return;
    let modelsToRender;
    if (currentFamily === "all") {
      modelsToRender = providerData.all || (Array.isArray(providerData) ? providerData : []);
    } else {
      const fam = providerData.families ? providerData.families[currentFamily] : null;
      modelsToRender = fam ? (fam.models || fam) : [];
    }
    renderModels(modelsToRender);
  }, SEARCH_DEBOUNCE_MS);
});

document.addEventListener("click", (e) => {
  const trigger = e.target.closest(".models-show-all");
  if (trigger) {
    e.preventDefault();
    e.stopPropagation();
    const provider = trigger.getAttribute("data-provider");
    if (provider) openModal(provider);
  }
});
