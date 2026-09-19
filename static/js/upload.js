/* ============================================================
   TRUTHCHECK — Upload JS
   Drag-and-drop, file preview, character counter
   ============================================================ */

(function () {
  'use strict';

  // ── Drag-and-Drop Upload ───────────────────────────────── //
  function initUploadBox(boxSelector, inputSelector, previewSelector) {
    const box     = document.querySelector(boxSelector);
    const input   = document.querySelector(inputSelector);
    const preview = document.querySelector(previewSelector);

    if (!box || !input) return;

    // Click to browse
    box.addEventListener('click', (e) => {
      if (e.target.closest('.preview-remove')) return;
      input.click();
    });

    // File selected via input
    input.addEventListener('change', () => {
      if (input.files && input.files[0]) {
        handleFile(input.files[0], box, preview);
      }
    });

    // Drag events
    ['dragenter', 'dragover'].forEach(ev => {
      box.addEventListener(ev, (e) => {
        e.preventDefault(); e.stopPropagation();
        box.classList.add('dragover');
      });
    });

    ['dragleave', 'dragend'].forEach(ev => {
      box.addEventListener(ev, () => box.classList.remove('dragover'));
    });

    box.addEventListener('drop', (e) => {
      e.preventDefault(); e.stopPropagation();
      box.classList.remove('dragover');
      const file = e.dataTransfer.files[0];
      if (file) {
        // Assign to file input
        const dt = new DataTransfer();
        dt.items.add(file);
        input.files = dt.files;
        handleFile(file, box, preview);
      }
    });

    // Remove preview
    const removeBtn = preview && preview.querySelector('.preview-remove');
    if (removeBtn) {
      removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        resetUpload(box, input, preview);
      });
    }
  }

  function handleFile(file, box, preview) {
    // Validate type
    const allowed = ['image/png', 'image/jpeg', 'image/webp', 'image/gif', 'video/mp4', 'video/webm'];
    if (!allowed.includes(file.type)) {
      showToast('Invalid file type. Please upload an image or video.', 'error');
      return;
    }

    // Validate size (50MB)
    if (file.size > 50 * 1024 * 1024) {
      showToast('File too large. Maximum size is 50MB.', 'error');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      if (preview) {
        const img = preview.querySelector('img') || preview.querySelector('video');
        if (img) {
          img.src = e.target.result;
          preview.classList.add('visible');
        }
      }

      // Update box label
      const title = box.querySelector('.upload-title');
      const subtitle = box.querySelector('.upload-subtitle');
      if (title)    title.textContent = file.name;
      if (subtitle) subtitle.textContent = formatBytes(file.size) + ' — click to change';
    };

    if (file.type.startsWith('video/')) {
      reader.readAsDataURL(file);
    } else {
      reader.readAsDataURL(file);
    }
  }

  function resetUpload(box, input, preview) {
    input.value = '';
    if (preview) preview.classList.remove('visible');
    const title = box.querySelector('.upload-title');
    const subtitle = box.querySelector('.upload-subtitle');
    if (title)    title.textContent = 'Drag & Drop or Click to Upload';
    if (subtitle) subtitle.textContent = 'Supports PNG, JPG, JPEG, WEBP formats';
  }

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  // ── Character Counter ──────────────────────────────────── //
  function initCharCounter(textareaSelector, counterSelector, max) {
    const textarea = document.querySelector(textareaSelector);
    const counter  = document.querySelector(counterSelector);
    if (!textarea || !counter) return;

    function update() {
      const len = textarea.value.length;
      counter.textContent = max ? `${len} / ${max}` : len + ' characters';
      if (max && len > max * 0.9) counter.style.color = 'var(--warning)';
      else counter.style.color = '';
    }

    textarea.addEventListener('input', update);
    update();
  }

  // Word Counter
  function initWordCounter(textareaSelector, counterSelector) {
    const textarea = document.querySelector(textareaSelector);
    const counter  = document.querySelector(counterSelector);
    if (!textarea || !counter) return;

    function update() {
      const words = textarea.value.trim().split(/\s+/).filter(w => w.length > 0);
      counter.textContent = words.length + ' words';
    }

    textarea.addEventListener('input', update);
    update();
  }

  // ── Form Submit Loading ────────────────────────────────── //
  function initSubmitLoading(formSelector, btnSelector) {
    const form = document.querySelector(formSelector);
    const btn  = document.querySelector(btnSelector);
    if (!form || !btn) return;

    form.addEventListener('submit', (e) => {
      // Validate file uploaded
      const fileInput = form.querySelector('input[type="file"]');
      if (fileInput && !fileInput.files.length) {
        e.preventDefault();
        showToast('Please upload a file first.', 'error');
        return;
      }
      btn.classList.add('loading');
      btn.disabled = true;
      btn.textContent = 'Analyzing...';
    });
  }

  // ── Toast Notifications ────────────────────────────────── //
  window.showToast = function(message, type = 'info', duration = 4000) {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      document.body.appendChild(container);
    }

    const icons = {
      success: '<svg viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></svg>',
      error:   '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
      info:    '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${icons[type] || icons.info}</span>
      <span class="toast-message">${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.animation = 'toastSlideOut 0.3s ease forwards';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  };

  // ── Init on DOM ready ──────────────────────────────────── //
  document.addEventListener('DOMContentLoaded', () => {
    // Image check page
    initUploadBox('#image-upload-box', '#image-input', '#image-preview');

    // Form submissions
    initSubmitLoading('#check-form', '#submit-btn');
    initSubmitLoading('#text-check-form', '#submit-btn');
  });

})();
