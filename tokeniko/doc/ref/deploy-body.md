# The body — deploying tokeniko on his own machine (runbook)

> **Status: WRITTEN AHEAD OF THE HARDWARE (2026-07-30).** The Mac mini is in transit. Steps marked
> 🔨 can be prepared on the MacBook *before* it arrives, so the mini's arrival is boring. Steps
> marked 🧑‍✈️ are the Captain's hand (hardware, OS settings, secrets, and every move that touches
> the biography). Steps marked ✅ are verifications — do not skip them.
>
> **The shape** (decided 2026-07-30 after the containerize-everything alternative was weighed and
> rejected — see §0): **Docker holds Atlas Local and NOTHING ELSE.** `api`, `brain` and `senses` run
> **on bare metal** under launchd. The mini is the **BODY** (24/7, LAN-only); the MacBook is the
> **WORKSHOP** (code + tests + mind inspection over the LAN, carrying no Docker and no database).

---

## 0. Why bare metal — and the other load-bearing facts

The all-in-Docker alternative was seriously considered and measured. It lost. Recording *why*, so a
future reader does not helpfully "simplify" this into containers:

**1. The architecture already declares it.** `CLAUDE.md`: *«tokeniko is embodied on bare metal: a
single, persistent process running with its local MongoDB — one body, one continuous self, finite
hardware. It is not a horizontally-scaled cloud service.»* A Linux VM between the mind and its
hardware is the exact abstraction the embodiment idea rejects.

