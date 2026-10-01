/* ============================================================
   FED-SPA search.js - client-side filtering.
   Matches name, city, county, street, and license number.
   Case-insensitive; every whitespace-separated term must hit.
   Exposes FedSpaSearch.
   ============================================================ */

(function () {
  'use strict';

  function haystack(p) {
    const a = p.address || {};
    return [
      p.business_name, p.license_number, p.profession, p.status,
      a.street, a.street2, a.city, a.zip, p.county, p.notes
    ].filter(Boolean).join(' ').toLowerCase();
  }

  /** query -> predicate. Empty query matches everything. */
  function makeMatcher(query) {
    const terms = String(query || '').toLowerCase().trim().split(/\s+/).filter(Boolean);
    if (!terms.length) return function () { return true; };
    return function (p) {
      const h = haystack(p);
      return terms.every(function (t) { return h.indexOf(t) !== -1; });
    };
  }

  /** Filter licensed parlors: query text + optional status dropdown. */
  function filterLicensed(parlors, query, status) {
    const match = makeMatcher(query);
    return parlors.filter(function (p) {
      if (status && status !== 'all' && String(p.status) !== status) return false;
      return match(p);
    });
  }

  /** Filter unlicensed entries (no status dropdown, just text). */
  function filterUnlicensed(parlors, query) {
    const match = makeMatcher(query);
    return parlors.filter(match);
  }

  /** Sort: name A-Z, stable, numbers-in-names handled naturally. */
  function byName(a, b) {
    return String(a.business_name || '').localeCompare(
      String(b.business_name || ''), undefined, { numeric: true, sensitivity: 'base' }
    );
  }

  window.FedSpaSearch = {
    makeMatcher: makeMatcher,
    filterLicensed: filterLicensed,
    filterUnlicensed: filterUnlicensed,
    byName: byName
  };
})();
