(() => {
  const headerInner = document.querySelector('.md-header__inner');
  if (!headerInner) return;

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

  const search = headerInner.querySelector('.md-search');
  if (search) {
    headerInner.insertBefore(stats, search);
  } else {
    headerInner.appendChild(stats);
  }

  const drawerTitle = document.querySelector('.md-nav--primary > .md-nav__title');
  const drawerStats = document.createElement('div');
  drawerStats.className = 'drawer-stats';
  drawerStats.innerHTML =
    '<div class="header-stat">' +
      '<span class="header-stat-number" id="drawer-stat-providers">0</span>' +
      '<span class="header-stat-label">providers</span>' +
    '</div>' +
    '<div class="header-stat-divider"></div>' +
    '<div class="header-stat header-stat-models">' +
      '<span class="header-stat-date" id="drawer-stat-models-date">&mdash;</span>' +
      '<span class="header-stat-time" id="drawer-stat-models-time"></span>' +
      '<span class="header-stat-label">Model updates</span>' +
    '</div>';

  if (drawerTitle?.parentElement) {
    drawerTitle.parentElement.insertBefore(drawerStats, drawerTitle.nextSibling);
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
      const hProv = document.getElementById('stat-providers');
      if (hProv && data._providers_count) {
        const target = data._providers_count;
        if (target > 0) {
          const duration = 800;
          const start = performance.now();
          function frame(now) {
            const t = Math.min((now - start) / duration, 1);
            const ease = 1 - (1 - t) ** 3;
            hProv.textContent = Math.round(ease * target);
            if (t < 1) requestAnimationFrame(frame);
          }
          requestAnimationFrame(frame);
        } else {
          hProv.textContent = target;
        }
      }

      const dProv = document.getElementById('drawer-stat-providers');
      if (dProv && data._providers_count) {
        dProv.textContent = data._providers_count;
      }

      const hDate = document.getElementById('stat-models-date');
      const hTime = document.getElementById('stat-models-time');
      if (hDate && hTime && data._models_updated) {
        const parts = data._models_updated.split(' ');
        hDate.textContent = parts[0] || '\u2014';
        hTime.textContent = parts.slice(1).join(' ') || '';
      }
      const dDate = document.getElementById('drawer-stat-models-date');
      const dTime = document.getElementById('drawer-stat-models-time');
      if (dDate && dTime && data._models_updated) {
        const parts = data._models_updated.split(' ');
        dDate.textContent = parts[0] || '\u2014';
        dTime.textContent = parts.slice(1).join(' ') || '';
      }
    })
    .catch(() => {});
})();
