/* No network, storage, framework or remote dependencies. */
(() => {
  'use strict';
  const slides = Array.from(document.querySelectorAll('.slide'));
  if (!slides.length) return;
  const byId = new Map(slides.map((slide, i) => [slide.id, i]));
  const get = id => document.getElementById(id);
  const controls = document.querySelector('.controls');
  const overview = get('overview-dialog');
  const notePanel = get('notes-panel');
  let index = 0;
  let noticeTimer;

  function hashIndex() {
    try { return byId.get(decodeURIComponent(location.hash.slice(1))) ?? 0; }
    catch (_) { return 0; }
  }

  function show(requested, updateHash = true) {
    index = Math.max(0, Math.min(slides.length - 1, requested));
    slides.forEach((slide, i) => {
      slide.hidden = i !== index;
      slide.setAttribute('aria-hidden', String(i !== index));
    });
    const slide = slides[index];
    get('counter').textContent = `${index + 1} / ${slides.length}`;
    get('prev').disabled = index === 0;
    get('next').disabled = index === slides.length - 1;
    get('progress').style.width = `${(index + 1) / slides.length * 100}%`;
    get('note-content').innerHTML = slide.querySelector('.speaker-notes').innerHTML;
    overview.querySelectorAll('[data-slide]').forEach(button => {
      button.setAttribute('aria-current', String(button.dataset.slide === slide.id));
    });
    document.title = `${slide.querySelector('h1').innerText.replace(/\s+/g, ' ')} · Shift Happens · DEVK`;
    if (updateHash) {
      // Works on file:// too; failure must not prevent navigation.
      try { history.replaceState(null, '', `#${encodeURIComponent(slide.id)}`); }
      catch (_) { location.hash = slide.id; }
    }
  }

  function fit() {
    const deck = get('deck');
    const scale = Math.min(deck.clientWidth / 1600, deck.clientHeight / 900);
    document.documentElement.style.setProperty('--scale', String(Math.max(.01, scale)));
  }

  function notes(open = notePanel.hidden) {
    notePanel.hidden = !open;
    get('notes').setAttribute('aria-expanded', String(open));
    if (open) get('close-notes').focus();
    else get('notes').focus();
  }

  function notify(message) {
    get('notice').textContent = message;
    get('notice').hidden = false;
    clearTimeout(noticeTimer);
    noticeTimer = setTimeout(() => { get('notice').hidden = true; }, 6000);
  }

  async function fullscreen() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else if (document.documentElement.requestFullscreen) await document.documentElement.requestFullscreen();
      else notify('Vollbild wird hier nicht unterstützt. Bitte die Vollbildfunktion des Browsers verwenden.');
    } catch (_) { notify('Vollbild konnte nicht gestartet werden. Bitte die Vollbildfunktion des Browsers verwenden.'); }
  }

  get('prev').addEventListener('click', () => show(index - 1));
  get('next').addEventListener('click', () => show(index + 1));
  get('notes').addEventListener('click', () => notes());
  get('close-notes').addEventListener('click', () => notes(false));
  get('fullscreen').addEventListener('click', fullscreen);
  get('print').addEventListener('click', () => window.print());
  get('overview').addEventListener('click', () => overview.showModal());
  get('close-overview').addEventListener('click', () => overview.close());
  overview.querySelectorAll('[data-slide]').forEach(button => {
    button.addEventListener('click', () => { show(byId.get(button.dataset.slide)); overview.close(); });
  });
  window.addEventListener('hashchange', () => show(hashIndex(), false));
  window.addEventListener('resize', fit);
  document.addEventListener('fullscreenchange', () => {
    const active = Boolean(document.fullscreenElement);
    const button = get('fullscreen');
    button.setAttribute('aria-pressed', String(active));
    if (active && document.activeElement === button) get('deck').focus();
    fit();
  });
  document.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.isComposing) return;
    if (overview.open) return; // Native dialog handles focus and Escape.
    if (event.target.closest('input,textarea,select,[contenteditable="true"]')) return;
    const key = event.key.toLowerCase();
    if (key === 'escape' && !notePanel.hidden) { notes(false); event.preventDefault(); return; }
    // Keep native Space/Enter activation on focused controls.
    if (event.target.closest('button,a') && (key === ' ' || key === 'enter')) return;
    const handlers = {
      arrowright: () => show(index + 1), pagedown: () => show(index + 1), ' ': () => show(index + 1),
      arrowleft: () => show(index - 1), pageup: () => show(index - 1),
      home: () => show(0), end: () => show(slides.length - 1),
      n: () => notes(), o: () => overview.showModal(), f: fullscreen
    };
    if (Object.hasOwn(handlers, key)) { event.preventDefault(); handlers[key](); }
  });
  let touchStart = null;
  get('deck').addEventListener('touchstart', event => {
    if (event.touches.length !== 1 || event.target.closest('a,button')) return;
    touchStart = { x: event.touches[0].clientX, y: event.touches[0].clientY };
  }, { passive: true });
  get('deck').addEventListener('touchend', event => {
    if (!touchStart || !event.changedTouches.length) return;
    const dx = event.changedTouches[0].clientX - touchStart.x;
    const dy = event.changedTouches[0].clientY - touchStart.y;
    if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) show(index + (dx < 0 ? 1 : -1));
    touchStart = null;
  }, { passive: true });
  get('deck').addEventListener('touchcancel', () => { touchStart = null; }, { passive: true });

  // Only activate single-slide mode after every control has been initialized.
  document.documentElement.classList.add('enhanced');
  controls.hidden = false;
  show(hashIndex(), false);
  fit();
})();
