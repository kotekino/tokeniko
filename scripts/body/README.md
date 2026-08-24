# `scripts/body/` — the body's furniture

Everything needed to run tokeniko unattended on the **Mac mini** (the BODY), and to push new code to
it from the **MacBook** (the WORKSHOP). The authority is `tokeniko/doc/ref/deploy-body.md`; this file
is only the *commands*.

> ⚠️ **The plists, the rotation rule and the compose volumes all hardcode the username
> `renzosala` and the repo path `/Users/renzosala/Develop/personal/tokeniko`.** The mini must use the
> same username and the same repo path, or all four files need regenerating (`docker-compose.yml`
> pins absolute volume paths and the `hostname: "0fa6568f05e0"` JEDI trick — see the runbook §0).

| file | what it is |
|---|---|
| `run_service.sh` | the wait-for-Mongo wrapper. `run_service.sh api\|brain\|senses` — sources `.env`, polls Mongo until it answers (bounded ~5 min), then `exec`s the service. launchd has no dependency ordering; this is the gate. |
| `online.tokeniko.api.plist` | LaunchAgent for the FastAPI server (`uvicorn`, one worker, no `--reload`). |
| `online.tokeniko.brain.plist` | LaunchAgent for the mind (`python -m brain.main`). |
| `online.tokeniko.senses.plist` | LaunchAgent for the connectors (`python -m senses.main`). |
| `newsyslog-tokeniko.conf` | rotation for the six log files (3 services × stdout/stderr). Needs `sudo`. |
| `deploy.sh` | the deploy loop: refuse a dirty/unpushed tree → `git pull --ff-only` on the body → conditional `pip install -e .` → tag → restart the three agents → health-check. |
| `verify_transplant.py` | the read-only transplant verifier (runbook §3.5, scripted). |
| `baseline-macbook-2026-08-06.json` | the MacBook baseline captured before the move — the evidence the transplant is diffed against. |
| `body.conf` | *(git-ignored, you create it)* the mini's ssh address for `deploy.sh`. |

---

## Installing the LaunchAgents

The log directory must exist **before** the agents start — launchd opens the log files itself and
will not create the folder:

```sh
mkdir -p /Users/renzosala/Develop/personal/tokeniko/tokeniko-tk1/logs
```

Then, per agent:

```sh
cd /Users/renzosala/Develop/personal/tokeniko
cp scripts/body/online.tokeniko.api.plist    ~/Library/LaunchAgents/
cp scripts/body/online.tokeniko.brain.plist  ~/Library/LaunchAgents/
cp scripts/body/online.tokeniko.senses.plist ~/Library/LaunchAgents/

launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/online.tokeniko.api.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/online.tokeniko.brain.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/online.tokeniko.senses.plist
```

`bootstrap` is the modern spelling; `launchctl load <plist>` is the legacy one and still works, but
it reports errors far less clearly. The modern verbs:

```sh
launchctl print    gui/$(id -u)/online.tokeniko.brain    # full state: PID, last exit, env
launchctl kickstart -k gui/$(id -u)/online.tokeniko.brain # restart (kill then start)
launchctl bootout  gui/$(id -u)/online.tokeniko.brain     # stop and unload (legacy: unload)
launchctl list | grep online.tokeniko                     # the quick "are they there" glance
```

**After editing a plist**, `bootout` then `bootstrap` again — launchd caches the old definition.

## Installing the log rotation (needs root)

```sh
sudo cp scripts/body/newsyslog-tokeniko.conf /etc/newsyslog.d/tokeniko.conf
sudo chown root:wheel /etc/newsyslog.d/tokeniko.conf
sudo chmod 644 /etc/newsyslog.d/tokeniko.conf
sudo newsyslog -nv          # DRY RUN: prints what it would do to each file, changes nothing
```

---

## The rehearsal — today, on the MacBook (runbook §1.4)

The whole point: prove the unattended story *before* the hardware exists. `tk-atlas` is already up
here, so the agents will find their Mongo.

