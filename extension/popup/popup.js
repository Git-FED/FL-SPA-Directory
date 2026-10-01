/* ============================================================
   FED-SPA popup.js - self-contained popup app.
   Loads ../data/licensed.json + ../data/unlicensed.encrypted.json
   (packaged copies), renders both tiers, handles the subscriber
   unlock. Access code persists via chrome.storage if the user
   chose "remember" in options.
   ============================================================ */

(function () {
  'use strict';

  const $ = (id) => document.getElementById(id);
  const esc = (v) => String(v == null ? '' : v)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');

  const state = {
    licensed: [],
    envelope: null,
    unlicensed: null,
    unlocked: false,
    tier: 'licensed'
  };

  /* ---------------- storage helpers ---------------- */

  function getSettings() {
    return new Promise((resolve) => {
      chrome.storage.local.get({ rememberCode: false, savedCode: '' }, resolve);
    });
  }

  /* ---------------- data ---------------- */

  async function loadJson(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return res.json();
  }

  async function loadData() {
    try {
      const doc = await loadJson('../data/licensed.json');
      state.licensed = (doc.parlors || []).slice()
        .sort((a, b) => (a.business_name || '').localeCompare(b.business_name || ''));
      $('dataAsOf').textContent = 'data as of ' + (doc.as_of || '-');
      $('emptyMsg').hidden = true;
    } catch (err) {
      $('emptyMsg').textContent = 'Failed to load packaged data.';
    }
    try {
      state.envelope = await loadJson('../data/unlicensed.encrypted.json');
    } catch (err) {
      state.envelope = null;
    }
  }

  /* ---------------- rendering ---------------- */

  function badge(status) {
    const key = String(status || '').toLowerCase().replace(/[^a-z]/g, '');
    return '<span class="badge ' + (key || 'flag') + '">' + esc(String(status || '?').toUpperCase()) + '</span>';
  }

  function licensedCard(p) {
    const a = p.address || {};
    const where = [a.city, a.state].filter(Boolean).join(', ');
    return (
      '<li class="card">' +
        '<div class="card-top">' +
          '<div>' +
            '<p class="card-name">' + esc(p.business_name) + '</p>' +
            '<p class="card-sub">' + esc(a.street || '') + (a.street && where ? ' · ' : '') +
              esc(where) + (p.county ? ' · ' + esc(p.county) : '') + '</p>' +
          '</div>' +
          badge(p.status) +
        '</div>' +
        '<p class="lic-line">' + esc(p.license_number) + ' · exp ' + esc(p.expiration_date) + '</p>' +
      '</li>'
    );
  }

  function unlicensedCard(u) {
    const a = u.address || {};
    const where = [a.street, [a.city, a.state, a.zip].filter(Boolean).join(' ')]
      .filter(Boolean).join(', ');
    return (
      '<li class="card unlicensed">' +
        '<div class="card-top">' +
          '<div>' +
            '<p class="card-name">' + esc(u.business_name) + '</p>' +
            '<p class="card-sub">' + esc(where) + '</p>' +
          '</div>' +
          '<span class="badge flag">' + esc(String(u.status || 'FLAGGED').toUpperCase()) + '</span>' +
        '</div>' +
        '<p class="card-sub" style="margin-top:6px">' + esc(u.reason || '') + '</p>' +
      '</li>'
    );
  }

  function render() {
    const list = $('parlorList');
    const q = $('searchInput').value.toLowerCase().trim();
    const status = $('statusFilter').value;

    const terms = q ? q.split(/\s+/) : [];
    const matches = (p) => {
      const hay = [
        p.business_name, p.license_number, p.status,
        p.address && p.address.street, p.address && p.address.city,
        p.address && p.address.zip, p.county
      ].filter(Boolean).join(' ').toLowerCase();
      return terms.every((t) => hay.includes(t));
    };

    let items, cards;
    if (state.tier === 'unlicensed' && state.unlocked && state.unlicensed) {
      items = (state.unlicensed.parlors || []).filter(matches);
      cards = items.map(unlicensedCard).join('');
      $('statusFilter').hidden = true;
    } else {
      items = state.licensed.filter((p) =>
        (status === 'all' || p.status === status) && matches(p));
      cards = items.map(licensedCard).join('');
      $('statusFilter').hidden = false;
    }

    list.innerHTML = cards || '';
    $('emptyMsg').hidden = cards.length > 0;
    if (!cards.length) {
      $('emptyMsg').textContent = state.tier === 'unlicensed'
        ? 'No watchlist matches.'
        : 'No matches. Try fewer words.';
    }

    // Tier tabs only exist when a real blob is packaged.
    const hasBlob = !!(state.envelope && state.envelope.data);
    $('tierTabs').hidden = !hasBlob;
    if (hasBlob) {
      $('tabUnlicensed').innerHTML = 'Unlicensed ' +
        (state.unlocked ? '' : '<span class="lock">&#128274;</span>');
      $('tabUnlicensed').classList.toggle('active', state.tier === 'unlicensed');
      $('tabLicensed').classList.toggle('active', state.tier === 'licensed');
    }
    $('unlockBox').hidden = !(state.tier === 'unlicensed' && !state.unlocked && hasBlob);
  }

  /* ---------------- crypto (Web Crypto, same envelope as web) ---------------- */

  function b64ToBytes(b64) {
    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return bytes;
  }

  async function decrypt(envelope, password) {
    const enc = new TextEncoder();
    const baseKey = await crypto.subtle.importKey('raw', enc.encode(password), 'PBKDF2', false, ['deriveKey']);
    const key = await crypto.subtle.deriveKey(
      { name: 'PBKDF2', salt: b64ToBytes(envelope.salt), iterations: envelope.iterations || 310000, hash: 'SHA-256' },
      baseKey, { name: 'AES-GCM', length: 256 }, false, ['decrypt']
    );
    const plain = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: b64ToBytes(envelope.iv) }, key, b64ToBytes(envelope.data)
    );
    return JSON.parse(new TextDecoder().decode(plain));
  }

  async function unlock() {
    const pw = $('passwordInput').value;
    const msg = $('unlockMsg');
    if (!pw) { msg.textContent = 'Enter your access code.'; return; }
    try {
      state.unlicensed = await decrypt(state.envelope, pw);
      state.unlocked = true;
      msg.textContent = '';
      $('passwordInput').value = '';
      const settings = await getSettings();
      if (settings.rememberCode) {
        chrome.storage.local.set({ savedCode: pw });
      }
      render();
    } catch (err) {
      state.unlocked = false;
      msg.textContent = 'Wrong code - decryption failed.';
    }
  }

  /* ---------------- wiring ---------------- */

  function wire() {
    $('searchInput').addEventListener('input', render);
    $('statusFilter').addEventListener('change', render);

    $('tabLicensed').addEventListener('click', () => { state.tier = 'licensed'; render(); });
    $('tabUnlicensed').addEventListener('click', () => {
      state.tier = 'unlicensed';
      if (!state.unlocked) trySavedCode();
      render();
    });

    $('unlockBtn').addEventListener('click', unlock);
    $('passwordInput').addEventListener('keydown', (e) => { if (e.key === 'Enter') unlock(); });

    $('optionsBtn').addEventListener('click', () => {
      if (chrome.runtime.openOptionsPage) chrome.runtime.openOptionsPage();
      else chrome.tabs.create({ url: chrome.runtime.getURL('options/options.html') });
    });
  }

  async function trySavedCode() {
    const settings = await getSettings();
    if (settings.rememberCode && settings.savedCode && state.envelope && state.envelope.data) {
      try {
        state.unlicensed = await decrypt(state.envelope, settings.savedCode);
        state.unlocked = true;
      } catch (err) {
        chrome.storage.local.remove('savedCode');
      }
    }
  }

  document.addEventListener('DOMContentLoaded', async () => {
    wire();
    await loadData();
    await trySavedCode();
    render();
  });
})();
