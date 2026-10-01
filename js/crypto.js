/* ============================================================
   FED-SPA crypto.js - subscriber blob decryption.
   Web Crypto API only. Envelope matches admin_scripts/
   encrypt_unlicensed.js exactly:

     PBKDF2-SHA256, 310,000 iterations, 256-bit key
     AES-256-GCM, 12-byte IV, 16-byte auth tag appended
     to the ciphertext (that is Web Crypto's native layout).

   Nothing leaves the device; wrong passwords simply throw
   OPERATION_ERROR during decrypt. Exposes FedSpaCrypto.
   ============================================================ */

(function () {
  'use strict';

  const enc = new TextEncoder();
  const dec = new TextDecoder();

  function b64ToBytes(b64) {
    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return bytes;
  }

  /** password + envelope -> raw JSON string. Throws on wrong password. */
  async function decrypt(envelope, password) {
    if (!envelope || !envelope.data || !envelope.salt || !envelope.iv) {
      throw new Error('empty-or-malformed-envelope');
    }

    // Derive the same key the admin script derived (PBKDF2-SHA256).
    const baseKey = await crypto.subtle.importKey(
      'raw', enc.encode(password), 'PBKDF2', false, ['deriveKey']
    );
    const key = await crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt: b64ToBytes(envelope.salt),
        iterations: envelope.iterations || 310000,
        hash: 'SHA-256'
      },
      baseKey,
      { name: 'AES-GCM', length: 256 },
      false,
      ['decrypt']
    );

    // AES-GCM decrypt; the trailing 16 bytes are the auth tag.
    const plaintext = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: b64ToBytes(envelope.iv) },
      key,
      b64ToBytes(envelope.data)
    );

    return dec.decode(plaintext);
  }

  /** Convenience: decrypt + JSON.parse + basic shape check. */
  async function decryptList(envelope, password) {
    const raw = await decrypt(envelope, password);
    const parsed = JSON.parse(raw);
    if (!parsed || !Array.isArray(parsed.parlors)) {
      throw new Error('bad-shape');
    }
    return parsed;
  }

  window.FedSpaCrypto = {
    decrypt: decrypt,
    decryptList: decryptList
  };
})();