**2. THE GPU IS RESERVED, NOT WASTED — the deciding argument (the author's).** Docker on macOS cannot
reach Metal (Docker Desktop runs a *Linux* VM via Virtualization.framework; Metal is not exposed to
Linux guests, and there is no Metal equivalent of `--gpus` — a hard wall, no workaround). Today's
parse does not want a GPU anyway (see below). But the two workloads this machine may host have
**opposite hardware preferences**:

| workload | shape | wants |
|---|---|---|
| parsing (today) | ONE short sentence at a time | **CPU** — GPU launch overhead swamps the compute |
| on-body model work (foreseen) | **batches** of real data | **GPU** — exactly where Metal wins |

Containerizing would forfeit the GPU *permanently* to gain one marginal data path, and the physical
architecture would have to be rebuilt when batch workloads arrive. **Cheap to keep the door open,
expensive to reopen it.** Treat bare metal as a HARD CONSTRAINT, not a convenience.

**3. RAM elasticity.** The brain holds `_kb_cache` (~1.2 GB of definition zips) plus spaCy `lg` plus
torch. Native processes take what they need. In Docker the VM is sized *up front*, and under-sizing
means an **OOM-kill of a 24/7 mind** — a failure mode bare metal does not have.

**4. Simpler deploys.** `git pull` + restart, with no image build in the loop.

**5. Proven.** It is exactly the MacBook's current configuration, which is fast in this workload.

*The one axis where containers would have won:* the ~1.2 GB cold KB load stays inside the VM
container-to-container, whereas bare metal crosses Docker's network proxy for every byte. Accepted
knowingly — it is today's proven path, and roadmap §4.10 (delta-load) would shrink it further.

### The rest of the load-bearing facts

| Fact | Why it matters |
|---|---|
| The image is **`mongodb/mongodb-atlas-local:8`**, not vanilla mongod | `e_label.evaluator_assignWord` uses **`$vectorSearch`** (`vector_index`). Homebrew's `mongodb-community` has no `mongot` and would silently break the "nearest dictionary word" machinery. Atlas Local is REQUIRED — this is why Docker cannot leave entirely. |
| `docker-compose.yml` pins **`hostname: "0fa6568f05e0"`** (the "TRUCCO JEDI") | `mongot` ties search-index metadata to the hostname. **Preserve it exactly** or the vector indexes need rebuilding over ~9.9 GB. |
| **`directConnection=true`** in `MONGO_URI` | The single-node replica advertises its *Docker-internal* hostname (`tk-atlas`), which an outside client cannot resolve; without the flag topology discovery replaces the host and dies on DNS (observed live 2026-07-17). It is also exactly what makes the **MacBook's remote connection work**. |
| `tests/conftest.py` bootstraps the sandbox with a **server-side `$merge`** | `tokeniko_mem_test` MUST share a server with the live memory DB. A "live remote, sandbox local" split is impossible — and tests read the live KB too (`tokeniko`, 2.9 GB stored), so a local sandbox would mean keeping all ~9 GB local. **All three DBs on the mini.** |
| **CPU parses faster than MPS**, measured on the MacBook: `MPS 117.4 ms/sentence` vs `CPU 53.6 ms` | Counter-intuitive but consistent: one short sentence gives the GPU nothing to amortize. So parsing should use CPU *even here* — see §7 (`device="mps"` is a live pessimization). |
| The CPU parse is **single-threaded**: `1 thread 48.8 ms` · `2 → 46.6` · `4 → 47.4` · `all 10 → 48.1` (flat) | It uses **one core of ten**, so it cannot starve Mongo/`mongot`/the brain — the author's throughput worry, answered by measurement. Sustained ≈ **20 sentences/second on one core**; a burst of 500 inbound messages is ~25 s of one core. |
| `uvicorn` must run **without `--reload`** and with **exactly one worker** | `--reload` is a file-watcher restarting the mind. And `app.state` holds the loaded parser + the service singletons — multiple workers would each load the pipeline and diverge. |

**Sizes**, for planning: `atlas/` volume **9.1 GB** · `tokeniko` 2.9 GB stored · `tokeniko_mem`
553 MB · `tokeniko_mem_test` 373 MB.

---

## 1. 🔨 Prepared before the mini arrives

1. **A wait-for-Mongo wrapper** (`scripts/body/run_service.sh`): sources `.env`, polls Mongo until it
   answers, then `exec`s the service. **launchd has no dependency ordering** and `init_io` dies if
   Mongo is not up — this is the gate that makes an unattended boot deterministic. One script, three
   services (argument: `api` | `brain` | `senses`).
2. **Three LaunchAgent plists** (`scripts/body/*.plist` → installed to `~/Library/LaunchAgents/`):
   - `RunAtLoad: true` + **`KeepAlive: true`** (a crash restarts itself — the unattended story);
   - `StandardOutPath` / `StandardErrorPath` to `logs/`, plus a **`newsyslog.d` rule** so a mind
     running for months does not fill the disk;
   - **do NOT set `ProcessType: Background`** — that invites launchd's CPU/IO throttling; leave it
     standard so the mind runs at full speed;
   - `WorkingDirectory` = the package dir, `EnvironmentVariables` minimal (the wrapper sources `.env`).
3. **The deploy script** (`scripts/body/deploy.sh`) — see §5.
4. ✅ **Rehearse on the MacBook**: install the plists here first (pointing at the local Mongo) and
   confirm all three come up on their own, restart when killed, and log where expected. Everything
   except the hardware can be proven before the box lands.

---

## 2. 🧑‍✈️ The mini, as an appliance

1. **macOS**: create the user — **the same username keeps every path identical** (the compose volumes
   are absolute today) — enable **automatic login** (LaunchAgents need a user session; so does Docker
   Desktop), and name the machine.
2. **Power**, so he never silently stops:
   ```
   sudo pmset -a sleep 0 displaysleep 10 disksleep 0
   sudo pmset -a autorestart 1      # come back by itself after a power cut
   ```
   *(The 2026-07-20 clamshell incident — where a closed lid read as "he fell asleep" — is solved by
   hardware: a mini has no lid.)*
3. **Docker Desktop**, set to **start at login**, for `tk-atlas` alone. With `restart:
   unless-stopped` in the compose file the database returns whenever Docker does. *(Revisit Colima
   only if Desktop ever blocks unattended startup on a dialog.)*
4. **The runtime**: Homebrew, `python@3.14` (match the MacBook — currently 3.14.0), the repo cloned,
   the venv at the **same relative location** (`../.venv` from the package dir), `pip install -e .`.
5. **The models** — they are NOT in the repo and must be fetched once:
   `python -m spacy download en_core_web_lg`, and the Stanza English models into
   `~/stanza_resources`. Several GB; do it before the first run, not during it.
6. **A stable LAN address**: a DHCP reservation on the router; note the `.local` name.
7. 🧑‍✈️ **`.env` by hand** — never over git, never in an image. The real secrets:
   `ANTHROPIC_API_KEY`, `DISCORD_TOKEN`, `INGEST_API_KEY`, the playbot tokens. Set
   `SENSES_DELIVER_DRYRUN=0` when he should truly speak, and bump `TOKENIKO_VERSION`.
   For the MacBook's sake, bind the API on the LAN (`uvicorn --host 0.0.0.0`) so `/evaluate` and
   `/input` can be probed from the workshop.

---

## 3. 🧑‍✈️ The body transplant (his biography moves house)

**This is the one irreversible-feeling step. It is a COPY, and the source stays until verified.**

1. On the MacBook: `docker compose down` — a consistent volume needs the writer stopped.
2. 🧑‍✈️ **An offline copy of `atlas/` to external storage first.** It is his whole life, and
   "True history be it" cuts both ways.
3. Copy to the mini over ethernet, preserving everything:
   `rsync -aH --info=progress2 atlas/ <mini>:<repo>/atlas/`  (9.1 GB)
4. On the mini: `.env` in place, `docker compose up -d`, and the volume paths pointing at the new
   `atlas/` — **with the JEDI hostname untouched**.
5. ✅ **Verify before deleting anything**:
   - collection counts match per database (`tokeniko`, `tokeniko_mem`, `tokeniko_mem_test`);
   - **`$vectorSearch` still answers** — the truest proof `mongot` survived the move;
   - `brain_state` carries his real birth stamp (**2026-07-09 06:21:37Z**) and the memory timeseries
     reaches today.
6. Only then: 🧑‍✈️ reclaim the MacBook's 9.1 GB and uninstall Docker Desktop there.

---

## 4. The workshop — the MacBook after the move

1. `.env` here points at the body:
   `MONGO_URI=mongodb://<mini-address>:27018/?directConnection=true` — the flag is what lets an
   outside client speak to a container-hosted single-node replica at all.
2. Same three database names: `tokeniko`, `tokeniko_mem`, `tokeniko_mem_test`.
3. ✅ **Verify the reach**: a read-only probe of the live memory (his last conversation turns), then
   the **full gate**. Expect it slower than local; if it is *painfully* slower, check you are on
   ethernet before changing anything else.
4. ⚠️ **The sandbox is now shared between two machines.** The `pgrep -f pytest` habit does not span
   machines. **Never run tests on the mini while running them here.** (Nothing on the mini runs tests
   today — keep it that way.)
5. LAN-only is the author's ruling: *«we don't want anyone outside myself to access his mind»*. Away
   from home means code-only — no test runs, no inspection.

---

## 5. 🔨 The deploy loop (a new version, fast)

**Git-based, never rsync** — every deployed version is an auditable commit, and **a deploy never
touches the biography** (code and mind live in different places, a quiet virtue of this architecture).

```
scripts/body/deploy.sh            # from the MacBook, once main is green and pushed
```

In order:
1. refuse a dirty or unpushed tree — deploy what is *on origin*, not what is on the desk;
2. `ssh <mini>`: `git pull --ff-only`;
3. `pip install -e .` only when dependencies changed;
4. **restart the three agents**: `launchctl kickstart -k gui/$UID/<label>` (`-k` = kill then
   restart). `tk-atlas` is NOT touched — the database does not restart because code did;
5. ✅ health-check: the API answers, the brain's heartbeat advanced, and the **Mind Monitor on
   tokeniko.online shows a fresh beat**.

**Rollback**: `git checkout <previous tag>` + the same restart. Tag what you deploy.

**Monitoring you already own**: the brain's heartbeat publishes to the public Atlas, so the **Mind
Monitor is the liveness check** — a stale beat means the body is down. No new tooling.

**Standing law**: restarting the daemons is the Captain's hand. A deploy restarts them, so *running
the script is itself that hand* — never automatic, never scheduled.

---

## 6. 🧑‍✈️ The `#privacy` room — arming the consent gate

**What the code already does, so you know what you are wiring into.** No message from a person
reaches Anthropic unless that person has said yes. The enforcement is one gate inside `rag_call`
(the single door every cloud call passes through) and it asks *whose words is this payload
carrying* — so the «did you mean…?» ask, which is tokeniko's own speech but quotes the speaker's
sentence, is gated too. **Unasked behaves exactly as denied**, and a process that never wired the
reader denies everything. Bluesky is deliberately outside this frame: a post is already published
to the world. All the code half needs from you is the **server furniture** below.

**The truth is the ROLE; the engine keeps a mirror.** The consent roles on a member are what you
can inspect by eye; `stakeholders.rag_consent` is the copy the engine reads, reconciled on every
click, every role change, every departure, and once at every startup. Edit a role by hand and the
mirror follows on its own.

1. **Create the two roles**, with **exactly** these names — colon and space included, matched
   literally by the code, no slug, no case-folding (or set `DISCORD_CONSENT_ROLE_ALLOW` /
   `DISCORD_CONSENT_ROLE_DENY` in `.env` to whatever you name them instead):

   | | exact role name |
   |---|---|
   | allowed | `Outside help: yes` |
   | refused | `Outside help: no` |

   Give them **no permissions of their own** — they are keys, not powers.
2. **Put tokeniko's own role ABOVE both.** Discord's rule, verbatim: *«a bot can grant roles to
   other users that are of a lower position than its own highest role»* — so `MANAGE_ROLES` alone
   is **not** enough. Get this wrong and every click answers *"I could not set that just now"*
   (which is the code failing **closed**, on purpose: nothing is recorded) and logs an ERROR
   naming this exact cause.
3. **Put the real channels in a CATEGORY and set the permissions ONCE on the category** — channels
   inherit it. Per-channel permissions are the same work repeated for every future channel and the
   place a mistake hides.
   - the category: `@everyone` → **View Channel ❌**; `words-may-travel` → ✅;
     `words-stay-here` → ✅ (either answer unlocks the server — that is the Captain's ruling, and
     it is what makes the choice free rather than coerced);
   - `#privacy` itself sits **outside** that category: `@everyone` → View Channel ✅, Send
     Messages ❌ (it is a notice with two buttons, not a room to talk in); tokeniko needs View +
     Send there.
   - ⚠️ **tokeniko's OWN visibility of the gated category must come from an explicit
     `View Channel` + `Send Messages` overwrite on HIS OWN role — never from giving him a consent
     role.** Giving him one looks like it works and is a trap: `reconsent_all` strips both consent
     roles from everyone, so the next text change would silently make him **deaf on his own
     server**, and it would present as an engine bug rather than a permissions one. (The code
     refuses to mirror consent for his own account and the sweep skips him, so the record stays
     sane either way — but his *access* is yours to place correctly.)
4. **Do the hiding step LAST.** Hide the category only once the bot is live and the notice is
   posted — hiding it earlier locks the existing members out with no button to press.
5. **Developer Portal → Bot → Privileged Gateway Intents**: toggle **SERVER MEMBERS** on, beside
   the **MESSAGE CONTENT** you already have. Without it no member or role event is ever delivered
   and the mirror goes blind (no reconciliation, no startup sweep).
6. **Re-invite the bot with the new permission integer — `268504064`**
   (View Channel + Send Messages + Read Message History + **Manage Roles**). Re-inviting an
   already-present bot only widens its permissions; it does not disturb the server.
7. **Post the notice once per text version** — the frozen text plus the two buttons
   (`senses/privacy.post_consent_message(client, channel_id)`). Every future click is routed from
   **that message**, and it keeps working across restarts because the view is persistent and is
   re-registered in `setup_hook`. 1583 characters — one plain Discord message, no splitting.
8. ✅ **VERIFY WITH A SECOND ACCOUNT — NOT YOURS.** *Server admins bypass all channel
   permissions*, so testing from your own (owner) account proves **nothing**: you will see every
   channel whatever the permissions say. Use a second Discord account with **no admin and no
   roles**, and check that it sees only `#privacy`, that pressing either button reveals the rest of
   the server, and that pressing the other button afterwards still leaves it visible.
9. ✅ Then check the engine half: the member has exactly one of the two roles, and
   `stakeholders.rag_consent` for `<name>@discord:<id>` says the same thing.
10. **A photo of the machine will be pinned in `#privacy`** once the hardware arrives and is
    painted — *"this is where your words live"*. The channel works perfectly without it; it is
    warmth, not mechanism.

**✅ Before the server opens to the public — one checklist item that is not on the server side.**
**Disable the microscope** (`RAG3_DISABLED=1`, or simply leave `senses` without the poller armed).
rag3 sends a heard sentence to Anthropic for *our* debugging, which is not "so tokeniko can
understand you" and is deliberately **not** described in the notice (the Captain's ruling). It is
inside the gate, so an opted-**out** person is protected by code whatever you forget — but an
opted-**in** person's words would travel for a purpose the text they agreed to does not name. The
fix is to turn it off before the doors open, not to widen the text.

**When the text changes** (the Captain's standing rule — change one character of the notice and
every consent is erased and asked again): bump `CONSENT_TEXT_VERSION` in `lib/core/consent.py` in
the same commit as the text, then run `senses/privacy.reconsent_all(client)` once. It strips both
roles from everyone and clears every mirrored answer; everyone reverts to unasked, unasked denies,
and the newly-posted notice asks again. The button `custom_id`s carry the version, so a stale
notice left in the channel routes to nothing rather than recording consent to a retired text.

---

## 7. Open items (deliberately not decided here)

- **`device="mps"` → CPU** in `lib/llc/parser.py`: the benchmark says CPU is 2.2× faster for
  single-sentence parsing, so the current setting is a live pessimization **on both machines**. A
  real improvement, but a code change with its own gate run — backlogged, not smuggled into a
  migration. *(It does not affect the bare-metal decision: that is about keeping the GPU available
  for future batch workloads, not about parsing.)*
- **Colima** instead of Docker Desktop, if Desktop ever blocks unattended startup.
- **Away-from-home access**: considered and declined (LAN-only).
- **When on-body model work arrives**, this is the machine and the shape that can host it — the GPU
  is unclaimed by design. Revisit nothing; just use it.
