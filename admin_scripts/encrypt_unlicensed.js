#!/usr/bin/env node
/**
 * FED-SPA unlicensed-list encryptor - Node.js native crypto only.
 *
 * Reads  data/private/unlicensed.plain.json   (NEVER committed)
 * Writes  data/private/unlicensed.encrypted.json  (safe to commit)
 *
 * Envelope: PBKDF2-SHA256 (310k iterations) -> AES-256-GCM.
 * The GCM auth tag is appended to the ciphertext (Web Crypto / CryptoKit /
 * javax.crypto all expect it that way), so decryption is one call on every
 * platform FED-SPA ships on.
 *
 * Usage:
 *   node admin_scripts/encrypt_unlicensed.js            (prompts for password)
 *   FEDSPA_PASSWORD="..." node admin_scripts/encrypt_unlicensed.js
 *   node admin_scripts/encrypt_unlicensed.js <plainPath> <encPath>
 *       (positional paths are for tests/CI: encrypt an arbitrary document
 *        without touching the repo's real files)
 */

'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const ROOT = path.resolve(__dirname, '..');
const DEFAULT_PLAIN = path.join(ROOT, 'data', 'private', 'unlicensed.plain.json');
const DEFAULT_ENC = path.join(ROOT, 'data', 'private', 'unlicensed.encrypted.json');

// Optional positional overrides (test/CI path): [plainPath] [encPath]
const PLAIN_PATH = process.argv[2] ? path.resolve(process.argv[2]) : DEFAULT_PLAIN;
const ENC_PATH = process.argv[3] ? path.resolve(process.argv[3]) : DEFAULT_ENC;

const ITERATIONS = 310000;
const SALT_BYTES = 16;
const IV_BYTES = 12;
const KEY_BYTES = 32; // AES-256

/** Prompt on the TTY with echo muted. */
function askHidden(question) {
  return new Promise((resolve, reject) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    const stdin = process.openStdin();
    process.stdin.setRawMode(true);
    let answer = '';
    const onData = (ch) => {
      if (ch === '\r' || ch === '\n') {
        process.stdin.setRawMode(false);
        stdin.removeListener('data', onData);
        rl.close();
        process.stdout.write('\n');
        resolve(answer);
      } else if (ch === '\u0003') {
        // Ctrl+C
        process.stdin.setRawMode(false);
        rl.close();
        process.exit(130);
      } else if (ch === '\u007f') {
        if (answer.length) answer = answer.slice(0, -1);
      } else {
        answer += ch.toString('utf8');
      }
    };
    stdin.on('data', onData);
    rl.question(question, () => {});
  });
}

async function main() {
  // 1. Load + parse the plaintext list (fails loudly on bad JSON).
  let plainRaw;
  try {
    plainRaw = fs.readFileSync(PLAIN_PATH, 'utf8');
  } catch (err) {
    console.error(`[x] Cannot read ${PLAIN_PATH}\n    ${err.message}`);
    process.exit(1);
  }
  let plain;
  try {
    plain = JSON.parse(plainRaw);
  } catch (err) {
    console.error(`[x] unlicensed.plain.json is not valid JSON: ${err.message}`);
    process.exit(1);
  }
  const count = Array.isArray(plain.parlors) ? plain.parlors.length : 0;
  console.log(`[+] Loaded ${count} unlicensed entr${count === 1 ? 'y' : 'ies'}.`);

  // 2. Get the subscriber password.
  let password = process.env.FEDSPA_PASSWORD;
  if (!password) {
    password = await askHidden('Subscriber password: ');
    const confirm = await askHidden('Confirm password: ');
    if (password !== confirm) {
      console.error('[x] Passwords do not match.');
      process.exit(1);
    }
  }
  if (password.length < 8) {
    console.error('[x] Password must be at least 8 characters.');
    process.exit(1);
  }

  // 3. Derive the key (PBKDF2-SHA256) - matches web/js/crypto.js exactly.
  const salt = crypto.randomBytes(SALT_BYTES);
  const iv = crypto.randomBytes(IV_BYTES);
  const key = crypto.pbkdf2Sync(password, salt, ITERATIONS, KEY_BYTES, 'sha256');

  // 4. Encrypt with AES-256-GCM; tag is appended to the ciphertext.
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
  const plaintext = Buffer.from(plainRaw, 'utf8');
  const ciphertext = Buffer.concat([
    cipher.update(plaintext),
    cipher.final(),
    cipher.getAuthTag(),
  ]);

  // 5. Write the envelope the apps know how to open.
  const envelope = {
    v: 1,
    kdf: 'PBKDF2-SHA256',
    iterations: ITERATIONS,
    salt: salt.toString('base64'),
    iv: iv.toString('base64'),
    data: ciphertext.toString('base64'),
    generated: new Date().toISOString(),
    entries: count,
  };
  fs.writeFileSync(ENC_PATH, JSON.stringify(envelope, null, 2) + '\n');
  console.log(`[+] Encrypted ${ciphertext.length} bytes -> ${ENC_PATH}`);
  console.log('[!] Keep the password safe; it is NOT recoverable from the output.');
  console.log('[!] Remind subscribers: unlock code rotates with every annual update.');

  // 6. Sanity check: prove the envelope round-trips before we call it done.
  const verify = JSON.parse(fs.readFileSync(ENC_PATH, 'utf8'));
  const dkey = crypto.pbkdf2Sync(password, Buffer.from(verify.salt, 'base64'), verify.iterations, KEY_BYTES, 'sha256');
  const blob = Buffer.from(verify.data, 'base64');
  const decipher = crypto.createDecipheriv('aes-256-gcm', dkey, Buffer.from(verify.iv, 'base64'));
  decipher.setAuthTag(blob.slice(-16));
  const round = Buffer.concat([decipher.update(blob.slice(0, -16)), decipher.final()]).toString('utf8');
  if (round !== plainRaw) {
    console.error('[x] Self-check FAILED - do not distribute this file.');
    process.exit(1);
  }
  console.log('[+] Self-check passed: encryption round-trips correctly.');
}

main().catch((err) => {
  console.error(`[x] Unexpected failure: ${err.message}`);
  process.exit(1);
});
