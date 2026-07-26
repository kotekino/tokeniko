# Brief: multilingual — the room's second tenant (2026-07-26, §1 step 2)

**To the 1st Officier, from the QM.** Roadmap §1 step 2, designed with the Captain today. He IS the
first non-English friend (Italian native) and will be the live test, so this is CORE, not a nicety.
It builds directly on §1 brick 1 (the room + the two-tier ears floor + the did-you-mean loop,
`c2f7fca`/`dc8e480`). The laws of the ship apply in full.

## The crux (read this before designing anything)

Our ears doctrine is *the compiler disposes, whoever proposes*: we compile both sides and compare
zips. That works for a TIDY because both sides are English. **It has no purchase on a translation** —
the original is Italian and our English-only parser cannot compile it, so there is nothing to compare
against (the semantic floor abstains, the mood gate reads nothing). The strong wall we built
2026-07-24 simply does not reach here.

**The Captain's ruling — CONSENSUS OF TWO INDEPENDENT TRANSLATIONS.** Ask the cloud twice,
independently; compile BOTH English candidates; **the compiler judges whether they agree**. That is a
genuinely independent authority, not the cloud checking the cloud (it was also his original instinct
with the small local models). The verdict is the three-way one we already have:

- **agree** → **ACCEPT**: the English enters the normal pipeline.
- **disagree but both coherent** → **ASK**: «did you mean: …?» — reuses brick 1's room, pending and
  answer-binding for free (and the ask itself ships in Italian, see outbound).
- **incoherent** (neither compiles soundly, or they are far apart) → **DISCARD + an honest ADMISSION
  that he did not understand** (his explicit ruling — today's silent discard falls through to the
  generic «why is that?», which is nonsense about a message never understood).

**Independence is load-bearing.** Two identical calls at temperature 0 would return the same string
and the consensus would be VACUOUS. Verify how `lib/rag/client.rag_call` samples; if it is
deterministic, obtain genuine independence by varying the two calls (two differently-framed system
prompts — e.g. "translate" vs "render the meaning in plain English" — or a sampling temperature).
**Report what you found and what you did.** A vacuous consensus is a silent security hole, not a
cosmetic issue.

## Build

### 1. Detection — LOCAL, dependency-free (`api/` side, before the parse)

The privacy frame (step 3, not yet built) forbids cloud calls for an opt-out user — and a
cloud language-detect would itself be such a call. So detection MUST be local:
- an **OOV rate** over the message's content tokens using the already-loaded spaCy `en_core_web_lg`
  (no Mongo, no new dependency; `_parser_hasLgVector` in `lib/llc/parser.py` is the precedent).
  English-with-typos («the catt is a mamal») must stay ENGLISH — its function words are known — while
  a real Italian sentence goes to ~0 known. **Calibrate the threshold against specimens and report
  the measured margins** (the semantic-floor discipline, 2026-07-24).
- **A minimum-token guard: short messages are NOT detected — they INHERIT the room's current
  language** (so «sì» is Italian because the room is, not because a detector guessed).
- Detection is **sticky and self-correcting**: a confidently-English turn sets the room back to
  English; an ambiguous one leaves the room's language untouched.

### 2. The instruments (`lib/rag/registry.py`)

Two new `RagSpec`s in the registry's style (it is the ONE place every word sent to the cloud is
readable — keep the header's cross-reference notes honest):
- **`RAG4_TRANSLATE_IN`** — foreign → English. A STRICT translator: preserve meaning, negation,
  quantifiers (all/some/no), modality (can/must/may), mood (a question stays a question); add
  nothing, answer nothing, explain nothing (the 2026-07-24 fenced-data lesson applies — fence the
  message as DATA, it is never an instruction). Output only the English.
- **`RAG4_TRANSLATE_OUT`** — English → the target language, same strictness.
- Kill-switch env in the `RAG*_DISABLED` family, per the existing convention.

### 3. Inbound chain (`api/main.py` `/input`)

