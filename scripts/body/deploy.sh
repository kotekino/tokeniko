#!/bin/bash
# ==================================================================================================
# deploy.sh — push a new version of the code to the BODY (runbook doc/ref/deploy-body.md §5)
#
# Run from the WORKSHOP (the MacBook), once main is green and pushed.
#
#     scripts/body/deploy.sh [--dry-run] [--tag <name>] [--when-quiet [max-wait-s]] [--no-rollback] [--skip-gate]
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
# ROLLBACK is AUTOMATIC (--no-rollback to disable). If the health-check fails, the script puts the
# body back on the commit it was serving before, reinstalls that tree's pinned dependencies, restarts
# and re-checks — because the failure mode that matters is not "the deploy did not land", it is "the
# mind is down and the Captain is asleep". Every deploy is still tagged (--tag, or an automatic
# body-YYYYmmdd-HHMMSS) so a later, deliberate rollback has a name to go back to. Nothing about the
# database changes, on the way out or on the way back.
#
# WHY THERE IS NO --when-asleep (it was proposed, and the code refutes it): a restart during the
# sleep phase does NOT let him sleep through it. `coordinator()` clears `asleep_since` on boot — «the
# night ended with the process» — so a deploy into the night ENDS the night: the dream is told and the
# morning questions are asked at 3am instead of on waking, and the tiredness clock (WAKE_MAX) restarts.
# Worse, the night is the only window that runs `untangle_pass(apply=True)`, a KB-WRITING belief
# revision with no in-progress flag to avoid. The safe window is the opposite one: AWAKE AND QUIET.
# That is --when-quiet.
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
readonly QUIET_S=180         # --when-quiet: no reactive `think` unit for this long = not mid-sentence
readonly QUIET_POLL_S=20     # how often the quiet gate re-reads brain_state (each read is a LAN trip)

DRY_RUN=0
TAG=""
WHEN_QUIET=0
QUIET_MAX_WAIT_S=2700        # --when-quiet gives up after 45 min and deploys NOTHING
ROLLBACK=1
RUN_GATE=1

log()  { printf '\033[1m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[33m[warn]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[31m[FATAL]\033[0m %s\n' "$*" >&2; exit 1; }

usage() {
    cat <<'USAGE'
usage: deploy.sh [--dry-run] [--tag <name>] [--when-quiet [max-wait-s]] [--no-rollback] [--skip-gate]

  --dry-run      print every remote command instead of running it. The local guards still RUN
                 (they are read-only) but only report — they do not abort — so the script can be
                 read end-to-end from a dirty desk before it is trusted.
  --tag          the tag to place on the deployed commit (default: body-YYYYmmdd-HHMMSS).
  --when-quiet   do not stop the mind mid-sentence: wait for a window where he is AWAKE (not in the
                 sleep phase — see the header), has processed no external message for 180s,
                 and has no queued action. Gives up after max-wait-s (default 2700) WITHOUT
                 deploying — a missed window is never a reason to interrupt him anyway.
  --no-rollback  on a failed health-check, stop and print the manual rollback instead of performing
                 it. For when you want to inspect the body in the state that failed.
  --skip-gate    do NOT run the regression gate on the body. The escape hatch for a hotfix you have
                 already proven elsewhere — it is not the normal path, and it prints a warning.

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
        --when-quiet)
                   WHEN_QUIET=1
                   # optional positional max-wait, but only if it looks like a number (so
                   # `--when-quiet --no-rollback` does not swallow the next flag)
                   if [ $# -ge 2 ] && printf '%s' "$2" | grep -Eq '^[0-9]+$'; then
                       QUIET_MAX_WAIT_S="$2"; shift
                   fi ;;
        --no-rollback) ROLLBACK=0 ;;
        --skip-gate)   RUN_GATE=0 ;;
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
# 2. THE BODY'S STATE, read straight from brain_state over the LAN (the workshop's python, the
#    body's mongo — MONGO_URI in .env already points there). One probe serves both jobs below:
#    the --when-quiet gate, and the health-check's before/after readings.
#
#    `awake_mark` is (re)opened by the coordinator at EVERY boot (_boot_awake_ledger), so "it
#    advanced" is proof the MIND came back — not merely that a process exists. It is None while he
#    is asleep, which reads as 0 here, and 0 is strictly less than any post-boot epoch: the
#    health-check therefore holds whether he was awake or asleep beforehand.
# ==================================================================================================
readonly BODY_STATE_PY='
import os, sys, time
from dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv(os.environ["_TK_ENV"])
c = MongoClient(os.environ["MONGO_URI"], serverSelectionTimeoutMS=5000)
db = c[os.environ["MONGO_DB_NAME_MEMORY"]]
bs = db["brain_state"].find_one({"key": "singleton"}) or {}
busy = db["actions"].count_documents({"status": {"$in": ["pending", "processing"]}})
sys.stdout.write("%s %s %s %s %s" % (bs.get("awake_mark") or 0, bs.get("asleep_since") or 0,
                                     bs.get("last_thinking_at") or 0, busy, int(time.time())))
