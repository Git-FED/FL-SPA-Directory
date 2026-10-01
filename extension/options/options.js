/* ==========================================================================
   FED-SPA extension options
   ---------------------------------------------------------------------------
   Small settings surface:
     1. Data status  -> asks the background service worker for the bundled
                        data version (GET_DATA_VERSION message).
     2. Subscriber code handling:
          rememberCode  (bool)   opt-in flag
          savedCode     (string) the actual code, only stored when the user
                                 opted in. Cleared instantly when the flag
                                 is switched off.
   Storage: chrome.storage.local - never synced, never sent anywhere.
   ========================================================================== */

'use strict';

(function () {

  const $ = (id) => document.getElementById(id);

  const els = {
    licCount: $('licCount'),
    asOf: $('asOf'),
    version: $('version'),
    rememberCode: $('rememberCode'),
    codeInput: $('codeInput'),
    saveBtn: $('saveBtn'),
    clearBtn: $('clearBtn'),
    statusMsg: $('statusMsg'),
  };

  // ------------------------------------------------------------------
  // status line helper
  // ------------------------------------------------------------------
  let statusTimer = null;

  function setStatus(msg, isError) {
    els.statusMsg.textContent = msg;
    els.statusMsg.classList.toggle('err', Boolean(isError));
    clearTimeout(statusTimer);
    statusTimer = setTimeout(() => {
      els.statusMsg.textContent = '';
    }, 4000);
  }

  // ------------------------------------------------------------------
  // load current settings + data version into the form
  // ------------------------------------------------------------------
  async function loadSettings() {
    const settings = await new Promise((resolve) =>
      chrome.storage.local.get({ rememberCode: false, savedCode: '' }, resolve));

    els.rememberCode.checked = settings.rememberCode;
    // Show a masked hint instead of echoing the actual code back.
    if (settings.savedCode) {
      els.codeInput.placeholder = 'Saved code: ' + '\u2022'.repeat(Math.min(24, settings.savedCode.length));
    }
  }

  async function loadDataVersion() {
    let info = null;
    try {
      info = await new Promise((resolve, reject) => {
        chrome.runtime.sendMessage({ type: 'GET_DATA_VERSION' }, (resp) => {
          if (chrome.runtime.lastError) reject(chrome.runtime.lastError);
          else resolve(resp);
        });
      });
    } catch (e) {
      // background unavailable (e.g. service worker asleep) - leave placeholders
    }
    if (info && info.count != null) els.licCount.textContent = info.count;
    if (info && info.asOf) els.asOf.textContent = info.asOf;
    if (info && info.version != null) els.version.textContent = 'v' + info.version;
  }

  // ------------------------------------------------------------------
  // save / clear
  // ------------------------------------------------------------------
  function save() {
    const remember = els.rememberCode.checked;
    const code = els.codeInput.value.trim();

    if (remember && !code && !hasSavedCode()) {
      setStatus('Enter a subscriber code first, or turn off "Remember my code".', true);
      return;
    }

    chrome.storage.local.set(
      { rememberCode: remember, savedCode: remember ? code : '' },
      () => {
        if (chrome.runtime.lastError) {
          setStatus('Could not save: ' + chrome.runtime.lastError.message, true);
          return;
        }
        els.codeInput.value = '';
        loadSettings();
        if (remember) setStatus('Saved. The popup and portal page enhancer will unlock automatically.');
        else setStatus('Remember-me is off. Stored code wiped.');
      }
    );
  }

  function clearStored() {
    chrome.storage.local.remove(['rememberCode', 'savedCode'], () => {
      els.rememberCode.checked = false;
      els.codeInput.value = '';
      els.codeInput.placeholder = 'Paste your subscriber code';
      setStatus('Cleared. Nothing is stored anymore.');
    });
  }

  // hasSavedCode: whether a code already lives in storage (so "save" with an
  // empty input is legitimate when just toggling the checkbox off).
  let savedCodePresent = false;

  function hasSavedCode() {
    return savedCodePresent;
  }

  function refreshSavedFlag() {
    return new Promise((resolve) =>
      chrome.storage.local.get('savedCode', (r) => {
        savedCodePresent = Boolean(r && r.savedCode);
        resolve(savedCodePresent);
      }));
  }

  // ------------------------------------------------------------------
  // wire up
  // ------------------------------------------------------------------
  loadSettings();
  loadDataVersion();
  refreshSavedFlag();

  els.saveBtn.addEventListener('click', () => { refreshSavedFlag().then(save); });
  els.clearBtn.addEventListener('click', clearStored);

  els.rememberCode.addEventListener('change', () => {
    // unchecking wipes instantly - no "save" round-trip required
    if (!els.rememberCode.checked) {
      chrome.storage.local.remove(['rememberCode', 'savedCode'], () => {
        setStatus('Remember-me off. Stored code wiped.');
      });
    }
  });

})();
