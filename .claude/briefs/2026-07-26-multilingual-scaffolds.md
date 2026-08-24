# Brief: multilingual scaffolds — a native voice per language (2026-07-26, §1 step 2b)

**To the 1st Officier, from the QM.** Promoted from `doc/parked.md` by the Captain's LIVE TEST
today: he spoke Italian and the *verdicts were right but the language was wrong* — «I cannot tell;
I lack the knowledge» and «because…?» came back in English while «sì — ne sono certo» came back in
Italian. This closes that. The laws of the ship apply in full.

**Scope split (read this first): you build the MACHINERY, the QM writes the TEXT.** The curated
scaffold rows in it/es/fr/de are prose curation and are the QM's hand (a separate seed script,
`scripts/seed_scaffolds_multilingual.py`, arriving in the same tree — do NOT write it, do NOT run
it). You own the model field, the shelf gate, the carrier, and the tests.

## Why (the diagnosis behind it)

`_localize` ships the target language only if the round trip is word-perfect OR `/voice/verify`
passes — and `verifier_voice` REFUSES an unsound raw. Every short curated reflex («hello!»,
«because…?», «I do not know») is a fragment, hence unsound BY CONSTRUCTION, hence unverifiable —
so it falls back to English unless the round trip happens to be lossless. Live, that hit greet,
answer_idk and why.

**The deeper point (the design spine): the zip-verifier is the wrong tool for a scaffold.** It
exists to stop meaning drift in DERIVED content. A scaffold is our OWN curated fixed string —
rendering it in another language is a curation problem, not an epistemics problem. So we curate the
rows per language instead of translating our own text at runtime: **zero cloud calls, zero
verification, zero latency, and a genuinely native register** («non lo so» is what an Italian
actually says; a translation of «I cannot tell; I lack the knowledge» never lands that way).
The Captain's framing: tokeniko is his TWIN and he is Italian — Italian is not a foreign language
tokeniko translates into, it is co-native.

## The Captain's rulings

- **Languages**: italian, spanish, french, german, english (english = today's rows, `lang="english"`).
- **v1 FENCE — slot-less categories only** (the same discipline as the mimicry's slot-less v1): the
  12 reflex categories that need no slot translation — `greet`, `welcome`, `farewell` (their only
  slot is `{name}`, a proper noun: language-neutral), `answer_yes`, `answer_no`, `answer_idk`,
  `answer_no_contradictory`, `agree`, `goodnight`, `speakup_inconsistent`, `clarify_conflict`,
  `concede_plain`.
- **The other 10 categories keep TODAY'S behavior**: they carry derived slots (`{belief}`,
  `{topic}`, `{notion}`, `{retracted}`, `{value}`, `{absurd}`/`{premises}`, `{hedge}`,
  `{weakened}`) whose content is stored English — they compose in English and go through the
  existing outbound translator, **for consistency** (his explicit ruling: the slotted ones still
  get translated, so a reply is never half-rendered by a different mechanism).
- **Gender**: curate AROUND grammatical gender where possible; masculine where unavoidable (he is
  «tokeniko», the twin of an Italian man). That is the QM's curation problem, not yours.
- **BLOG scaffolds stay English** (28 categories, `blog_*`) — the public journal's language is fixed.

## Build (machinery only)

### 1. The model — `lib/core/memory.py`

`MEMScaffold.lang: str = "english"` — the row's language. Defaulting to english means **every
existing row keeps working untouched** (no migration, no recompile). Document it in the model's
comment block in the file's voice.

### 2. The shelf gate — `lib/core/voice.creative_compose`

The reader already gates by category / enabled / slots / bands / `scope` (the mimic scope). Add the
language gate with the Captain's **FALLBACK CHAIN**:
1. rows whose `lang` == the requested language → if any, use that shelf;
2. otherwise **fall back to the english shelf**, exactly as today (which the outbound translator
   then handles as it does now — the translator becomes the FALLBACK layer, never the primary path).
`creative_compose` gains a `lang: Optional[str] = None` parameter (None ⇒ english ⇒ byte-identical
to today). Keep the never-mute discipline: an over-narrow gate must degrade to a wider shelf, never
to silence, and the `_FALLBACK` hardwired strings remain the floor.

### 3. Threading the room's language to the composer

The room (`MEMExchange.lang`) is read by `senses/outbound._room_language`, but composition happens
EARLIER, in `brain/behavior.plan_action` → `brain/compose.compose_raw` → `creative_compose`.
Thread the language the same way `target` was threaded for the mimic scope (2026-07-24): resolve the
room for (canonical target uid, channel id) at plan time and pass its `lang` through
`compose_raw(..., lang=…)`. **If the channel id is not available at plan time, STOP and report** —
do not invent a second source of truth for the room key (`io.exchange_channel_key` is the one
definition).

### 4. The carrier — `senses/outbound.py`

A reply already composed in the room's language must NOT be translated again. Pass the composed
row's language forward (or re-derive it) so `_localize` becomes a **no-op when the text is already
native**. The cheapest honest signal is preferable to a guess: if you cannot thread the row's
language cleanly, report the seam rather than sniffing the text. English rooms and unthreaded paths
must stay byte-identical to today.

### 5. Tests (sandbox, sibling style)

The lang gate (an italian row is picked for an italian room; an english room never sees it; a
category with NO italian row falls back to the english shelf) · `lang` defaults to english so every
existing row and every existing test is untouched · the never-mute floor (no rows at all → the
hardwired `_FALLBACK`) · the threading (a plan for an italian room composes from the italian shelf)
· the carrier no-op (a native row is not re-translated; an english row in an italian room still is)
· the slotted categories still compose in english and still route to the translator (the Captain's
consistency ruling) · blog composition untouched. Full gate foreground, `pgrep -f pytest` first.

## Out of scope (do NOT build; report if tempted)

- **The curated TEXT** — the QM's seed script (`scripts/seed_scaffolds_multilingual.py`). Do not
  write it, do not run it, do not `--apply` anything (the Captain's hand).
- The slotted categories' native rendering (the mixed curated-frame + English-slot problem — its
  own design session).
- Blog scaffolds; the privacy frame (§1 step 3).
- No commits, no daemon restarts, no status-doc edits (the QM reconciles).
