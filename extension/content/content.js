/* ============================================================
   FED-SPA content.js - runs on the FL DOH MQA portal.
   Purpose: when you're doing manual verification on the state
   site, this script highlights establishments that are already
   in the FED-SPA list, and marks FED-SPA-flagged (unlicensed)
   businesses with a red ribbon if they appear in search results.

   It reads packaged data ONLY (no messaging needed):
     chrome.runtime.getURL('data/licensed.json')
     chrome.runtime.getURL('data/unlicensed.encrypted.json')
   The unlicensed tier is skipped unless the user saved a code
   in options (rememberCode) - decrypting happens right here,
   in-page, with Web Crypto. Nothing is sent anywhere.
   ============================================================ */

(async function () {
  'use strict';

  const MARK = 'fedspa-mark';

  async function loadJson(path) {
    try {
      const res = await fetch(chrome.runtime.getURL(path));
      return res.ok ? res.json() : null;
    } catch (err) {
      return null;
    }
  }

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

  function tag(el, text, kind) {
    if (el.querySelector('.' + MARK)) return;
    const badge = document.createElement('span');
    badge.className = MARK + ' ' + (kind === 'unlicensed' ? 'fedspa-bad' : 'fedspa-good');
    badge.textContent = text;
    badge.title = 'FED-SPA: ' + text;
    el.appendChild(badge);
  }

  async function main() {
    const licensedDoc = await loadJson('data/licensed.json');
    if (!licensedDoc) return;

    const licensedNames = new Map();
    (licensedDoc.parlors || []).forEach((p) => {
      licensedNames.set(String(p.business_name || '').toLowerCase(), p);
    });

    // Optionally decrypt the unlicensed tier.
    let unlicensedNames = new Set();
    const settings = await new Promise((resolve) =>
      chrome.storage.local.get({ rememberCode: false, savedCode: '' }, resolve));
    if (settings.rememberCode && settings.savedCode) {
      const envelope = await loadJson('data/unlicensed.encrypted.json');
      if (envelope && envelope.data) {
        try {
          const doc = await decrypt(envelope, settings.savedCode);
          (doc.parlors || []).forEach((u) =>
            unlicensedNames.add(String(u.business_name || '').toLowerCase()));
        } catch (err) { /* stale saved code; ignore */ }
      }
    }

    // The portal renders results in tables - scan rows generically.
    const scan = () => {
      document.querySelectorAll('tr, .result-row, li').forEach((row) => {
        const text = (row.textContent || '').toLowerCase();
        if (!text || text.length > 600) return;   // skip giant containers
        licensedNames.forEach((p, name) => {
          if (text.includes(name) && !row.textContent.includes('FED-SPA:')) {
            tag(row, 'FED-SPA: verified licensed', 'licensed');
          }
        });
        unlicensedNames.forEach((name) => {
          if (text.includes(name) && !row.textContent.includes('FED-SPA:')) {
            tag(row, 'FED-SPA: on unlicensed watchlist', 'unlicensed');
          }
        });
      });
    };

    scan();
    // Re-scan when the portal re-renders (it posts back on search).
    const observer = new MutationObserver(() => scan());
    observer.observe(document.body, { childList: true, subtree: true });
  }

  main();
})();
