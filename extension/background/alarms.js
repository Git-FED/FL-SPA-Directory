/* ============================================================
   FED-SPA alarms.js - schedule definitions for background.js.
   Data ships annually, so:
     - ANNUAL_REFRESH: yearly tick that re-reads packaged data
       and re-syncs the badge (fires on install/startup too).
     - WEEKLY_NUDGE:   lightweight badge re-check; also the
       natural place to add "data as of X" notifications later.
   Alarms survive browser restarts (that's the point of the
   chrome.alarms permission).
   ============================================================ */

const FedSpaAlarms = (() => {
  const ANNUAL_REFRESH = 'fedspa-annual-refresh';
  const WEEKLY_NUDGE = 'fedspa-weekly-nudge';

  async function schedule() {
    // Clear then re-create so changes to this file take effect.
    await chrome.alarms.clearAll();

    await chrome.alarms.create(ANNUAL_REFRESH, {
      delayInMinutes: 60,
      periodInMinutes: 60 * 24 * 365   // once a year
    });

    await chrome.alarms.create(WEEKLY_NUDGE, {
      delayInMinutes: 30,
      periodInMinutes: 60 * 24 * 7     // once a week
    });
  }

  return { ANNUAL_REFRESH, WEEKLY_NUDGE, schedule };
})();
