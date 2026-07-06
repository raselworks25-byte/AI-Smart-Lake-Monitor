(() => {
  /* ── Theme Toggle ── */
  const themeToggle = document.getElementById('themeToggle');
  const themeIcon   = document.getElementById('themeIcon');
  const htmlEl      = document.documentElement;

  const applyTheme = (theme) => {
    htmlEl.setAttribute('data-theme', theme);
    if (themeIcon) themeIcon.textContent = theme === 'light' ? '☀️' : '🌙';
    localStorage.setItem('fb-theme', theme);
  };

  // Load saved preference
  applyTheme(localStorage.getItem('fb-theme') || 'dark');

  themeToggle?.addEventListener('click', () => {
    applyTheme(htmlEl.getAttribute('data-theme') === 'light' ? 'dark' : 'light');
  });

  /* ── Quick Menu ── */
  const quickMenuToggle   = document.getElementById('quickMenuToggle');
  const quickMenuPanel    = document.getElementById('quickMenuPanel');
  const quickMenuBackdrop = document.getElementById('quickMenuBackdrop');
  const closeQuickMenu    = document.getElementById('closeQuickMenu');

  const setQuickMenuState = (open) => {
    if (!quickMenuPanel || !quickMenuBackdrop) return;
    quickMenuPanel.classList.toggle('open', open);
    quickMenuBackdrop.classList.toggle('open', open);
    quickMenuPanel.setAttribute('aria-hidden', open ? 'false' : 'true');
  };

  quickMenuToggle?.addEventListener('click', () => {
    setQuickMenuState(!quickMenuPanel?.classList.contains('open'));
  });
  closeQuickMenu?.addEventListener('click', () => setQuickMenuState(false));
  quickMenuBackdrop?.addEventListener('click', () => setQuickMenuState(false));
  document.querySelectorAll('.quick-menu-link').forEach(l => l.addEventListener('click', () => setQuickMenuState(false)));
  document.addEventListener('keydown', e => { if (e.key === 'Escape') setQuickMenuState(false); });

  /* ── Containers ── */
  const statusContainer          = document.getElementById('systemStatus');
  const waterQualityContainer    = document.getElementById('waterQualityCards');
  const detectionSummaryContainer= document.getElementById('detectionSummary');
  const alertsList               = document.getElementById('alertsList');
  const detectionTable           = document.getElementById('detectionTable');
  const waterTable               = document.getElementById('waterTable');
  const trendSelect              = document.getElementById('trendPeriod');
  const lastUpdateLabel          = document.getElementById('lastUpdateLabel');

  let trendChart;

  /* ── Helpers ── */
  const statusClass = (value) => {
    const v = String(value).toLowerCase();
    if (v.includes('online') || v.includes('good') || v.includes('streaming') || v.includes('healthy')) return 'status-ok';
    if (v.includes('moderate') || v.includes('warning')) return 'status-warn';
    return 'status-bad';
  };

  const buildMetricTile = (name, value, subtitle, status = '') => `
    <div class="metric-tile">
      <div class="metric-name">${name}</div>
      <div class="metric-value">${value}</div>
      <div class="metric-updated">${subtitle}</div>
      ${status ? `<div class="status-badge ${statusClass(status)}">${status}</div>` : ''}
    </div>
  `;

  /* ── Trend Chart ── */
  const renderTrendChart = (payload) => {
    const canvas = document.getElementById('trendChart');
    if (!canvas) return;
    if (trendChart) trendChart.destroy();

    const gridColor = 'rgba(255,255,255,0.05)';
    const tickColor = '#5a7a8e';

    trendChart = new Chart(canvas, {
      type: 'line',
      data: {
        labels: payload.labels,
        datasets: [
          { label: 'TDS (ppm)',       data: payload.tds,         borderColor: '#00e5cc', backgroundColor: 'rgba(0,229,204,0.06)', tension: 0.4, pointRadius: 2, borderWidth: 2, fill: true },
          { label: 'Turbidity (NTU)', data: payload.turbidity,   borderColor: '#f59e0b', backgroundColor: 'rgba(245,158,11,0.05)', tension: 0.4, pointRadius: 2, borderWidth: 2 },
          { label: 'Temp (°C)',       data: payload.temperature, borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.05)', tension: 0.4, pointRadius: 2, borderWidth: 2 },
          { label: 'Waste Count',     data: payload.waste,       borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,0.05)', tension: 0.4, pointRadius: 2, borderWidth: 2 },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: {
            labels: { color: tickColor, font: { size: 11, family: 'Manrope' }, boxWidth: 10, padding: 16 }
          },
          tooltip: {
            backgroundColor: 'rgba(8,20,34,0.95)',
            borderColor: 'rgba(0,229,204,0.3)',
            borderWidth: 1,
            titleColor: '#00e5cc',
            bodyColor: '#94b3c8',
            padding: 10,
            cornerRadius: 10,
          }
        },
        scales: {
          x: {
            ticks: { color: tickColor, font: { size: 10, family: 'JetBrains Mono' }, maxRotation: 0 },
            grid: { color: gridColor },
            border: { color: 'transparent' },
          },
          y: {
            ticks: { color: tickColor, font: { size: 10, family: 'JetBrains Mono' } },
            grid: { color: gridColor },
            border: { color: 'transparent' },
          },
        },
      },
    });
  };

  /* ── Table renderers ── */
  const renderDetections = (rows) => {
    if (!detectionTable) return;
    detectionTable.innerHTML = rows.map(row => `
      <tr>
        <td>${row.timestamp}</td>
        <td>${row.class_id ?? '-'}</td>
        <td>${row.class_name || row.object_type || '-'}</td>
        <td>${row.bottle_count}</td>
        <td>${row.debris_count}</td>
        <td><strong style="color:var(--text);">${row.total_objects}</strong></td>
        <td><span style="color:var(--teal);">${row.confidence_score}</span></td>
      </tr>
    `).join('');
  };

  const renderWaterLogs = (rows) => {
    if (!waterTable) return;
    waterTable.innerHTML = rows.map(row => `
      <tr>
        <td>${row.timestamp}</td>
        <td>${row.tds}</td>
        <td>${row.turbidity}</td>
        <td>${row.temperature}</td>
        <td><span class="status-badge ${statusClass(row.status)}">${row.status}</span></td>
      </tr>
    `).join('');
  };

  const refreshStreamSnapshot = async () => {
    try {
      const response = await fetch('/api/stream/snapshot');
      const payload = await response.json();
      const snapshotImage = document.getElementById('streamSnapshotImage');
      if (snapshotImage && payload.snapshot_url) {
        snapshotImage.src = `${payload.snapshot_url}${payload.snapshot_url.includes('?') ? '&' : '?'}v=${Date.now()}`;
      }

      const streamIndicator = document.getElementById('streamIndicator');
      if (streamIndicator) {
        const isLive = Boolean(payload.snapshot_url && payload.snapshot_url !== '/static/img/placeholder-detection.svg');
        streamIndicator.className = `stream-pill ${isLive ? 'live-pill' : 'offline-pill'}`;
        streamIndicator.innerHTML = `<span style="width:6px;height:6px;border-radius:50%;background:currentColor;display:inline-block;${isLive ? 'animation:dot-blink 1.8s infinite;' : ''}"></span> ${isLive ? 'Live' : 'Offline'}`;
      }
    } catch (err) {
      console.warn('refreshStreamSnapshot error', err);
    }
  };

  /* ── API calls ── */
  const loadOverview = async () => {
    try {
      const response = await fetch('/api/overview');
      const payload  = await response.json();

      if (lastUpdateLabel) lastUpdateLabel.textContent = `Updated: ${payload.status.last_update}`;

      if (statusContainer) {
        statusContainer.innerHTML = [
          buildMetricTile('Raspberry Pi', payload.status.raspberry_pi, `Last sync: ${payload.status.last_update}`),
          buildMetricTile('ESP32',        payload.status.esp32,         'UART sensor bridge', payload.status.esp32),
          buildMetricTile('Camera',       payload.status.camera,        'Live stream ready',  payload.status.camera),
          buildMetricTile('System Sync',  'Healthy',                    'Cloud DB active',    'Healthy'),
        ].join('');
      }

      if (waterQualityContainer) {
        const w = payload.water_quality;
        waterQualityContainer.innerHTML = [
          buildMetricTile('TDS',         `${w.tds} ppm`,         `Threshold: ${w.thresholds.tds} ppm`,         w.status),
          buildMetricTile('Turbidity',   `${w.turbidity} NTU`,   `Threshold: ${w.thresholds.turbidity} NTU`,   w.status),
          buildMetricTile('Temperature', `${w.temperature} °C`,  `Threshold: ${w.thresholds.temperature} °C`,  w.status),
          buildMetricTile('Water Status', w.status,               'Real-time classification',                   w.status),
        ].join('');
      }

      if (detectionSummaryContainer) {
        const d = payload.detection_summary;
        detectionSummaryContainer.innerHTML = [
          buildMetricTile('Plastic Bottle', d.plastic_bottle, 'Class 0'),
          buildMetricTile('Debris',         d.debris,         'Class 1'),
          buildMetricTile('Total Detections', d.total_waste,   `Latest: ${d.latest_class_name || 'N/A'}`),
        ].join('');
      }

      if (alertsList) {
        alertsList.innerHTML = payload.alerts.map(alert => `
          <div class="alert-item ${alert.level.toLowerCase()}">
            <div>
              <div class="alert-level">${alert.level}</div>
              <div class="alert-msg">${alert.message}</div>
            </div>
            <div class="alert-time">${alert.time}</div>
          </div>
        `).join('');
      }

      /* Stream indicator */
      const streamIndicator = document.getElementById('streamIndicator');
      if (streamIndicator) {
        const isLive = payload.status.camera === 'Streaming';
        streamIndicator.className = `stream-pill ${isLive ? 'live-pill' : 'offline-pill'}`;
        streamIndicator.innerHTML = `<span style="width:6px;height:6px;border-radius:50%;background:currentColor;display:inline-block;${isLive ? 'animation:dot-blink 1.8s infinite;' : ''}"></span> ${isLive ? 'Live' : 'Offline'}`;
      }
    } catch (err) {
      console.warn('loadOverview error', err);
    }
  };

  const loadLogs = async () => {
    try {
      const [dr, wr] = await Promise.all([
        fetch('/api/detections'),
        fetch('/api/water-quality/logs'),
      ]);
      renderDetections(await dr.json());
      renderWaterLogs(await wr.json());
    } catch (err) {
      console.warn('loadLogs error', err);
    }
  };

  const loadTrend = async (period = 'today') => {
    try {
      const response = await fetch(`/api/charts/${period}`);
      renderTrendChart(await response.json());
    } catch (err) {
      console.warn('loadTrend error', err);
    }
  };

  const refreshTrend = () => loadTrend(trendSelect?.value || 'today');

  trendSelect?.addEventListener('change', refreshTrend);

  document.querySelectorAll('[data-filter]').forEach(btn => {
    btn.addEventListener('click', () => {
      if (trendSelect) trendSelect.value = btn.dataset.filter;
      loadTrend(btn.dataset.filter);
    });
  });

  /* Stream controls */
  document.getElementById('startStream')?.addEventListener('click', () => {
    const ind = document.getElementById('streamIndicator');
    if (ind) { ind.className = 'stream-pill live-pill'; ind.innerHTML = '<span style="width:6px;height:6px;border-radius:50%;background:currentColor;display:inline-block;animation:dot-blink 1.8s infinite;"></span> Live'; }
  });

  document.getElementById('stopStream')?.addEventListener('click', () => {
    const ind = document.getElementById('streamIndicator');
    if (ind) { ind.className = 'stream-pill offline-pill'; ind.innerHTML = '<span style="width:6px;height:6px;border-radius:50%;background:currentColor;display:inline-block;"></span> Offline'; }
  });

  document.getElementById('snapshotBtn')?.addEventListener('click', () => {
    fetch('/api/stream/snapshot').then(r => r.json()).then(p => alert(`Snapshot saved at ${p.timestamp}`));
  });

  document.getElementById('fullscreenBtn')?.addEventListener('click', () => {
    document.querySelector('.stream-panel')?.requestFullscreen?.();
  });

  /* Init */
  loadOverview();
  loadLogs();
  loadTrend();
  refreshStreamSnapshot();

  setInterval(loadOverview, 10000);
  setInterval(loadLogs,     20000);
  setInterval(refreshTrend, 30000);
  setInterval(refreshStreamSnapshot, 5000);
})();
