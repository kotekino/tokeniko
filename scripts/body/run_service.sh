#!/bin/bash
# ==================================================================================================
# run_service.sh — the wait-for-Mongo wrapper (runbook doc/ref/deploy-body.md §1.1)
#
# launchd HAS NO DEPENDENCY ORDERING. At boot the three LaunchAgents fire the moment the user
# session exists — which is before Docker Desktop has finished bringing `tk-atlas` up — and
# `init_io()` dies on an unreachable Mongo. This wrapper is the gate that makes an unattended boot
# deterministic: source `.env`, poll Mongo until it answers, then `exec` the real service so
# launchd supervises the SERVICE, not a babysitting shell.
#
#   usage:  run_service.sh api|brain|senses
#
# On a timeout it exits NON-ZERO on purpose: `KeepAlive: true` in the plist then retries the whole
# wrapper. A script that hangs forever waiting would look alive to launchd and be silent for days.
#
# `.env` is SOURCED here and never displayed — no echo, no log line, no `set -x`. The only thing
# this script ever prints about the environment is which keys were MISSING.
# ==================================================================================================
set -euo pipefail

# --- knobs (deliberately at the top, deliberately constants) --------------------------------------
readonly WAIT_TOTAL_S=300          # bounded total wait ≈ 5 minutes, then hand back to KeepAlive
readonly WAIT_SLEEP_S=3            # pause between attempts
readonly WAIT_ATTEMPT_MS=3000      # per-attempt serverSelectionTimeoutMS — short, we retry anyway
readonly LOG_EVERY=10              # sparse logging: attempt 1, then every Nth (a months-long log
                                   # must not become a wall of "still waiting")

# --- where we are ---------------------------------------------------------------------------------
# resolved from the script's own location, so cwd is irrelevant (launchd's cwd is not ours).
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd -P)"
PKG_DIR="${REPO_ROOT}/tokeniko-tk1"
VENV_BIN="${REPO_ROOT}/.venv/bin"
ENV_FILE="${PKG_DIR}/.env"

log() { printf '%s [run_service] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*"; }
die() { log "FATAL: $*"; exit 1; }

# --- the argument ---------------------------------------------------------------------------------
SERVICE="${1:-}"
case "${SERVICE}" in
  api|brain|senses) ;;
  *) printf 'usage: %s api|brain|senses\n' "$(basename -- "$0")" >&2; exit 64 ;;
esac

[ -d "${PKG_DIR}" ]   || die "package dir not found: ${PKG_DIR}"
[ -x "${VENV_BIN}/python" ] || die "venv python not found: ${VENV_BIN}/python (did you create ../.venv and \`pip install -e .\`?)"

cd "${PKG_DIR}"

# --- .env ------------------------------------------------------------------------------------------
# Parsed line by line rather than `source`d: a value may legitimately contain `=` (a Mongo URI's
# query string) or `#` (a token), and nothing in the file must ever be shell-expanded — a `$` in a
# secret is a character, not a variable. No line of the file is ever printed.
[ -f "${ENV_FILE}" ] || die ".env missing at ${ENV_FILE} — the body cannot know who it is. Copy .env.template and fill it BY HAND (never over git)."

load_env() {
  local line key val
  while IFS= read -r line || [ -n "${line}" ]; do
    line="${line#"${line%%[![:space:]]*}"}"          # strip leading whitespace
    case "${line}" in ''|'#'*) continue ;; esac      # blank + comment
    line="${line#export }"
    case "${line}" in *=*) ;; *) continue ;; esac    # not an assignment
    key="${line%%=*}"
    val="${line#*=}"
    key="${key%"${key##*[![:space:]]}"}"             # strip trailing whitespace off the key
    case "${key}" in
      [A-Za-z_]*) ;;
      *) continue ;;
    esac
    # strip ONE layer of matching surrounding quotes; everything else is taken literally
    case "${val}" in
      \"*\") val="${val:1:${#val}-2}" ;;
      \'*\') val="${val:1:${#val}-2}" ;;
    esac
    export "${key}=${val}"
  done < "${ENV_FILE}"
}
load_env

[ -n "${MONGO_URI:-}" ] || die "MONGO_URI is not set in ${ENV_FILE}"

# --- the Mongo gate ---------------------------------------------------------------------------------
# pymongo, not `mongosh`: pymongo is already a dependency of the venv the service runs in, so the
# probe can never disagree with the client the service will use — and the mini is not required to
# carry the mongo shell at all.
readonly PING_PY='
import os, sys
from pymongo import MongoClient
try:
    MongoClient(os.environ["MONGO_URI"],
                serverSelectionTimeoutMS=int(os.environ["_TK_ATTEMPT_MS"]),
                connectTimeoutMS=int(os.environ["_TK_ATTEMPT_MS"])).admin.command("ping")
except Exception as error:
    sys.stderr.write(type(error).__name__ + "\n")
    sys.exit(1)
'

wait_for_mongo() {
  local attempt=0 deadline=$(( SECONDS + WAIT_TOTAL_S )) reason
  while :; do
    attempt=$(( attempt + 1 ))
    if reason="$(_TK_ATTEMPT_MS="${WAIT_ATTEMPT_MS}" "${VENV_BIN}/python" -c "${PING_PY}" 2>&1 >/dev/null)"; then
      log "mongo answered (attempt ${attempt}) — starting ${SERVICE}"
      return 0
    fi
    if [ "${attempt}" -eq 1 ] || [ $(( attempt % LOG_EVERY )) -eq 0 ]; then
      log "waiting for mongo (attempt ${attempt}, ${reason:-unreachable}) — Docker Desktop may still be starting tk-atlas"
    fi
    if [ "${SECONDS}" -ge "${deadline}" ]; then
      log "mongo did not answer within ${WAIT_TOTAL_S}s after ${attempt} attempts — exiting non-zero so launchd (KeepAlive) retries"
      return 1
    fi
    sleep "${WAIT_SLEEP_S}"
  done
}

wait_for_mongo || exit 1

# --- exec the real thing -----------------------------------------------------------------------------
# `exec`, so the supervised PID IS the service: launchd's KeepAlive then watches the mind, and a
# SIGTERM reaches the coordinator's graceful-shutdown handler instead of a shell.
case "${SERVICE}" in
  api)
    # NO --reload: it is a file-watcher, and a file-watcher restarting the mind is not a mind.
    # EXACTLY ONE worker: app.state holds the loaded spaCy/Stanza parser and the service
    # singletons — a second worker would load its own pipeline and diverge from the first.
    # --host 0.0.0.0 so the workshop (the MacBook) can probe /input and /evaluate over the LAN.
    exec "${VENV_BIN}/uvicorn" api.main:app --host 0.0.0.0 --port 8000 --workers 1
    ;;
  brain)
    exec "${VENV_BIN}/python" -m brain.main
    ;;
  senses)
    exec "${VENV_BIN}/python" -m senses.main
    ;;
esac
