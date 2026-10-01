#!/usr/bin/env bash
#
# FED-SPA annual update - one command runs the whole workflow.
#
#   ./admin_scripts/merge_and_encrypt.sh              # standard annual run
#   SCRAPE=1 ./admin_scripts/merge_and_encrypt.sh     # also re-scrape MQA first
#
# Steps:
#   1. Validate current data files against the schema
#   2. (optional) Re-scrape the FL DOH MQA portal into data/meta/raw/
#   3. Regenerate platform copies of the licensed list
#   4. Encrypt the subscriber unlicensed list (skipped if empty)
#   5. Re-validate + fan out the encrypted blob
#   6. Print the manual wrap-up checklist (changelog, commit, tag)
#
set -euo pipefail
cd "$(dirname "$0")/.."

PY=python3
NODE=node
BOLD=$'\033[1m'; DIM=$'\033[2m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'; RED=$'\033[31m'; RESET=$'\033[0m'

step() { printf "\n${BOLD}== %s ==${RESET}\n" "$1"; }
die()  { printf "\n${RED}[x] %s${RESET}\n" "$1" >&2; exit 1; }

step "1/6 Validating current data"
$PY admin_scripts/validate_schema.py || die "Fix schema violations before continuing."

if [[ "${SCRAPE:-0}" == "1" ]]; then
  step "2/6 Re-scraping the MQA portal"
  if [[ -f data/meta/raw/queries.txt ]]; then
    $PY admin_scripts/scrape_mqa.py scrape --file data/meta/raw/queries.txt \
      || die "Scrape failed - check network / run 'scrape_mqa.py discover'."
  else
    $PY admin_scripts/scrape_mqa.py discover
    printf "${YELLOW}No data/meta/raw/queries.txt found - discover output above.${RESET}\n"
    printf "${DIM}Create it (one establishment name per line), review raw results, then re-run with SCRAPE=1.${RESET}\n"
  fi
else
  step "2/6 Skipping scrape (pass SCRAPE=1 to re-scrape)"
fi

step "3/6 Generating public/platform copies"
$PY admin_scripts/generate_public_files.py || die "Public file generation failed."

step "4/6 Encrypting the subscriber list"
ENTRIES=$($PY - <<'EOF'
import json,sys
try:
    d=json.load(open('data/private/unlicensed.plain.json'))
    print(len(d.get('parlors',[])))
except Exception:
    print(-1)
EOF
)
if [[ "$ENTRIES" == "-1" ]]; then
  die "data/private/unlicensed.plain.json is unreadable."
elif [[ "$ENTRIES" == "0" ]]; then
  printf "${YELLOW}Unlicensed list is empty - skipping encryption (placeholder remains).${RESET}\n"
else
  if [[ -z "${FEDSPA_PASSWORD:-}" ]]; then
    printf "${DIM}You will be prompted twice for the subscriber password.${RESET}\n"
  fi
  $NODE admin_scripts/encrypt_unlicensed.js || die "Encryption failed."
fi

step "5/6 Re-validating + fanning out encrypted blob"
$PY admin_scripts/validate_schema.py --quiet || true
$PY admin_scripts/generate_public_files.py || die "Final generation failed."

step "6/6 Manual wrap-up checklist"
cat <<'EOF'
Remaining steps (only you can do these):

  [ ] Review data/meta/raw/scrape_<date>.json - confirm every triage
  [ ] Update data/meta/changelog.md (new entry on top)
  [ ] Bump "version" + "as_of" in licensed.json / unlicensed.plain.json
  [ ] If the subscriber password changed, notify subscribers
  [ ] git add -A && git commit -m "data: annual refresh YYYY-MM-DD"
  [ ] git tag data-YYYY-MM-DD && git push --tags
  [ ] Rebuild/republish: web deploy, extension zip, Android/Auto/Wear APKs

Done for another year.
EOF

printf "\n${GREEN}FED-SPA annual update complete.${RESET}\n"
