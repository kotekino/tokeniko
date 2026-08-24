# Brief 1a: the per-user conversational-context room + the "did you mean?" ASK (2026-07-25)

**To the 1st Officier, from the QM.** The first brick of roadmap §1 (the per-user conversational
context + multilingual chapter), designed with the Captain today. This is **1a — the room + the
ask**; a sibling brief (1b) adds the ANSWER binding right behind it, so 1a is a deliberate
stepping stone: tokeniko learns to ASK «did you mean X?» and to hold the pending state, but the
yes/no/restate RESOLUTION is 1b. The laws of the ship apply in full.

## The design (the Captain's rulings)

A **per-`(user, channel)` conversational-context room** we don't yet hold first-class. A REFERENCE
model (the author's "partial A"): a small Mongo doc per pair storing LIGHT state that REFERENCES
timeseries items by id — NO zip/text duplication, one read per tick, matching the `MEMReductio` /
trust-episode precedent (store the relation + refs, never copy content). The two-tier verifier
spine at the ears: *asking ≠ believing* — the strong wall (2026-07-24) still trashes a drifting
polish; a polish that is a COHERENT, semantically-plausible alternative reading is neither believed
nor discarded but OFFERED as a question. Nothing is believed without the human's confirmation (1b).

## Build

### 1. The room — a new model + collection (`lib/core/memory.py` + `models.py` + `io.py`)

`MEMExchange` (name is the QM's proposal — rename freely if a better one fits): the distilled
current state of one exchange.
- `user_uid: str` (the CANONICAL soul uid — resolve through `canonical_uid` as the trust ledger
  does), `channel_id: str` (the Discord channel id from the item's `metadata`; DMs have one too).
- `pending: list[MEMPending]` — usually 0–1. `MEMPending` = `{kind: str, ref_item_id: str,
  opened_at: int, expires_at: int, status: str}` (`kind="did_you_mean"` for v1; `status` a small
  enum `open|resolved|lapsed` — 1a only ever writes `open`, 1b resolves/lapses).
- `reply_tempo: float` (seconds; the EMA, see §3), `last_turn_at: int` (the previous turn's epoch,
  for the EMA gap), `updated_at: int`.
- Register the Bunnet `Document` (`TKExchangeDoc`, collection e.g. `exchanges`) in `init_io`
  beside the other MEMORY-db docs; a compound index on `(user_uid, channel_id)`. Keep any
  recursive-model `model_rebuild()` discipline if the pending list needs it.
- A tiny reader/upsert helper (`io.get_exchange(user_uid, channel_id)` fetch-or-create, `.run()`
  discipline) — the brain's one entry point to the room.

### 2. The two-tier floor at the ears (`lib/llc/normalizer.py` + `api/main.py`)

Grow the verifier into a **three-way verdict** — `ACCEPT | ASK | DISCARD` — instead of today's
`(ok, note)`:
- **ACCEPT** = passes the current strict `verifier_preserves` (sound leaves preserved + mood gate
  + semantic floor). Behaves exactly as today (the polish becomes `normalized`).
- **ASK** = NOT accepted, BUT the polish is a coherent offerable reading: structurally SOUND (no
  unsound leaves), MOOD-preserved, and semantically PLAUSIBLE — `verifier_semantic_similarity` in
  `[RAG1_ASK_FLOOR, RAG1_SEMANTIC_FLOOR)` (a second, lower env floor). **Calibrate `RAG1_ASK_FLOOR`
  against real specimens and report the measured margins** (the officer's discipline — as the
  semantic floor was calibrated 2026-07-24). A genuine ambiguous-tidy should land ASK; the
  prompt-soup hallucination (mood flip / far drift) must land DISCARD.
- **DISCARD** = the current reject-and-trash (raw parse stands; the `ears-hallucination` microscope
  lead is still logged — a discarded polish IS a caught drift).
- At `/input` (the `rag1_rejection` seam): on **ASK**, store the candidate on the item — a new
  `MEMItem.suggested_reading: Optional[str]` (the polished text; the item is stored anyway, so the
  reading lives exactly once, here — the room only references its id). On **ACCEPT/DISCARD**,
  unchanged. Do NOT open the pending here — the BRAIN owns the reaction + conversational state
  (below); `/input` only flags the candidate.

### 3. `reply_tempo` — the adaptive rhythm (`brain/`, updated in thinking)

On each processed turn from a user in a channel (the `context_add` seam in `think_one`), update
that exchange's tempo O(1):
- the sample = the gap since `last_turn_at` (the previous turn in this exchange), **outlier-capped**
  (ignore a gap above `MIMIC_`-style ceiling, e.g. `EXCHANGE_GAP_CEIL` default 3600s — an
  overnight/at-work silence is not conversational rhythm and must never poison the EMA).
- `reply_tempo = α·sample + (1-α)·reply_tempo` (α env, ~0.3); seed on first contact from a default.
- persist `last_turn_at`, `updated_at`. This is the only per-turn write to the room — keep it cheap.
- (Prefer response-latency — gap when the previous turn was tokeniko's — if it's clean to detect;
  else the plain inter-turn cadence is an accepted proxy. Report which you chose.)

### 4. The ASK reaction (`brain/thinking.py` + `behavior.py` + compose)

In `think_one`, when a processed item carries `suggested_reading` (and is not a question/social):
- **open the pending** in the room: append a `MEMPending{kind:"did_you_mean", ref_item_id: item.id,
  opened_at: now, expires_at: now + clamp(k·reply_tempo, EXCHANGE_WIN_MIN, EXCHANGE_WIN_MAX),
  status:"open"}` — `k` env (~3–5×); first-contact default window GENEROUS (a clarification
  deserves more patience than an ambient beat — longer than the 600s momentum). Opening is
  ONCE-per-item (thinking's source-cursor already advances once per item; the pending is the 1b
  hook, not a re-ask guard).
- **spawn the ask idea**: a new `EvalToken.DID_YOU_MEAN` → a behavior rule → `tokeniko:ask` (or a
  dedicated `clarify`-style action — follow the curiosity-«why» / cross-item-«clarify» reflex
  pattern), directed at the asker (`target=item.sourceId`), carrying the reading as the compose
  slot. A new compose category **`did_you_mean`** with a `{reading}` slot (add to `voice._FALLBACK`
  + the `brain/compose` router), e.g. «did you mean: {reading}?». The ask REPLACES the generic
  unknown-«why» for this item (do not fire both — route the did-you-mean instead of the eval:unknown
  reflex when a `suggested_reading` is present).
- **directedness-gated by construction**: the ask's urge × the item's `directedness` vs the act
  threshold means an ambient (0.6) stumble may stay silent — the existing mechanism, no special
  case. Seed the `eval:did_you_mean → tokeniko:ask` behavior rule (extend
  `scripts/seed_behavior_rules.py`; SURFACE the seed, the `--apply` run is the Captain's hand).

## Tests (sandbox, sibling style)

The room (create/fetch/upsert; the `(user_uid,channel_id)` key) · the tempo EMA (a sample updates
it; an over-ceiling gap is ignored; first-contact seeds the default) · the three-way verdict
(ACCEPT unchanged; a coherent ambiguous tidy in the ask band → ASK; the prompt-soup specimen →
DISCARD; report the margins) · `/input` stores `suggested_reading` only on ASK · the reaction
(an item with `suggested_reading` opens exactly one pending + spawns the did-you-mean idea, not the
unknown-why; expiry = clamp(k·tempo)) · directedness gating (ambient stays quiet). Existing
translator/thinking/compose tests stay green. Full gate foreground, `pgrep -f pytest` first.

## Out of scope (1b owns it — do NOT build; report if tempted)

- The ANSWER binding (yes/no/restate/lapse resolution of the pending) — brief 1b.
- Multilingual translation + the conversation-language tenant (step 2 of the chapter).
- The privacy/consent frame (step 3).
- No commits, no daemon restarts, no `--apply` seed runs, no status-doc edits (the QM reconciles).