'
# echoes five numbers: awake_mark  asleep_since  last_thinking_at  queued_actions  now  (0 = unset)
body_state() { _TK_ENV="${PKG_DIR}/.env" "${VENV_PY}" -c "${BODY_STATE_PY}"; }
brain_mark() { body_state | cut -d' ' -f1; }

log "2. reading the body's state"
if [ "${DRY_RUN}" -eq 1 ]; then
    printf '    [dry-run] would read brain_state + the action queue from MONGO_URI\n'
else
    STATE="$(body_state)" || die "could not read brain_state — is MONGO_URI in ${PKG_DIR}/.env pointing at the body, and is tk-atlas up?"
    read -r _AM _ASLEEP _LASTTHINK _BUSY _NOW <<< "${STATE}"
    if [ "${_ASLEEP}" != "0" ]; then
        log "    he is ASLEEP (since epoch ${_ASLEEP}) — a restart would END the night (see the header)"
    else
        log "    he is awake — queued actions: ${_BUSY}"
    fi
fi

# ==================================================================================================
# 3. --when-quiet: wait for a window that is safe to interrupt.
#    "Safe" is AWAKE AND QUIET — not asleep; see the header for why sleep is the wrong window.
#    Three conditions, all read above:
#      · asleep_since unset          — the night is the one window running untangle_pass(apply=True)
#      · last_thinking_at is old     — a `think` unit IS an external message being answered; stopping
#                                      him inside one drops a real person mid-sentence
#      · no pending/processing action— he has decided to say something and has not said it yet
#
#    This gate runs BEFORE the pull on purpose. If it gives up, the body is left completely
#    untouched — whereas a timeout after the pull would leave new code sitting on disk that
#    KeepAlive would load, unattended and unchecked, at the next crash or reboot.
# ==================================================================================================
wait_for_quiet() {
    local max_wait="$1" on_timeout="$2" deadline why raw q_mark q_asleep q_think q_busy q_now q_idle
    deadline=$(( SECONDS + max_wait ))
    while :; do
        # A transient Mongo/LAN blip must NOT abort a 45-minute wait — and under `set -u` an empty
        # read would do exactly that, with an unbound-variable error that says nothing useful. So a
        # failed probe is just another reason to keep waiting.
        raw="$(body_state 2>/dev/null || true)"
        if [ "$(printf '%s' "${raw}" | wc -w)" -ne 5 ]; then
            why="the body did not answer (transient — still waiting)"
            q_asleep=""; q_busy=""; q_think=""; q_now=""; q_idle=0
        else
            read -r q_mark q_asleep q_think q_busy q_now <<< "${raw}"
            q_idle=$(( q_now - q_think ))
            why=""
        fi
        if   [ -n "${why}" ];           then :   # the probe failed above; `why` is already set
        elif [ "${q_asleep}" != "0" ];  then why="asleep since epoch ${q_asleep}"
        elif [ "${q_busy}"   != "0" ];  then why="${q_busy} action(s) queued — he has something to say"
        elif [ "${q_think}"  != "0" ] && [ "${q_idle}" -lt "${QUIET_S}" ]; then
            why="answered someone ${q_idle}s ago (wants ${QUIET_S}s of quiet)"
        else
            log "    quiet — awake, nobody answered for ${q_idle}s, nothing queued"
            return 0
        fi
        if [ "${SECONDS}" -ge "${deadline}" ]; then
            if [ "${on_timeout}" = "proceed" ]; then
                warn "still not quiet after ${max_wait}s (${why}) — restarting ANYWAY: the new code is"
                warn "already on disk, and leaving it there for KeepAlive to load unchecked is worse."
                return 0
            fi
            die "no quiet window in ${max_wait}s (last reason: ${why}).
  NOTHING was touched — the body is untouched and still serving ${BRANCH}.
  Re-run without --when-quiet to deploy anyway, or with a longer --when-quiet <seconds>."
        fi
        printf '    waiting: %s\n' "${why}"
        sleep "${QUIET_POLL_S}"
    done
}