**Before you start:** the `senses` agent SPEAKS. Confirm `SENSES_DELIVER_DRYRUN=1` in
`tokeniko/.env` unless you mean him to be heard from the MacBook.

```sh
# 0. the log directory
mkdir -p /Users/renzosala/Develop/personal/tokeniko/tokeniko-tk1/logs

# 1. install and start all three
cd /Users/renzosala/Develop/personal/tokeniko
for s in api brain senses; do
  cp scripts/body/online.tokeniko.$s.plist ~/Library/LaunchAgents/
  launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/online.tokeniko.$s.plist
done

# 2. they should come up on their own (the api takes ~30-60s: spaCy + Stanza load in the lifespan)
launchctl list | grep online.tokeniko              # PID in column 1, last exit code in column 2
tail -f tokeniko/logs/*.log                        # the wrapper's "mongo answered" then the service

# 3. THE KEEPALIVE PROOF — kill one and watch it come back
launchctl print gui/$(id -u)/online.tokeniko.brain | grep -E 'pid|state'
kill -9 <that pid>
sleep 40 && launchctl print gui/$(id -u)/online.tokeniko.brain | grep -E 'pid|state'
#   ^ a DIFFERENT pid = KeepAlive works. (ThrottleInterval is 30s, so give it more than 30.)

# 4. the API answers
curl -fsS -o /dev/null -w '%{http_code}\n' http://localhost:8000/openapi.json     # expect 200

# 5. take them down again
for s in api brain senses; do launchctl bootout gui/$(id -u)/online.tokeniko.$s; done
```

If a service does not come up, its `logs/<service>.err.log` says why — the wrapper logs a clear
FATAL for a missing `.env` or a missing venv, and a clear timeout line if Mongo never answered.

---

## The transplant verifier

Read-only by construction: no insert, no update, no index creation, and raw pymongo rather than
`init_io()` (which would upsert the stakeholder singleton). Safe against the live body, mid-thought.

```sh
# on the MacBook, IMMEDIATELY BEFORE `docker compose down` — capture the baseline
./.venv/bin/python scripts/body/verify_transplant.py --out scripts/body/baseline-<date>.json

# on the mini, after the rsync and `docker compose up -d` — diff against it
./.venv/bin/python scripts/body/verify_transplant.py --compare scripts/body/baseline-<date>.json
echo $?     # 0 = every measured value identical; 1 = mismatch; 2 = could not reach mongo
```

**Capture the baseline as late as possible.** Every count in it is a moving target while the mind is
alive — a baseline taken a week before the move will differ from the copy purely because he kept
thinking. The comparison prints identity mismatches (birth stamp, `$vectorSearch`, first memory) in
red and mere growth in yellow, so you can tell "the copy is broken" from "he lived a bit".

`--fast` uses estimated counts. Do not use it for the decision to delete the source.

---

## Deploying a new version

```sh
# once, on the MacBook: tell the script where the body is
cat > scripts/body/body.conf <<'CONF'
TOKENIKO_BODY_HOST=renzosala@tokeniko.local
TOKENIKO_BODY_REPO=/Users/renzosala/Develop/personal/tokeniko
TOKENIKO_BODY_API=http://tokeniko.local:8000
CONF

scripts/body/deploy.sh --dry-run     # read every remote command before trusting it
scripts/body/deploy.sh               # for real
```

`body.conf` is git-ignored (it is a machine-local fact). `TOKENIKO_BODY_HOST` in the environment
works instead of the file.

**Standing law:** restarting the daemons is the Captain's hand, and this script restarts them —
so *running it is itself that hand*. Never automatic, never scheduled, never from a hook.

**Rollback** — every deploy is tagged (`body-YYYYmmdd-HHMMSS`, or `--tag <name>`):

```sh
ssh $BODY_HOST 'cd <repo> && git checkout <previous tag>'
for l in api brain senses; do ssh $BODY_HOST "launchctl kickstart -k gui/\$(id -u)/online.tokeniko.$l"; done
```

The database is never touched by any of this. `tk-atlas` does not restart because code changed.
