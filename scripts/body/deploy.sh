#!/bin/bash
# ==================================================================================================
# deploy.sh — push a new version of the code to the BODY (runbook doc/ref/deploy-body.md §5)
#
# Run from the WORKSHOP (the MacBook), once main is green and pushed.
#
#     scripts/body/deploy.sh [--dry-run] [--tag <name>]
#
# GIT-BASED, NEVER RSYNC. Every deployed version is an auditable commit, and a deploy never touches
# the biography: code and mind live in different places (a quiet virtue of this architecture — the
# database is not restarted because code changed, and `tk-atlas` is never touched here).
#
# ------------------------------------------------------------------------------------------------
# STANDING LAW — restarting the daemons is the Captain's hand.
# This script restarts them. Therefore RUNNING THIS SCRIPT *IS* THAT HAND: never automatic, never
# scheduled, never from a hook, never from an agent. A human decides that the mind stops mid-thought.
# ------------------------------------------------------------------------------------------------
#
# ROLLBACK: every deploy is tagged (--tag, or an automatic body-YYYYmmdd-HHMMSS). To go back:
#     ssh $BODY_HOST 'cd <repo> && git checkout <previous tag>'
#     ssh $BODY_HOST 'launchctl kickstart -k gui/$(id -u)/online.tokeniko.{api,brain,senses}'
#   i.e. the same restart, with an older tree. Nothing about the database changes.
# ==================================================================================================
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd -P)"
PKG_DIR="${REPO_ROOT}/tokeniko"
VENV_PY="${REPO_ROOT}/.venv/bin/python"
CONF_FILE="${SCRIPT_DIR}/body.conf"

readonly LABELS=(online.tokeniko.api online.tokeniko.brain online.tokeniko.senses)
readonly API_WAIT_S=240      # the API's lifespan loads spaCy + Stanza; be patient before failing
readonly BRAIN_WAIT_S=180    # the coordinator writes brain_state.awake_mark at boot
readonly POLL_S=5

DRY_RUN=0
TAG=""

log()  { printf '\033[1m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[33m[warn]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[31m[FATAL]\033[0m %s\n' "$*" >&2; exit 1; }

usage() {
    cat <<'USAGE'
usage: deploy.sh [--dry-run] [--tag <name>]

  --dry-run   print every remote command instead of running it. The local guards still RUN
              (they are read-only) but only report — they do not abort — so the script can be
              read end-to-end from a dirty desk before it is trusted.
  --tag       the tag to place on the deployed commit (default: body-YYYYmmdd-HHMMSS).

The body's address comes from, in order:
  1. $TOKENIKO_BODY_HOST in the environment
  2. scripts/body/body.conf (git-ignored), which may set:
        TOKENIKO_BODY_HOST=renzosala@tokeniko.local     # ssh target (required)
        TOKENIKO_BODY_REPO=/Users/renzosala/Develop/personal/tokeniko   # repo path on the body
        TOKENIKO_BODY_API=http://tokeniko.local:8000    # where the API answers on the LAN
USAGE
}

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run) DRY_RUN=1 ;;
        --tag)     [ $# -ge 2 ] || die "--tag needs a value"; TAG="$2"; shift ;;
        -h|--help) usage; exit 0 ;;
        *)         usage >&2; die "unknown argument: $1" ;;
    esac
    shift
done

# --- where the body lives ---------------------------------------------------------------------
# shellcheck source=/dev/null
[ -f "${CONF_FILE}" ] && . "${CONF_FILE}"

BODY_HOST="${TOKENIKO_BODY_HOST:-}"
[ -n "${BODY_HOST}" ] || die "the body's address is unknown.
  Set TOKENIKO_BODY_HOST in the environment, or create ${CONF_FILE} (git-ignored) containing:
      TOKENIKO_BODY_HOST=renzosala@tokeniko.local
  Optionally also TOKENIKO_BODY_REPO and TOKENIKO_BODY_API — see --help."

BODY_REPO="${TOKENIKO_BODY_REPO:-/Users/renzosala/Develop/personal/tokeniko}"
# default the API address off the ssh target's host part (user@host -> host)
BODY_API="${TOKENIKO_BODY_API:-http://${BODY_HOST##*@}:8000}"
TAG="${TAG:-body-$(date -u '+%Y%m%d-%H%M%S')}"

# --- the remote-command primitive ---------------------------------------------------------------
# Every remote command is PRINTED before it runs, so a --dry-run reading and a live run show the
# same script. `ssh -n` so a remote command can never eat this script's stdin.
# The echo goes to STDERR on purpose: stdout is the remote command's own output, which callers
# capture (`OLD_SHA="$(remote ...)"`). Mixing the two would deploy a sha with a log line glued to it.
remote() {
    printf "    \033[36mssh %s\033[0m '%s'\n" "${BODY_HOST}" "$*" >&2
    if [ "${DRY_RUN}" -eq 1 ]; then
        return 0
    fi
    ssh -n "${BODY_HOST}" "$*"
}