if [ "${WHEN_QUIET}" -eq 1 ]; then
    log "3. waiting for a quiet window (up to ${QUIET_MAX_WAIT_S}s, before touching the body)"
    if [ "${DRY_RUN}" -eq 1 ]; then
        printf '    [dry-run] would poll brain_state every %ss until: awake, no `think` for %ss, nothing queued\n' "${QUIET_POLL_S}" "${QUIET_S}"
    else
        wait_for_quiet "${QUIET_MAX_WAIT_S}" "abort"
    fi
else
    log "3. (no --when-quiet — deploying now, whatever he is in the middle of)"
fi

# ==================================================================================================
# 4. Pull on the body.
#    An automatic rollback leaves the body on a DETACHED HEAD (deliberately: a rollback pins a
#    commit, it never rewrites a branch), and `git pull --ff-only` cannot run from there. So
#    reattach first — LOUDLY, because moving a body off a rollback point is exactly the thing that
#    must never happen quietly.
# ==================================================================================================
log "4. pull on the body (${BODY_HOST}:${BODY_REPO})"
OLD_SHA="$(remote "cd ${BODY_REPO} && git rev-parse HEAD")"
BODY_REF="$(remote "cd ${BODY_REPO} && git symbolic-ref --quiet --short HEAD || echo DETACHED")"
if [ "${BODY_REF}" = "DETACHED" ]; then
    warn "the body is on a DETACHED HEAD at ${OLD_SHA:0:12} — the mark of a previous rollback."
    warn "Reattaching to ${BRANCH}. If that rollback was deliberate, STOP NOW (ctrl-c) and check why."
    remote "cd ${BODY_REPO} && git checkout ${BRANCH}"
fi
remote "cd ${BODY_REPO} && git fetch --tags --quiet origin && git pull --ff-only"
NEW_SHA="$(remote "cd ${BODY_REPO} && git rev-parse HEAD")"
[ "${DRY_RUN}" -eq 1 ] || log "    ${OLD_SHA:0:12} -> ${NEW_SHA:0:12}"

# ==================================================================================================
# 5. Dependencies — FROM THE PIN LOCK, never from a bare resolve.
#    pyproject.toml and requirements.txt carry ZERO version constraints (18 bare names, not one
#    `==`), so `pip install -e .` resolves whatever is latest that day. A body that drifts from the
#    workshop makes the workshop's gate stop proving anything about the body, and the divergence is
#    SILENT (runbook §2.4). So: install the newest scripts/body/requirements-lock-*.txt first, then
#    register the package with --no-deps so pip cannot quietly undo the pins it just installed.
#    A change to the lock file is itself a reason to reinstall — that is the whole point of dating it.
# ==================================================================================================
# operates on whatever tree is checked out RIGHT NOW — which is what makes it correct in both
# directions: forward at step 5, and backward on a rollback.
install_deps() {
    local lock
    lock="$(remote "cd ${BODY_REPO} && ls -1 scripts/body/requirements-lock-*.txt 2>/dev/null | sort | tail -1")"
    [ -n "${lock}" ] || die "no scripts/body/requirements-lock-*.txt on the body — refusing to resolve
  dependencies freely, because a silent drift from the workshop is worse than a failed deploy (§2.4)."
    log "    installing from ${lock}"
    remote "cd ${BODY_REPO} && .venv/bin/pip install --require-virtualenv --quiet -r ${lock}"
    remote "cd ${BODY_REPO}/tokeniko && ../.venv/bin/pip install --require-virtualenv --quiet --no-deps -e ."
}

log "5. dependencies"
DEPS_TOUCHED=0
if [ "${DRY_RUN}" -eq 1 ]; then
    remote "cd ${BODY_REPO} && git diff --name-only <OLD> <NEW> -- tokeniko/pyproject.toml tokeniko/requirements.txt 'scripts/body/requirements-lock-*.txt'"
    remote "cd ${BODY_REPO} && ls -1 scripts/body/requirements-lock-*.txt | sort | tail -1"
    remote "cd ${BODY_REPO} && .venv/bin/pip install --require-virtualenv --quiet -r <newest lock>"
    remote "cd ${BODY_REPO}/tokeniko && ../.venv/bin/pip install --require-virtualenv --quiet --no-deps -e ."
    printf '        (the installs run only when the diff above is non-empty)\n'