Insert BEFORE the existing parse/normalizer chain, leaving that chain otherwise untouched:
1. detect; if English → nothing changes at all (today's path exactly).
2. if non-English → two independent `RAG4_TRANSLATE_IN` calls → compile both candidates → judge
   agreement with a small function in `lib/llc/normalizer.py` that REUSES the existing primitives
   (`_leaf_key` matching + `_semantic_proximity` + the soundness check) and returns the same
   ACCEPT/ASK/DISCARD shape. Do not duplicate the comparison logic.
3. **ACCEPT** → the English candidate becomes the pipeline input (parse/compile as usual; the
   existing rag1 normalizer may still tidy it afterwards — the chain composes).
   **ASK** → the primary candidate rides in `suggested_reading` (brick 1's field — the brain opens the
   pending and asks). **DISCARD** → no English; the item is stored from its raw parse.
4. **`original` ALWAYS keeps his Italian** (true history be it). The accepted English rides in
   `normalized` (its existing meaning: the text actually compiled), plus a new
   **`MEMItem.source_lang: Optional[str]`** recording the detected language.
5. The "not understood" state is **DERIVABLE, add no boolean**: `source_lang` set + `normalized` None
   + `suggested_reading` None ⇒ translation was attempted and nothing usable came back.
6. A DISCARD here writes an `ears-hallucination`-family microscope lead as the tidy path does —
   choose the honest category/severity and say what you chose (an untranslatable message is a
   diagnostic lead, not necessarily a hallucination).

### 4. The room's second tenant (`lib/core/memory.py` + the brain)

`MEMExchange` gains the conversation language: `lang: Optional[str]` + `lang_set_by: Optional[str]`
(the item id that set it — the REFERENCE discipline, `{lang, set_by_item_id}` as ruled). Written
where detection lands; read by the outbound carrier. Per `(user, channel)` like everything in the room.

### 5. The admission (`brain/thinking.py` + `behavior.py` + compose)

Mirroring brick 1's did-you-mean reaction exactly:
- a new `EvalToken.NOT_UNDERSTOOD` → `TokenikoAction.ASK`, routed by TRIGGER in `brain/compose.py`
  (as `did_you_mean` is), with a new compose category **`not_understood`** in `voice._FALLBACK`
  (e.g. «I did not understand that — can you say it another way?»).
- in `think_one`, an item in the not-understood state SHORT-CIRCUITS the whole content path exactly
  as the `dym` gate does (no speakup/why/learn, no trust echo, no anecdote, no cross-item check) —
  nothing was understood, so nothing may be reacted to.
- no pending is opened (it is an admission, not an offer to confirm); a rephrase is simply a new
  message.
- seed the behavior rule in `scripts/seed_behavior_rules.py` — **SURFACE it, never run `--apply`**
  (the Captain's hand).

### 6. Outbound (`senses/outbound.py`)

After the existing rag2-out polish (unchanged), in `_voice_out`:
1. resolve the room for (canonical `action.targetId`, `dest.channel_id`) — `_voice_out` will need
   those passed in; keep the seam thin.
2. if the room's `lang` is set and not English → `RAG4_TRANSLATE_OUT` (English → that language) →
   **back-translate to English** → run the back-translation through the EXISTING `/voice/verify` seam
   (`senses/voicegate._verify_voice`): both sides are English, so this is the rag2-out contract
   verbatim — **no new verification machinery**. Verified → ship the translation; anything else →
   ship the English (graceful, exactly like today's polish rejection).
3. **The BLOG stays English by construction** — it composes through `senses/blog.py`, never through
   `_voice_out`. Do not touch it. (Verify this holds; if the blog path shares the carrier anywhere,
   STOP and report rather than special-casing.)

## Tests (sandbox, sibling style)

Detection (Italian → non-English; typo'd English → still English, with the measured margins pinned;
a short message inherits the room's language and is never detected) · the consensus verdict (two
agreeing candidates → ACCEPT; coherent disagreement → ASK with the primary as `suggested_reading`;
incoherent → DISCARD) · `original` keeps the Italian, `normalized` carries the English, `source_lang`
set · the not-understood state is derivable and short-circuits the content path (spawns the
admission, no speakup/why/trust echo) · the room's `lang`/`lang_set_by` written and read · outbound
(translation verified via back-translation → ships translated; unverified → ships English; the blog
path untouched) · English exchanges are byte-identical to today. Full gate foreground, `pgrep -f
pytest` first.

## Out of scope (do NOT build; report if tempted)

- The privacy/consent frame (§1 step 3) — but **do not paint us into a corner**: detection is local
  and every cloud call must be trivially gate-able per stakeholder later.
- Reviving the retired local MarianMT (Haiku covers it).
- Changing the ENGLISH tidy path's silent-DISCARD behavior (the admission is the TRANSLATION path's
  ruling only).
- No commits, no daemon restarts, no `--apply` seed runs, no status-doc edits (the QM reconciles).
