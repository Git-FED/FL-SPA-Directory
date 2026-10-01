# FED-SPA Data Changelog

All notable changes to the FED-SPA data files. Format loosely based on
[Keep a Changelog](https://keepachangelog.com/). New entries go on top.

## [2026-09-07] - Initial Dataset

### Added
- `data/public/licensed.json` created with the first verified establishment:
  - **Halo Asian Spa, Inc** (MM41109) - Clear - expires 2027-08-31 -
    975 West Gateway Blvd, Suite 105, Boynton Beach, FL 33426.
  - Discipline on file: No. Public complaint: No.
  - Source: FL DOH MQA Verification Portal, data as of 9/7/2026.
- `data/meta/schema.json` defining licensed and unlicensed record shapes.
- `data/private/unlicensed.plain.json` initialized empty (subscriber tier).
- `data/private/unlicensed.encrypted.json` initialized as a placeholder blob
  awaiting the first run of `encrypt_unlicensed.js`.

### Workflow
- Annual review cycle established: run `admin_scripts/merge_and_encrypt.sh`
  once per year (or whenever the DOH database changes materially).