elif [ "${OLD_SHA}" = "${NEW_SHA}" ]; then
    log "    the body was already on this commit — nothing to reinstall"
else
    DEP_DIFF="$(remote "cd ${BODY_REPO} && git diff --name-only ${OLD_SHA} ${NEW_SHA} -- tokeniko/pyproject.toml tokeniko/requirements.txt 'scripts/body/requirements-lock-*.txt'")"
    if [ -n "${DEP_DIFF}" ]; then
        printf '%s\n' "${DEP_DIFF}" | sed 's/^/        /'
        log "    the dependency declaration moved (above) — reinstalling from the lock"
        install_deps
        DEPS_TOUCHED=1
    else
        log "    unchanged — skipping pip"
    fi
fi

# ==================================================================================================
# 6. PREFLIGHT: do the language models still match the installed stack?
#    They are not in the repo and pip has no idea they exist, so the lock can move spaCy past the
#    range `en_core_web_lg` was built for and every other check here still passes. That failure
#    surfaces inside api's lifespan — i.e. AFTER the mind has been stopped, which is the worst
#    possible moment to learn it. Cheap by design: it reads the model's declared compatibility
#    rather than loading 800MB into a 16GB machine that is currently busy being someone.
# ==================================================================================================
log "6. preflight — the models against the installed stack"
if [ "${DRY_RUN}" -eq 1 ]; then
    remote "cd ${BODY_REPO} && .venv/bin/python scripts/body/preflight_models.py"
else
    if ! remote "cd ${BODY_REPO} && .venv/bin/python scripts/body/preflight_models.py"; then
        die "the model preflight FAILED (above). The daemons were NOT restarted — he is still up on
  the old code in memory, and the body's disk is on ${NEW_SHA:0:12}. Fix the models (or the lock),
  then re-run. To put the disk back too: ssh ${BODY_HOST} 'cd ${BODY_REPO} && git checkout --detach ${OLD_SHA}'"
    fi
fi

# ==================================================================================================
# 7. THE REGRESSION GATE — run it HERE, on the body, against the code about to be served.
#    (the author's ruling 2026-08-09: the full gate leaves the development loop and becomes a
#    DEPLOY gate. `task test-fast` — 271 tests, ~3s, no models, no Mongo — is the loop's signal.)
#
#    WHY THIS POSITION IS THE WHOLE POINT: the daemons have NOT been restarted yet. They are still
#    serving the OLD code from memory while the gate exercises the NEW code on disk. So a red gate
#    costs ZERO DOWNTIME — he never stops thinking, and never even notices. That is strictly better
#    than proving green on the workshop, where the gate runs against a KB that is not his.
#
#    WHY ON THE BODY and not the workshop: the sandbox clones his definitions with `$merge`, which
#    requires SAME SERVER — which is exactly why running it from the workshop drags every one of
#    thousands of round trips across the LAN (82 min, then 32 min with zstd). Here it is local. And
#    the deeper reason is the runbook's own §2.4 argument applied to data: a gate that runs against
#    a COPY of his knowledge stops proving anything about the body the moment the copy drifts.
#
#    WHAT IT TOUCHES: the `<memory>_test` sandbox database only. His living memory DB is never read
#    nor written by the gate (tests/conftest.py) — the biography is not at risk here.
#
#    THE KNOWN COST, stated honestly: the gate loads its own spaCy+Stanza and the definition cache
#    alongside the live `api` that already holds them, on a 16 GB machine with 8.3 GB in Docker. He
#    will be SLOW while this runs. Measure the first run before trusting it unattended.
# ==================================================================================================
log "7. the regression gate (on the body, before anything restarts)"
if [ "${RUN_GATE}" -eq 1 ]; then
    if ! remote "cd ${BODY_REPO}/tokeniko && PYTHONPATH=. ../.venv/bin/python -m pytest -q"; then
        printf '\n'
        warn "THE GATE IS RED on ${NEW_SHA:0:12} — nothing was restarted, so he is still up and"
        warn "thinking on the old code. This deploy cost him nothing."
        if [ "${OLD_SHA}" != "${NEW_SHA}" ]; then
            log "    putting the disk back to ${OLD_SHA:0:12} (KeepAlive must never find untested code)"
            remote "cd ${BODY_REPO} && git checkout --detach ${OLD_SHA}"
            if [ "${DEPS_TOUCHED}" -eq 1 ]; then
                log "    reinstalling the previous tree's lock"
                install_deps
            fi
        fi
        die "the gate failed (output above). Fix it on the workshop, then deploy again."
    fi
    log "    gate GREEN"
