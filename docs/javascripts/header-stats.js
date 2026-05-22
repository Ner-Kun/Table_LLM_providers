(() => {
  const container = document.querySelector('.md-header__inner');
  if (!container) return;

  const stats = document.createElement('div');
  stats.className = 'header-stats';
  stats.innerHTML =
    '<div class="header-stat">' +
      '<span class="header-stat-number" id="stat-providers">0</span>' +
      '<span class="header-stat-label">providers</span>' +
    '</div>' +
    '<div class="header-stat-divider"></div>' +
    '<div class="header-stat header-stat-models">' +
      '<span class="header-stat-date" id="stat-models-date">&mdash;</span>' +
      '<span class="header-stat-time" id="stat-models-time"></span>' +
      '<span class="header-stat-label">Model updates</span>' +
    '</div>';

  const search = container.querySelector('.md-search');
  if (search) {
    container.insertBefore(stats, search);
  } else {
    container.appendChild(stats);
  }

  let base = '';
  const scripts = document.getElementsByTagName('script');
  for (let i = 0; i < scripts.length; i++) {
    const src = scripts[i].src;
    if (src.indexOf('header-stats') !== -1) {
      base = src.substring(0, src.lastIndexOf('/') + 1);
      break;
    }
  }

  fetch(`${base}../models_data.json`)
    .then(r => r.json())
    .then(data => {
      const el = document.getElementById('stat-providers');
      if (el && data._providers_count) {
        const target = data._providers_count;
        if (target > 0) {
          const duration = 800;
          const start = performance.now();
          function frame(now) {
            const t = Math.min((now - start) / duration, 1);
            const ease = 1 - (1 - t) ** 3;
            el.textContent = Math.round(ease * target);
            if (t < 1) requestAnimationFrame(frame);
          }
          requestAnimationFrame(frame);
        } else {
          el.textContent = target;
        }
      }

      const dateEl = document.getElementById('stat-models-date');
      const timeEl = document.getElementById('stat-models-time');
      if (dateEl && timeEl && data._models_updated) {
        const parts = data._models_updated.split(' ');
        dateEl.textContent = parts[0] || '\u2014';
        timeEl.textContent = parts.slice(1).join(' ') || '';
      }
    })
    .catch(() => {
    });
})();