guard_fail() {
    if [ "${DRY_RUN}" -eq 1 ]; then
        warn "[dry-run] would REFUSE: $1"
        return 0
    fi
    die "$1"
}

# ==================================================================================================
# 1. Local guards — deploy what is on ORIGIN, not what is on the desk.
# ==================================================================================================
log "1. local guards (deploy origin, not the desk)"
cd "${REPO_ROOT}"

DIRTY="$(git status --porcelain)"
if [ -n "${DIRTY}" ]; then
    printf '%s\n' "${DIRTY}" | sed 's/^/      /'
    guard_fail "the working tree is dirty (above). Commit or stash before deploying."
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if ! git fetch --quiet origin 2>/dev/null; then
    if [ "${DRY_RUN}" -eq 1 ]; then
        warn "[dry-run] could not fetch origin — the unpushed check below is against a stale ref"
    else
        die "could not fetch origin — is the network up?"
    fi
fi

if ! git rev-parse --verify --quiet "origin/${BRANCH}" >/dev/null; then
    guard_fail "no origin/${BRANCH} — push the branch first (the body pulls from origin)."
elif ! git merge-base --is-ancestor HEAD "origin/${BRANCH}"; then
    printf '      unpushed commits:\n'
    git --no-pager log --oneline "origin/${BRANCH}..HEAD" | sed 's/^/        /'
    guard_fail "HEAD is not on origin/${BRANCH} (above). Push before deploying."
fi

HEAD_SHA="$(git rev-parse HEAD)"
log "    branch ${BRANCH} @ ${HEAD_SHA:0:12} — will be tagged ${TAG}"

# ==================================================================================================
# 2. Read the brain's boot mark BEFORE the restart — the health-check's "before" reading.
#    brain_state.awake_mark is rewritten by the coordinator at every boot (_boot_awake_ledger), so
#    "it advanced" is proof the mind actually came back, not merely that a process exists.
# ==================================================================================================
readonly BRAIN_MARK_PY='
import os, sys
from dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv(os.environ["_TK_ENV"])
c = MongoClient(os.environ["MONGO_URI"], serverSelectionTimeoutMS=5000)
bs = c[os.environ["MONGO_DB_NAME_MEMORY"]]["brain_state"].find_one({"key": "singleton"}) or {}
sys.stdout.write(str(bs.get("awake_mark") or 0))
'
brain_mark() { _TK_ENV="${PKG_DIR}/.env" "${VENV_PY}" -c "${BRAIN_MARK_PY}"; }

MARK_BEFORE=0
if [ "${DRY_RUN}" -eq 1 ]; then
    log "2. [dry-run] would read brain_state.awake_mark (the pre-restart mark)"
else
    log "2. reading brain_state.awake_mark (the pre-restart mark)"
    MARK_BEFORE="$(brain_mark)" || die "could not read brain_state — is MONGO_URI in ${PKG_DIR}/.env pointing at the body?"
    log "    awake_mark before = ${MARK_BEFORE}"
fi

# ==================================================================================================
# 3. Pull on the body.
# ==================================================================================================
log "3. pull on the body (${BODY_HOST}:${BODY_REPO})"
OLD_SHA="$(remote "cd ${BODY_REPO} && git rev-parse HEAD")"
remote "cd ${BODY_REPO} && git fetch --tags --quiet origin && git pull --ff-only"
NEW_SHA="$(remote "cd ${BODY_REPO} && git rev-parse HEAD")"
[ "${DRY_RUN}" -eq 1 ] || log "    ${OLD_SHA:0:12} -> ${NEW_SHA:0:12}"

# ==================================================================================================
# 4. Reinstall the package ONLY when the dependency declaration moved.
#    pyproject.toml lives in the PACKAGE dir, so its path from the git root is tokeniko/pyproject.toml.
# ==================================================================================================
log "4. dependencies"
if [ "${DRY_RUN}" -eq 1 ]; then
    remote "cd ${BODY_REPO} && git diff --name-only <OLD> <NEW> -- tokeniko/pyproject.toml tokeniko/requirements.txt"
    remote "cd ${BODY_REPO}/tokeniko && ../.venv/bin/pip install -e ."
    printf '        (the pip install runs only when the diff above is non-empty)\n'
elif [ "${OLD_SHA}" = "${NEW_SHA}" ]; then
    log "    the body was already on this commit — nothing to reinstall"