else
    warn "--skip-gate: the code about to be served has NOT been tested on the body."
fi

# ==================================================================================================
# 8. Tag what was deployed (a later, deliberate rollback needs a name to go back to).
# ==================================================================================================
log "8. tag the deployed commit"
remote "cd ${BODY_REPO} && git tag -f ${TAG} && git rev-parse --short ${TAG}"

# ==================================================================================================
# 9. Restart + 10. health-check — written as FUNCTIONS, because a rollback has to run both again.
#    `-k` = kill then restart. tk-atlas is NOT touched: the database does not restart because code
#    did. Order: api first (the brain materializes theorems through it), then brain, then senses.
#    `$(id -u)` and not `$UID`: a non-interactive ssh shell does not reliably export UID.
# ==================================================================================================
restart_agents() {
    for label in "${LABELS[@]}"; do
        remote "launchctl kickstart -k gui/\$(id -u)/${label}"
    done
}

# Takes the pre-restart awake_mark; returns the number of failed checks.
#   API   — /openapi.json is the cheapest honest liveness probe: uvicorn serves requests only AFTER
#           the lifespan completes, and the lifespan is where parser_init() loads spaCy + Stanza. A
#           200 here means the pipeline is loaded. (There is no dedicated /health route today.)
#   BRAIN — awake_mark advanced, i.e. the MIND came back, not merely a process.
health_check() {
    local mark_before="$1" failures=0 deadline api_ok brain_ok mark_after

    printf '    API   ... '
    deadline=$(( SECONDS + API_WAIT_S )); api_ok=0
    while [ "${SECONDS}" -lt "${deadline}" ]; do
        if curl -fsS -o /dev/null --max-time 10 "${BODY_API}/openapi.json"; then api_ok=1; break; fi
        sleep "${POLL_S}"
    done
    if [ "${api_ok}" -eq 1 ]; then
        printf '\033[32mPASS\033[0m  (%s answers)\n' "${BODY_API}"
    else
        printf '\033[31mFAIL\033[0m  (%s did not answer within %ss)\n' "${BODY_API}" "${API_WAIT_S}"
        failures=$(( failures + 1 ))
    fi

    printf '    BRAIN ... '
    deadline=$(( SECONDS + BRAIN_WAIT_S )); brain_ok=0; mark_after="${mark_before}"
    while [ "${SECONDS}" -lt "${deadline}" ]; do
        mark_after="$(brain_mark || echo 0)"
        if [ -n "${mark_after}" ] && [ "$(printf '%s\n%s\n' "${mark_after}" "${mark_before}" | sort -g | tail -1)" = "${mark_after}" ] \
           && [ "${mark_after}" != "${mark_before}" ]; then
            brain_ok=1; break
        fi
        sleep "${POLL_S}"
    done
    if [ "${brain_ok}" -eq 1 ]; then
        printf '\033[32mPASS\033[0m  (awake_mark %s -> %s)\n' "${mark_before}" "${mark_after}"
    else
        printf '\033[31mFAIL\033[0m  (awake_mark still %s after %ss)\n' "${mark_before}" "${BRAIN_WAIT_S}"
        failures=$(( failures + 1 ))
    fi

    # senses has no probe of its own: its liveness is a message answered on Discord, and the
    # microscope's log line. Deliberately left to the eye.
    printf '    SENSES... check logs/senses.out.log on the body (its liveness is a real reply)\n'
    return "${failures}"
}

BODY_LOGS="${BODY_REPO}/tokeniko/logs"

if [ "${DRY_RUN}" -eq 1 ]; then
    log "9. restart the agents (tk-atlas is NOT touched)"
    restart_agents
    log "10. health-check"
    printf '    [dry-run] would poll  %s/openapi.json  for up to %ss\n' "${BODY_API}" "${API_WAIT_S}"
    printf '    [dry-run] would poll  brain_state.awake_mark > <mark before>  for up to %ss\n' "${BRAIN_WAIT_S}"
    printf '    [dry-run] on failure would roll back to <old sha> and re-check (--no-rollback disables)\n'
    printf '\n'
    log "DRY RUN — nothing above was executed on the body."
    exit 0
