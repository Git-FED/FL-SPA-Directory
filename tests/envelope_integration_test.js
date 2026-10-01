#!/usr/bin/env node
/**
 * FED-SPA envelope integration test.
 *
 * Runs web/js/crypto.js (the REAL browser decrypt path - Web Crypto API,
 * zero mocks beyond a window shim) against an envelope and proves:
 *   1. a wrong password is rejected by GCM auth (throws, not garbage)
 *   2. the right password decrypts to a well-formed document
 *   3. every entry carries the fields web/js/ui.js renders
 *
 * Usage:
 *   node tests/envelope_integration_test.js [envelopePath] [password]
 *
 *   no args  -> data/private/unlicensed.encrypted.json with
 *               $FEDSPA_PASSWORD (local: the envelope you just encrypted)
 *   with args-> any envelope + password (CI: synthetic round-trip)
 *
 * CI runs it like this (production password never leaves the maintainer):
 *   echo '{"version":2,"as_of":"...","parlors":[]}' > /tmp/plain.json
 *   FEDSPA_PASSWORD=ci-password node admin_scripts/encrypt_unlicensed.js \
 *       /tmp/plain.json /tmp/env.json
 *   node tests/envelope_integration_test.js /tmp/env.json ci-password
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const DEFAULT_ENV = path.join(ROOT, 'data', 'private', 'unlicensed.encrypted.json');

const ENV_PATH = process.argv[2] ? path.resolve(process.argv[2]) : DEFAULT_ENV;
const PASSWORD = process.argv[3] || process.env.FEDSPA_PASSWORD;

if (!PASSWORD) {
  console.error('[x] no password: pass it as arg 2 or set FEDSPA_PASSWORD');
  process.exit(2);
}

// -- load the real crypto.js with a minimal window shim --------------------
const code = fs.readFileSync(path.join(ROOT, 'web', 'js', 'crypto.js'), 'utf8');
global.window = {};
new Function('window', code)(global.window);
const FedSpaCrypto = global.window.FedSpaCrypto;

const envelope = JSON.parse(fs.readFileSync(ENV_PATH, 'utf8'));

async function main() {
  const expected = typeof envelope.entries === 'number' ? envelope.entries : null;

  // 1. wrong password MUST throw (GCM auth, not silent garbage)
  let wrongThrew = false;
  try {
    await FedSpaCrypto.decrypt(envelope, 'definitely-not-the-password');
  } catch (e) {
    wrongThrew = true;
    console.log('[ok] wrong password rejected by GCM auth (' + e.name + ')');
  }
  if (!wrongThrew) throw new Error('wrong password did NOT throw');

  // 2. right password MUST decrypt to a well-formed document
  const doc = await FedSpaCrypto.decryptList(envelope, PASSWORD);
  const n = doc.parlors.length;
  console.log('[ok] decrypted via web code path: ' + n + ' entries, as_of ' + doc.as_of);
  if (expected !== null && n !== expected) {
    throw new Error('expected ' + expected + ' entries, got ' + n);
  }

  // 3. every entry must have the fields the UI renders (unlicensedCard)
  const need = ['business_name', 'address', 'status', 'reason', 'last_checked'];
  for (const e of doc.parlors) {
    for (const f of need) {
      if (e[f] === undefined) throw new Error('entry missing ' + f + ': ' + e.business_name);
    }
    for (const a of ['street', 'city', 'state']) {
      if (e.address[a] === undefined) throw new Error('address missing ' + a + ': ' + e.business_name);
    }
  }
  console.log('[ok] all ' + n + ' entries carry the fields web/js/ui.js renders');

  console.log('\nENVELOPE INTEGRATION: PASS (' + path.relative(ROOT, ENV_PATH) + ')');
}

main().catch((e) => { console.error('[x] ' + e.message); process.exit(1); });