else
    DEP_DIFF="$(remote "cd ${BODY_REPO} && git diff --name-only ${OLD_SHA} ${NEW_SHA} -- tokeniko/pyproject.toml tokeniko/requirements.txt")"
    if [ -n "${DEP_DIFF}" ]; then
        log "    dependency files changed — reinstalling"
        remote "cd ${BODY_REPO}/tokeniko && ../.venv/bin/pip install -e ."
    else
        log "    unchanged — skipping pip"
    fi
fi

# ==================================================================================================
# 5. Tag what was deployed (rollback needs a name to go back to).
# ==================================================================================================
log "5. tag the deployed commit"
remote "cd ${BODY_REPO} && git tag -f ${TAG} && git rev-parse --short ${TAG}"

# ==================================================================================================
# 6. Restart the three agents. `-k` = kill then restart. tk-atlas is NOT touched — the database
#    does not restart because code did.
#    Order: api first (the brain materializes theorems through it), then brain, then senses.
#    `$(id -u)` and not `$UID`: a non-interactive ssh shell does not reliably export UID.
# ==================================================================================================
log "6. restart the agents (tk-atlas is NOT touched)"
for label in "${LABELS[@]}"; do
    remote "launchctl kickstart -k gui/\$(id -u)/${label}"
done

# ==================================================================================================
# 7. Health-check.
# ==================================================================================================
log "7. health-check"
FAILURES=0

if [ "${DRY_RUN}" -eq 1 ]; then
    printf '    [dry-run] would poll  %s/openapi.json  for up to %ss\n' "${BODY_API}" "${API_WAIT_S}"
    printf '    [dry-run] would poll  brain_state.awake_mark > %s  for up to %ss\n' "<mark before>" "${BRAIN_WAIT_S}"
else
    # --- the API answers -------------------------------------------------------------------------
    # /openapi.json is the cheapest honest liveness probe: uvicorn serves requests only AFTER the
    # lifespan completes, and the lifespan is where parser_init() loads spaCy + Stanza. A 200 here
    # means the pipeline is loaded. (There is no dedicated /health route in api/main.py today.)
    printf '    API   ... '
    deadline=$(( SECONDS + API_WAIT_S )); api_ok=0
    while [ "${SECONDS}" -lt "${deadline}" ]; do
        if curl -fsS -o /dev/null --max-time 10 "${BODY_API}/openapi.json"; then api_ok=1; break; fi
        sleep "${POLL_S}"
    done
    if [ "${api_ok}" -eq 1 ]; then
        printf '\033[32mPASS\033[0m  (%s answers)\n' "${BODY_API}"
    else
        printf '\033[31mFAIL\033[0m  (%s did not answer within %ss — check logs/api.err.log on the body)\n' "${BODY_API}" "${API_WAIT_S}"
        FAILURES=$(( FAILURES + 1 ))
    fi

    # --- the brain came back ----------------------------------------------------------------------
    printf '    BRAIN ... '
    deadline=$(( SECONDS + BRAIN_WAIT_S )); brain_ok=0; mark_after="${MARK_BEFORE}"
    while [ "${SECONDS}" -lt "${deadline}" ]; do
        mark_after="$(brain_mark || echo 0)"
        if [ -n "${mark_after}" ] && [ "$(printf '%s\n%s\n' "${mark_after}" "${MARK_BEFORE}" | sort -g | tail -1)" = "${mark_after}" ] \
           && [ "${mark_after}" != "${MARK_BEFORE}" ]; then
            brain_ok=1; break
        fi
        sleep "${POLL_S}"
    done
    if [ "${brain_ok}" -eq 1 ]; then
        printf '\033[32mPASS\033[0m  (awake_mark %s -> %s)\n' "${MARK_BEFORE}" "${mark_after}"
    else
        printf '\033[31mFAIL\033[0m  (awake_mark still %s after %ss — check logs/brain.err.log on the body)\n' "${MARK_BEFORE}" "${BRAIN_WAIT_S}"
        FAILURES=$(( FAILURES + 1 ))
    fi

    # senses has no probe of its own: its liveness is a message answered on Discord, and the
    # microscope's log line. Deliberately left to the eye.
    printf '    SENSES... check logs/senses.out.log on the body (its liveness is a real reply)\n'
fi

printf '\n'
if [ "${DRY_RUN}" -eq 1 ]; then
    log "DRY RUN — nothing above was executed on the body."
    exit 0
fi

log "The human-eye check: the Mind Monitor on https://tokeniko.online should show a fresh beat"
log "within ~5 minutes (BRAIN_HEARTBEAT_MIN_S). A stale beat means the body is down."

if [ "${FAILURES}" -gt 0 ]; then
    die "${FAILURES} health check(s) FAILED. Roll back with: ssh ${BODY_HOST} 'cd ${BODY_REPO} && git checkout <previous tag>' + the same kickstarts."
fi
log "deploy OK — ${BODY_HOST} is on ${NEW_SHA:0:12} (tag ${TAG})"
