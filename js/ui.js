/* ============================================================
   FED-SPA ui.js - DOM rendering helpers.
   No framework, no build step. Consumed by app.js / search.js.
   Exposes a small global namespace: FedSpaUI.
   ============================================================ */

(function () {
  'use strict';

  const STATUS_CLASSES = {
    clear: 'status-clear',
    active: 'status-active',
    delinquent: 'status-delinquent',
    expired: 'status-expired',
    inactive: 'status-inactive',
    probation: 'status-probation',
    flag: 'status-flag'
  };

  const UNLICENSED_LABELS = {
    no_license_found: 'NO LICENSE FOUND',
    expired: 'EXPIRED',
    inactive: 'INACTIVE',
    revoked: 'REVOKED',
    delinquent: 'DELINQUENT'
  };

  /** ISO date -> "Aug 31, 2027" (or the raw string if unparseable). */
  function prettyDate(iso) {
    if (!iso) return '-';
    const d = new Date(iso + 'T00:00:00');
    if (isNaN(d)) return iso;
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  }

  /** Days from today until an ISO date (negative = past). */
  function daysUntil(iso) {
    if (!iso) return Infinity;
    const then = new Date(iso + 'T00:00:00');
    if (isNaN(then)) return Infinity;
    return Math.floor((then - new Date()) / 86400000);
  }

  function esc(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function statusBadge(status, extraClass) {
    const key = String(status || '').toLowerCase().replace(/[^a-z]/g, '');
    const cls = STATUS_CLASSES[key] || 'status-flag';
    const label = String(status || 'UNKNOWN').toUpperCase();
    return '<span class="status-badge ' + cls + (extraClass ? ' ' + extraClass : '') + '">' + esc(label) + '</span>';
  }

  function flagChip(text, tone) {
    return '<span class="chip" style="' + (tone === 'danger'
      ? 'color:var(--danger);border-color:rgba(255,95,109,.5);'
      : tone === 'warn' ? 'color:var(--warning);border-color:rgba(242,193,78,.5);' : '') +
      '">' + esc(text) + '</span>';
  }

  /** One licensed parlor -> card HTML. onClickName is a callback. */
  function parlorCard(p, onClickName) {
    const days = daysUntil(p.expiration_date);
    const expiring = days <= 180 && days >= 0;
    const expired = days < 0;

    const addr = p.address || {};
    const where = [addr.city, addr.state].filter(Boolean).join(', ');
    const street = [addr.street, addr.street2].filter(Boolean).join(' ');

    const flags = [];
    if (p.discipline_on_file) flags.push(flagChip('Discipline on file', 'danger'));
    if (p.public_complaint) flags.push(flagChip('Public complaint', 'warn'));
    if (expired) flags.push(flagChip('License expired ' + prettyDate(p.expiration_date), 'danger'));
    else if (expiring) flags.push(flagChip('Expires in ' + days + ' days', 'warn'));

    const name = esc(p.business_name);
    const clickAttr = onClickName ? ' data-open="' + esc(p.license_number) + '"' : '';

    return (
      '<li class="parlor-card">' +
        '<div class="parlor-top">' +
          '<div>' +
            '<button type="button" class="parlor-name"' + clickAttr + '>' + name + '</button>' +
            '<p class="parlor-sub">' + esc(street) + (street && where ? ' &middot; ' : '') +
              esc(where) + (p.county ? ' &middot; ' + esc(p.county) + ' County' : '') + '</p>' +
          '</div>' +
          statusBadge(p.status) +
        '</div>' +
        (flags.length ? '<div class="parlor-flags">' + flags.join('') + '</div>' : '') +
        '<p class="license-line">' + esc(p.license_number) +
          ' &middot; exp ' + esc(prettyDate(p.expiration_date)) + '</p>' +
      '</li>'
    );
  }

  /** One unlicensed parlor -> card HTML (subscriber tier). */
  function unlicensedCard(u) {
    const addr = u.address || {};
    const where = [addr.street, [addr.city, addr.state, addr.zip].filter(Boolean).join(' ')]
      .filter(Boolean).join(', ');
    const label = UNLICENSED_LABELS[u.status] || String(u.status || 'FLAGGED').toUpperCase();
    return (
      '<li class="parlor-card unlicensed">' +
        '<div class="parlor-top">' +
          '<div>' +
            '<span class="parlor-name" style="cursor:default">' + esc(u.business_name) + '</span>' +
            '<p class="parlor-sub">' + esc(where) + '</p>' +
          '</div>' +
          '<span class="status-badge status-flag">' + esc(label) + '</span>' +
        '</div>' +
        '<p class="parlor-sub small" style="margin-top:8px">' + esc(u.reason || '') + '</p>' +
        (u.license_number_last_known
          ? '<p class="license-line">last known: ' + esc(u.license_number_last_known) + '</p>' : '') +
        '<p class="license-line">checked ' + esc(prettyDate(u.last_checked)) + '</p>' +
      '</li>'
    );
  }

  /** Full detail table for the modal. */
  function detailHtml(p) {
    const addr = p.address || {};
    const full = [addr.street, addr.street2, addr.city, addr.state, addr.zip]
      .filter(Boolean).join(' ');
    const rows = [
      ['License #', esc(p.license_number)],
      ['Profession', esc(p.profession)],
      ['Status', statusBadge(p.status)],
      ['Expiration', esc(prettyDate(p.expiration_date))],
      ['Originally issued', esc(prettyDate(p.original_issue_date))],
      ['County', esc(p.county || '-')],
      ['Address', esc(full || '-')],
      ['Discipline on file', p.discipline_on_file ? 'Yes' : 'No'],
      ['Public complaint', p.public_complaint ? 'Yes' : 'No'],
      ['Data as of', esc(prettyDate(p.data_as_of))],
      ['Last checked', esc(prettyDate(p.last_checked))]
    ];
    let html = '<dl class="detail-grid">';
    rows.forEach(function (r) { html += '<dt>' + r[0] + '</dt><dd>' + r[1] + '</dd>'; });
    html += '</dl>';
    if (p.notes) {
      html += '<div class="modal-section"><strong>Notes</strong><br>' + esc(p.notes) + '</div>';
    }
    html += '<div class="modal-section">Verify directly on the Florida DOH MQA portal:<br>' +
      '<a href="https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders" ' +
      'target="_blank" rel="noopener noreferrer">mqa-internet.doh.state.fl.us</a></div>';
    return html;
  }

  function emptyState(message) {
    return '<li class="empty-state">' + esc(message) + '</li>';
  }

  function errorBox(message) {
    const el = document.getElementById('errorBox');
    if (!el) return;
    el.textContent = message;
    el.classList.remove('hidden');
  }

  function clearError() {
    const el = document.getElementById('errorBox');
    if (el) { el.textContent = ''; el.classList.add('hidden'); }
  }

  window.FedSpaUI = {
    prettyDate: prettyDate,
    daysUntil: daysUntil,
    esc: esc,
    statusBadge: statusBadge,
    parlorCard: parlorCard,
    unlicensedCard: unlicensedCard,
    detailHtml: detailHtml,
    emptyState: emptyState,
    errorBox: errorBox,
    clearError: clearError
  };
})();
