/* ============================================================
   TRUTHCHECK — Sidebar JS
   Toggle collapse, active state, mobile overlay
   ============================================================ */

(function () {
  'use strict';

  const appShell  = document.querySelector('.app-shell');
  const sidebar   = document.querySelector('.sidebar');
  const toggle    = document.querySelector('.sidebar-toggle');
  const STORAGE_KEY = 'tc_sidebar_collapsed';

  // ── Restore Saved State ────────────────────────────────── //
  if (localStorage.getItem(STORAGE_KEY) === 'true') {
    appShell && appShell.classList.add('sidebar-collapsed');
    sidebar  && sidebar.classList.add('collapsed');
  }

  // ── Toggle Collapse ────────────────────────────────────── //
  if (toggle) {
    toggle.addEventListener('click', () => {
      const isCollapsed = sidebar.classList.toggle('collapsed');
      appShell && appShell.classList.toggle('sidebar-collapsed', isCollapsed);
      localStorage.setItem(STORAGE_KEY, isCollapsed);
    });
  }

  // ── Active Nav Item ────────────────────────────────────── //
  function setActiveNav() {
    const path = window.location.pathname;
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.remove('active');
      const href = item.getAttribute('href') || '';
      if (href === path || (href !== '/' && path.startsWith(href))) {
        item.classList.add('active');
      }
    });
  }

  setActiveNav();

  // ── Mobile Overlay ─────────────────────────────────────── //
  const mobileToggleBtn = document.querySelector('#mobile-menu-btn');
  const overlay = document.createElement('div');
  overlay.className = 'sidebar-overlay';
  overlay.style.cssText = `
    position: fixed; inset: 0; background: rgba(0,0,0,0.6);
    z-index: 99; display: none; backdrop-filter: blur(4px);
  `;
  document.body.appendChild(overlay);

  function openMobileSidebar() {
    sidebar && sidebar.classList.add('mobile-open');
    overlay.style.display = 'block';
    document.body.style.overflow = 'hidden';
  }

  function closeMobileSidebar() {
    sidebar && sidebar.classList.remove('mobile-open');
    overlay.style.display = 'none';
    document.body.style.overflow = '';
  }

  mobileToggleBtn && mobileToggleBtn.addEventListener('click', openMobileSidebar);
  overlay.addEventListener('click', closeMobileSidebar);

  // Close on resize back to desktop
  window.addEventListener('resize', () => {
    if (window.innerWidth > 720) closeMobileSidebar();
  });
})();
