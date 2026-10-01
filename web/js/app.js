/* ============================================================
   FED-SPA app.js - bootstrap & state.
   Loads ./data/licensed.json and ./data/unlicensed.encrypted.json,
   renders the public list, wires search/filter/modal, and handles
   the subscriber unlock flow. The access code is kept in
   sessionStorage only (cleared when the tab closes).
   ============================================================ */

(function () {
  'use strict';

  const UI = window.FedSpaUI;
  const SEARCH = window.FedSpaSearch;
  const CRYPTO = window.FedSpaCrypto;

  const state = {
    licensed: [],
    envelope: null,      // encrypted subscriber blob
    unlicensed: null,    // decrypted list (null until unlocked)
    unlocked: false,
    allExpanded: false
  };

  const $ = function (id) { return document.getElementById(id); };

  /* ---------------- data loading ---------------- */

  async function loadJson(url) {
    const res = await fetch(url, { cache: 'no-cache' });
    if (!res.ok) throw new Error(url + ' -> HTTP ' + res.status);
    return res.json();
  }

  async function loadData() {
    try {
      const doc = await loadJson('data/licensed.json');
      state.licensed = (doc.parlors || []).slice().sort(SEARCH.byName);
      $('dataAsOf').textContent = 'Data as of ' + UI.prettyDate(doc.as_of);
      $('dataCount').textContent = state.licensed.length + ' verified';
    } catch (err) {
      UI.errorBox('Could not load the licensed list (' + err.message +
        '). If you are offline, reopen the installed app to see cached data.');
      state.licensed = [];
    }

    try {
      state.envelope = await loadJson('data/unlicensed.encrypted.json');
    } catch (err) {
      state.envelope = null;
    }
  }

  /* ---------------- rendering ---------------- */

  function renderList() {
    const list = $('parlorList');
    const query = $('searchInput').value;
    const status = $('statusFilter').value;
    const results = SEARCH.filterLicensed(state.licensed, query, status);

    if (!state.licensed.length) {
      list.innerHTML = UI.emptyState('No licensed data loaded.');
    } else if (!results.length) {
      list.innerHTML = UI.emptyState('No matches for "' + UI.esc(query) + '".');
    } else {
      list.innerHTML = results.map(function (p) { return UI.parlorCard(p, true); }).join('');
    }
    const locations = new Set(results.map(function (p) {
      const a = p.address || {};
      return [a.city, a.state].filter(Boolean).join(', ') || 'Unknown location';
    }));
    $('resultCount').textContent =
      results.length + ' of ' + state.licensed.length + ' establishments · ' +
      locations.size + ' location' + (locations.size === 1 ? '' : 's');
  }

  function renderUnlicensed() {
    if (!state.unlocked || !state.unlicensed) return;
    const list = $('unlicensedList');
    const entries = (state.unlicensed.parlors || []).slice().sort(SEARCH.byName);
    $('unlicensedCount').textContent = entries.length + ' flagged';

    if (!entries.length) {
      list.innerHTML = UI.emptyState('Watchlist is empty in this snapshot.');
    } else {
      list.innerHTML = entries.map(UI.unlicensedCard).join('');
    }
  }

  /* ---------------- modal ---------------- */

  function openDetail(licenseNumber) {
    const p = state.licensed.find(function (x) { return x.license_number === licenseNumber; });
    if (!p) return;
    $('modalTitle').textContent = p.business_name;
    $('modalBody').innerHTML = UI.detailHtml(p);
    $('detailModal').showModal();
  }

  /* ---------------- subscriber flow ---------------- */

  function subscriberUiState() {
    const hasBlob = !!(state.envelope && state.envelope.data);
    const form = $('unlockForm');
    const panel = $('unlicensedPanel');
    const notice = $('subscriberNotice');

    if (state.unlocked) {
      form.hidden = true;
      panel.hidden = false;
      notice.hidden = true;
      renderUnlicensed();
    } else if (hasBlob) {
      form.hidden = false;
      panel.hidden = true;
      notice.hidden = true;
    } else {
      form.hidden = true;
      panel.hidden = true;
      notice.hidden = false;
    }
  }

  async function unlock() {
    const pw = $('passwordInput').value;
    const msg = $('unlockMsg');
    const btn = $('unlockButton');
    if (!pw) { msg.textContent = 'Enter your access code first.'; return; }

    btn.disabled = true;
    msg.textContent = 'Decrypting on this device...';
    try {
      state.unlicensed = await CRYPTO.decryptList(state.envelope, pw);
      state.unlocked = true;
      try { sessionStorage.setItem('fedspa_pw', pw); } catch (e) { /* private mode */ }
      msg.textContent = '';
      $('passwordInput').value = '';
      subscriberUiState();
    } catch (err) {
      state.unlocked = false;
      state.unlicensed = null;
      msg.textContent = 'Wrong code (or the blob is corrupt) - decryption failed.';
    } finally {
      btn.disabled = false;
    }
  }

  function lock() {
    state.unlocked = false;
    state.unlicensed = null;
    try { sessionStorage.removeItem('fedspa_pw'); } catch (e) { /* ignore */ }
    subscriberUiState();
  }

  /* ---------------- wiring ---------------- */

  function wire() {
    $('searchInput').addEventListener('input', renderList);
    $('statusFilter').addEventListener('change', renderList);
    $('expandAll').addEventListener('click', function () {
      // This is a reset/browse action, not a second data source: the public
      // snapshot is rendered from every record in data/licensed.json.
      $('searchInput').value = '';
      $('statusFilter').value = 'all';
      renderList();
      $('parlorList').scrollIntoView({ behavior: 'smooth', block: 'start' });
      this.textContent = 'Showing all records';
    });
    $('unlicensedSearch').addEventListener('input', function () {
      if (!state.unlicensed) return;
      const q = this.value;
      const list = $('unlicensedList');
      const entries = SEARCH.filterUnlicensed(state.unlicensed.parlors || [], q)
        .sort(SEARCH.byName);
      list.innerHTML = entries.length
        ? entries.map(UI.unlicensedCard).join('')
        : UI.emptyState('No matches.');
    });

    $('parlorList').addEventListener('click', function (ev) {
      const btn = ev.target.closest('.parlor-name[data-open]');
      if (btn) openDetail(btn.getAttribute('data-open'));
    });

    $('modalClose').addEventListener('click', function () { $('detailModal').close(); });
    $('detailModal').addEventListener('click', function (ev) {
      if (ev.target === this) this.close();  // backdrop click
    });

    $('unlockButton').addEventListener('click', unlock);
    $('passwordInput').addEventListener('keydown', function (ev) {
      if (ev.key === 'Enter') unlock();
    });
    $('lockButton').addEventListener('click', lock);

    $('year').textContent = new Date().getFullYear();
  }

  /* ---------------- boot ---------------- */

  async function boot() {
    wire();
    if ('serviceWorker' in navigator && location.protocol !== 'file:') {
      try {
        navigator.serviceWorker.register('js/service-worker.js');
      } catch (e) { /* offline install still works without SW */ }
    }
    await loadData();
    renderList();
    subscriberUiState();

    // Silent re-unlock if the tab was reloaded mid-session.
    const saved = sessionStorage.getItem('fedspa_pw');
    if (saved && state.envelope && state.envelope.data) {
      try {
        state.unlicensed = await CRYPTO.decryptList(state.envelope, saved);
        state.unlocked = true;
        subscriberUiState();
      } catch (err) { sessionStorage.removeItem('fedspa_pw'); }
    }
  }

  document.addEventListener('DOMContentLoaded', boot);
})();
