/* ============================================================
   TRUTHCHECK — Charts JS
   Dashboard Chart.js visualizations
   ============================================================ */

(function () {
  'use strict';

  // ── Chart Defaults ─────────────────────────────────────── //
  if (typeof Chart === 'undefined') return;

  Chart.defaults.color = '#6b7694';
  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.font.size = 12;
  Chart.defaults.borderColor = 'rgba(255,255,255,0.05)';

  // ── Activity Line Chart ────────────────────────────────── //
  function initActivityChart() {
    const ctx = document.getElementById('activityChart');
    if (!ctx) return;

    const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const realData   = [12, 18, 8, 25, 15, 22, 30];
    const fakeData   = [4,  7,  3, 10, 8,  6,  12];

    new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Real',
            data: realData,
            borderColor: '#00e5a0',
            backgroundColor: 'rgba(0, 229, 160, 0.08)',
            borderWidth: 2.5,
            pointBackgroundColor: '#00e5a0',
            pointRadius: 4,
            pointHoverRadius: 6,
            tension: 0.4,
            fill: true,
          },
          {
            label: 'Fake',
            data: fakeData,
            borderColor: '#ff4d6d',
            backgroundColor: 'rgba(255, 77, 109, 0.06)',
            borderWidth: 2.5,
            pointBackgroundColor: '#ff4d6d',
            pointRadius: 4,
            pointHoverRadius: 6,
            tension: 0.4,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { intersect: false, mode: 'index' },
        plugins: {
          legend: {
            position: 'top',
            align: 'end',
            labels: {
              boxWidth: 10,
              boxHeight: 10,
              borderRadius: 5,
              useBorderRadius: true,
              padding: 16,
            },
          },
          tooltip: {
            backgroundColor: '#0d1525',
            borderColor: 'rgba(255,255,255,0.07)',
            borderWidth: 1,
            padding: 12,
            titleFont: { weight: '600', size: 13 },
            bodyFont: { size: 12 },
            callbacks: {
              label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.y} checks`,
            },
          },
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { padding: 8 },
          },
          y: {
            grid: { color: 'rgba(255,255,255,0.04)' },
            ticks: {
              padding: 8,
              callback: val => val + '',
            },
            beginAtZero: true,
          },
        },
      },
    });
  }

  // ── Donut Chart ────────────────────────────────────────── //
  function initDonutChart() {
    const ctx = document.getElementById('donutChart');
    if (!ctx) return;

    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Authentic', 'Fake', 'Uncertain'],
        datasets: [{
          data: [68, 24, 8],
          backgroundColor: [
            'rgba(0, 229, 160, 0.85)',
            'rgba(255, 77, 109, 0.85)',
            'rgba(255, 181, 71, 0.85)',
          ],
          borderColor: [
            'rgba(0, 229, 160, 0.3)',
            'rgba(255, 77, 109, 0.3)',
            'rgba(255, 181, 71, 0.3)',
          ],
          borderWidth: 2,
          hoverOffset: 8,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0d1525',
            borderColor: 'rgba(255,255,255,0.07)',
            borderWidth: 1,
            padding: 12,
            callbacks: {
              label: ctx => ` ${ctx.label}: ${ctx.parsed}%`,
            },
          },
        },
      },
    });
  }

  // ── Animated Stat Counters ─────────────────────────────── //
  function animateCounters() {
    document.querySelectorAll('[data-count]').forEach(el => {
      const target   = parseInt(el.getAttribute('data-count'), 10);
      const suffix   = el.getAttribute('data-suffix') || '';
      const duration = 1500;
      const start    = performance.now();

      function step(now) {
        const elapsed  = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased    = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        const current  = Math.round(eased * target);
        el.textContent = current.toLocaleString() + suffix;
        if (progress < 1) requestAnimationFrame(step);
      }

      requestAnimationFrame(step);
    });
  }

  // ── Trust Score Ring ───────────────────────────────────── //
  window.animateTrustRing = function(score) {
    const ring = document.querySelector('.ring-fill');
    const pct  = document.querySelector('.trust-percent');
    if (!ring) return;

    const circumference = 408; // 2 * π * r (r = 65)
    const offset = circumference - (score / 100) * circumference;

    // Set color class
    ring.classList.remove('real', 'fake', 'warn');
    if (score >= 70) ring.classList.add('real');
    else if (score >= 40) ring.classList.add('warn');
    else ring.classList.add('fake');

    // Animate offset
    setTimeout(() => {
      ring.style.strokeDashoffset = offset;
    }, 300);

    // Animate number
    if (pct) {
      let current = 0;
      const duration = 1500;
      const start = performance.now();

      function step(now) {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        current = Math.round(eased * score);
        pct.textContent = current + '%';
        if (progress < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    }
  };

  // ── Period Toggle ──────────────────────────────────────── //
  function initPeriodTabs() {
    document.querySelectorAll('.period-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        // In real app, refetch chart data for selected period
      });
    });
  }

  // ── Init ───────────────────────────────────────────────── //
  document.addEventListener('DOMContentLoaded', () => {
    initActivityChart();
    initDonutChart();
    animateCounters();
    initPeriodTabs();

    // Auto-trigger trust ring if score is on the page
    const scoreEl = document.querySelector('[data-score]');
    if (scoreEl) {
      const score = parseInt(scoreEl.getAttribute('data-score'), 10);
      setTimeout(() => window.animateTrustRing(score), 500);
    }
  });

})();