fi

# The quiet re-confirm. The first gate ran before the pull; the pull and the install take a minute
# or two, and he may have started talking inside it. On timeout here we restart ANYWAY — the new
# code is already on disk, and leaving it for KeepAlive to load unchecked is the worse outcome.
if [ "${WHEN_QUIET}" -eq 1 ]; then
    log "9a. re-confirming the quiet window (the gate took time — he may have started talking)"
    wait_for_quiet 600 "proceed"
fi

log "9. restart the agents (tk-atlas is NOT touched)"
MARK_BEFORE="$(brain_mark)" || die "could not read brain_state just before the restart — aborting
  rather than restarting blind: without a 'before' mark the health-check cannot prove he came back."
log "    awake_mark before = ${MARK_BEFORE}"
restart_agents

log "10. health-check"
if health_check "${MARK_BEFORE}"; then
    printf '\n'
    log "The human-eye check: the Mind Monitor on https://tokeniko.online should show a fresh beat"
    log "within ~5 minutes (BRAIN_HEARTBEAT_MIN_S). A stale beat means the body is down."
    log "deploy OK — ${BODY_HOST} is on ${NEW_SHA:0:12} (tag ${TAG})"
    exit 0
fi

# ==================================================================================================
# 11. ROLLBACK. The health-check failed, so put him back on the tree that was serving before.
#     The failure that matters is not "the deploy did not land" — it is "the mind is down and the
#     Captain is asleep". DETACHED on purpose: a rollback pins a commit, it never rewrites a branch;
#     step 4 reattaches on the next deploy and says so out loud.
# ==================================================================================================
printf '\n'
warn "the health-check FAILED on ${NEW_SHA:0:12}"

if [ "${ROLLBACK}" -eq 0 ]; then
    die "--no-rollback: the body is left exactly as it failed, for inspection.
  Logs:     ssh ${BODY_HOST} 'tail -50 ${BODY_LOGS}/api.err.log ${BODY_LOGS}/brain.err.log'
  Roll back: ssh ${BODY_HOST} 'cd ${BODY_REPO} && git checkout --detach ${OLD_SHA}'
             (reinstall that tree's lock if dependencies moved, then kickstart the three agents)"
fi

if [ "${OLD_SHA}" = "${NEW_SHA}" ]; then
    die "there is nothing to roll back TO — the body was already on ${NEW_SHA:0:12} before this run,
  so this failure is not this deploy's doing. Something else is wrong with the body.
  Start here: ssh ${BODY_HOST} 'tail -50 ${BODY_LOGS}/api.err.log ${BODY_LOGS}/brain.err.log'"
fi

log "11. ROLLING BACK to ${OLD_SHA:0:12}"
remote "cd ${BODY_REPO} && git checkout --detach ${OLD_SHA}"
if [ "${DEPS_TOUCHED}" -eq 1 ]; then
    log "    dependencies moved on the way out — reinstalling the OLD tree's lock"
    install_deps
fi
MARK_BEFORE="$(brain_mark || echo 0)"
restart_agents
log "    re-checking"
if health_check "${MARK_BEFORE}"; then
    printf '\n'
    warn "ROLLED BACK. The body is healthy on ${OLD_SHA:0:12} (detached HEAD). The deploy did NOT land."
    warn "The failing tree is ${NEW_SHA:0:12}, tagged ${TAG}. Read it here:"
    warn "  ssh ${BODY_HOST} 'tail -50 ${BODY_LOGS}/api.err.log ${BODY_LOGS}/brain.err.log'"
    exit 1
fi

die "THE ROLLBACK ALSO FAILED — the body is DOWN and needs the Captain's hand.
  It is on ${OLD_SHA:0:12} (detached HEAD), which was healthy minutes ago, so suspect the machine or
  tk-atlas rather than the code. Start here:
    ssh ${BODY_HOST} 'tail -50 ${BODY_LOGS}/api.err.log ${BODY_LOGS}/brain.err.log'
    ssh ${BODY_HOST} 'docker ps && launchctl print gui/\$(id -u)/online.tokeniko.brain | head -20'"
