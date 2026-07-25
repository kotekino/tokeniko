# Brief 1b: the "did you mean?" ANSWER binding — the pending lifecycle (2026-07-25)

**To the 1st Officier, from the QM.** The second half of §1's first brick. DO NOT start until 1a
is committed (it depends on the room, `MEMExchange`/`MEMPending`, `suggested_reading`, and the
opened pending). The Captain was emphatic: a «did you mean?» must HANDLE the answer, not
ask-and-ignore. The laws of the ship apply in full.

## The design (the Captain's ruling, fork b)

After tokeniko asks «did you mean X?», the room holds an OPEN pending scoped to `(asker, channel)`.
The asker's NEXT directed message binds it — resolved BEFORE the normal assertion path:
- **«sì» / «yes» / affirmation** → re-ingest the reading X **as CONFIRMED** (now it MAY be believed
  — the human said so): compile X and run it through the normal ingestion as the confirmed meaning
  of the original item; mark the pending `resolved`.
- **«no» / negation** → DROP the reading (never believed); mark `resolved`. Optionally a brief
  acknowledgement («understood»), the Captain's call at review — default silent.
- **a clear restatement** (a fresh, non-yes/no message that parses soundly) → SUPERSEDE: let it flow
  through the normal pipeline as a new assertion, and mark the pending `resolved` (the human
  reworded instead of confirming).
- **silence past `expires_at`** → LAPSE: mark `lapsed` (a lazy check when next touching the room —
  no timer/scheduler; the brain notices on the next interaction or wondering pass). A lapsed window
  means "away" relative to THIS person's rhythm — nothing is believed.

## Build

### 1. The binding, before the assertion path (`brain/thinking.py`)

In `think_one`, EARLY (before the question/assertion branches, near the social-act early-return):
- fetch the room for `(canonical(item.sourceId), channel_id)`; if it has an OPEN, non-expired
  `did_you_mean` pending → this message is a candidate ANSWER.
- classify the message: affirmation / negation / restatement. Reuse the anchor-catch discipline
  (nearest-of-anchors, never a fixed word list — the `lib/llc/anchors` / social-detect pattern):
  a small yes/no anchor set (multilingual-friendly — «sì», «yes», «no», «esatto», …; the anchor
  resolver already generalizes beyond a list). A message that is neither a clear yes nor no and
  parses as a sound assertion → restatement.
- **affirmation** → load the referenced item (`pending.ref_item_id`), read its `suggested_reading`,
  and re-ingest it as the confirmed meaning: compile the reading and route it through the normal
  ingestion/eval path AS IF the human had said it cleanly (it now MAY become belief/knowledge — the
  confirmation is the human's authority; provenance should note "confirmed reading of <item>").
  Resolve the pending. Then STOP (do not also treat the «yes» itself as an assertion).
- **negation** → resolve the pending, drop the reading, STOP (the «no» is not an assertion to
  evaluate).
- **restatement** → resolve the pending and FALL THROUGH to the normal assertion path (the reworded
  message is ingested normally).
- Guard: the binding only fires when the incoming message is DIRECTED enough (the same addressed
  bar the ask respected) — an ambient aside from the asker mid-window is not necessarily the answer.

### 2. Lapse (lazy, no scheduler)

When the room is touched (the binding fetch, the tempo update, or a wondering-pass sweep) and an
OPEN pending is past `expires_at`, mark it `lapsed`. No timer, no new loop — the lazy check is
enough (a lapsed pending simply stops being a binding target). Biography: pendings are never
deleted, only `resolved`/`lapsed` (the room is the record of every clarification asked).

### 3. The confirmation acknowledgement (optional, the Captain's call at review)

Default: an affirmation re-ingests silently (the re-ingested reading's own reflexes speak — a true
reading may corroborate, a false one speak up, exactly as a cleanly-said message would). A dedicated
«got it» is NOT built unless the Captain asks — keep 1b about the binding.

## Tests (sandbox, sibling style)

The full lifecycle on a seeded open pending: affirmation → the reading is re-ingested as the
confirmed meaning + pending resolved + the «yes» itself is not evaluated · negation → dropped +
resolved · restatement → the pending resolves + the new message ingests normally · silence past
`expires_at` → lapsed on next touch, never a binding target · a directed non-answer vs an ambient
aside · multilingual yes/no via the anchor catch («sì»/«no») · nothing binds when there is no open
pending (the normal path is untouched). Full gate foreground, `pgrep -f pytest` first.

## Out of scope

- Multilingual translation (chapter step 2) — but the anchor-catch yes/no should already tolerate
  «sì»/«no» so 1b doesn't need re-touching when translation lands.
- The privacy/consent frame (step 3). No commits, no daemon restarts, no `--apply` runs, no
  status-doc edits (the QM reconciles).
