/* ============================================================
   FED-SPA background service worker (Manifest V3).
   Responsibilities:
     - Badge: count of licensed establishments (set on install
       and on alarm refresh; cleared if data can't be read).
     - Alarms: schedule the annual data refresh reminder and a
       weekly nudge (see alarms.js for cadence).
     - Message router: popup <-> options messaging.
   No network calls to third parties; only packaged data is read.
   ============================================================ */

importScripts('alarms.js');

const BADGE_COLOR = '#2dd4a7';

async function readLicensed() {
  try {
    const res = await fetch(chrome.runtime.getURL('data/licensed.json'));
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    return null;
  }
}

async function updateBadge() {
  const doc = await readLicensed();
  const count = doc && Array.isArray(doc.parlors) ? doc.parlors.length : 0;
  try {
    await chrome.action.setBadgeBackgroundColor({ color: BADGE_COLOR });
    if (count > 0) {
      await chrome.action.setBadgeText({ text: String(count) });
    } else {
      await chrome.action.setBadgeText({ text: '' });
    }
  } catch (err) {
    /* action API unavailable in some contexts; ignore */
  }
}

chrome.runtime.onInstalled.addListener(async (details) => {
  await FedSpaAlarms.schedule();
  await updateBadge();
  if (details.reason === 'install') {
    // First run: nothing noisy - badge count is the welcome signal.
  }
});

chrome.runtime.onStartup.addListener(async () => {
  await FedSpaAlarms.schedule();
  await updateBadge();
});

// Fired when alarms.js says it's time to remind/refresh.
chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === FedSpaAlarms.ANNUAL_REFRESH) {
    await updateBadge();
    // Version-keyed data ships with extension updates; a new
    // release is how the annual refresh reaches users.
  } else if (alarm.name === FedSpaAlarms.WEEKLY_NUDGE) {
    await updateBadge();
  }
});

// Simple message router for popup/options.
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg && msg.type === 'GET_DATA_VERSION') {
    readLicensed().then((doc) => sendResponse({ as_of: doc ? doc.as_of : null }));
    return true; // async response
  }
  if (msg && msg.type === 'BADGE_REFRESH') {
    updateBadge().then(() => sendResponse({ ok: true }));
    return true;
  }
});
