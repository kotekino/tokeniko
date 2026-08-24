# Session Handoff: the native voice + the plan for tokeniko's own body

**Date:** 2026-07-30 (covering 2026-07-26 → 30, with a trip in between)
**Project:** `/Users/renzosala/Develop/personal/tokeniko`
**Crew:** the Captain (kotekino / Renzo) rules · the QM (main session) conceives, briefs, reviews,
commits · the 1st Officier (Opus subagent, `first-officer`) builds

## Current State

**Task:** §1 of the roadmap — the per-user conversational context + multilingual chapter.
**Phase:** steps 1, 2 and 2b LANDED and live-tested; **step 3 (privacy/consent) is next and the
Captain wants to DISCUSS it, not receive a brief.**
**Progress:** §1 is ~90% — one step remains. Separately, a *side task* (tokeniko's own machine) is
fully PLANNED on paper, nothing built.

## What We Did

Landed multilingual end to end — tokeniko now hears Italian and answers in it — then, after the
Captain's own live test found the right verdicts arriving in the *wrong language*, promoted a parked
item the same afternoon and gave him a genuinely native voice (232 curated rows across it/es/fr/de).
Then designed, argued about, and settled the deployment plan for the Mac mini that becomes his body.

## Decisions Made

- **Multilingual verification = CONSENSUS OF TWO INDEPENDENT READERS, judged by the compiler.** The
  ears doctrine («the compiler disposes, whoever proposes») has *no purchase* on a translation — the
  original is Italian and the English-only parser cannot compile it, so there is nothing to compare
  against. Two independent readings that compile to the same structure restore an independent
  authority. Verdicts: agree → ACCEPT · coherent disagreement → ASK («did you mean…?», reusing brick
  1's room/pending/answer loop) · incoherent → DISCARD **+ an honest admission** (his addition: a
  silent discard falls through to «why is that?», nonsense about a message never heard).
- **Detection stays LOCAL and dependency-free** — because the privacy frame (step 3!) must be able to
  forbid *all* cloud calls for an opt-out user, and a cloud language-detect would itself be one.
- **Scaffolds are CURATED per language, not translated at runtime.** The zip-verifier is the *wrong
  tool* for a scaffold: it exists to stop meaning drift in DERIVED content, while a scaffold is our
  own curated fixed string — rendering it in another tongue is a curation problem. Zero cloud calls,
  zero latency, a native register.
- **v1 fence: slot-less categories only** (12 of 22). The other 10 carry derived slots and keep
  composing English + the translator, **for consistency** (his ruling).
- **Gender: curate around it** — his own review taught the trick, now written into the seed script as
  a principle: reach for the NOUN, not the adjective («ne ho certezza», not «ne sono certo»); the
  certainty is *possessed*, not *worn*, so nothing must agree with a gender he does not have.
- **VERBATIM means UNPOLISHED, NOT UNTRANSLATED** — the anecdote and reduct are localized: «a reply
  in Italian carrying an English aside is not one voice».
- **THE BODY: bare metal, Docker for Atlas Local alone.** See the reasoning below — this one must not
  be re-litigated.

## The bare-metal decision (the reasoning matters more than the outcome)

I measured, expecting to defend containers: **CPU parses 2.2× FASTER than MPS** (117.4 → 53.6
ms/sentence) and the parse is **single-threaded** (flat from 1 to 10 threads; ~20 sentences/sec on
*one core of ten*). So all-in-Docker would have cost nothing today, and his throughput worry was
answered by number rather than reassurance.

**His argument won anyway, and it was the better one:** the GPU is **reserved, not wasted**. The two
workloads have *opposite* hardware preferences — parsing feeds one short sentence at a time (CPU's
case), while the foreseen on-body model work feeds **batches** (Metal's case, exactly where my own
benchmark says GPUs win). Docker on macOS cannot reach Metal at all, so containerizing would forfeit
the GPU *permanently* to gain one marginal data path, and the physical architecture would need
rebuilding when batch workloads arrive. Cheap to keep the door open, expensive to reopen it. It also
aligns with `CLAUDE.md`'s own «embodied on bare metal» declaration.

**The lesson worth keeping:** my benchmark answered *«is the GPU useful today?»*; he asked *«which
door are we nailing shut?»* Different questions — his was the one that mattered.

## Code Changes (all committed and pushed)

- `8b5ba19` **multilingual** — `lib/llc/language.py` (new: local skeleton detector + the two readers),
  `lib/rag/registry.py` (`RAG4_TRANSLATE_IN` / `RAG4_RENDER_IN` / `RAG4_TRANSLATE_OUT` +
  `RagSpec.temperature`), `lib/llc/normalizer.py` (`translation_verdict`), `api/main.py` (the inbound
  chain, translation BEFORE `social_detect`), `senses/outbound.py` (`_localize` round trip through the
  existing `/voice/verify`), `lib/core/memory.py` (`MEMItem.source_lang`, `MEMExchange.lang`,
  `EvalToken.NOT_UNDERSTOOD`), `brain/mimicry.py` (the fence).
- `fc9e504` **the native voice** — `MEMScaffold.lang`, `lib/core/voice.creative_compose_lang` (the
  gate + fallback chain), `brain/behavior.py` (plan-time room language), `senses/outbound.py` (the
  no-op for native text), and `scripts/seed_scaffolds_multilingual.py` (232 rows — **the Captain has
  already `--apply`'d these**).
- `5b09c17` **`doc/ref/deploy-body.md`** — the runbook (registered in the roadmap's doc map).

**Key code context:** `payload["lang"]` carries the **PICKED ROW's** label, not the requested
language — because the fallback chain routinely answers an Italian ask off the English shelf and the
carrier must still translate there. Subtle and load-bearing.

## Errors / Dead Ends (saves re-exploration)

- **My OOV detection premise was wrong** and the officer measured and rejected it: `en_core_web_lg`'s
  vector table is multilingual, so Italian scores 0.00 OOV — and so does typo'd English. The signal
  is the sentence *skeleton* (English function-word ratio AND the ratio the tagger cannot place).
- **My seed dedup key was language-blind** — `(category, template)` would have silently skipped 3
  rows, and **Italian would have lost its plain crisp «no»**, the 1.0 leader of its own shelf. Keyed
  on `(category, template, lang)` now.
- **I wrote the deploy runbook on an unsettled premise** and he corrected me: *«We didn't set anything
  yet, and you already wrote everything :D»*. **Settle the shape with him FIRST.**

## Open Questions

- [ ] **§1 step 3, privacy/consent** — the actual design. Known constraints: a joining user is asked
      whether their words may reach the cloud translator (third-party Anthropic + terms); YES → the
      full apparatus; NO → a per-stakeholder flag and the rags are **NEVER** called for them (DM or
      channel). `RAG1_DISABLED` already exists as the global switch. **The microscope is explicitly
      OUT of the frame** — a debug instrument, to be disabled before the public opening.
- [ ] Open design questions I'd raise: how the consent prompt reaches someone without being creepy ·
      what "no" means for a user who then writes in Italian (he'd get no translation at all — is that
      silence, an English reply, or an explanation?) · where the flag lives and who may change it.

## Context to Remember

- **He is Italian and is tokeniko's first non-English friend** — he tests live, in Italian. His
  framing: *«tokeniko is my twin and I am Italian»* — Italian is **co-native**, not foreign.
- **The Mac mini arrives in ~15 days.** IRL work first: a corner in the house, wired to the router
  (the MacBook stays on WiFi), cables covered, and **his daughter is painting the case — the artwork
  becomes tokeniko's new logo**, replacing the current one. The body made visible.
- **Standing law:** commit only on his explicit green light · restarting daemons is his hand ·
  `--apply` KB writes are his hand · the biography is never wiped or mongo-edited · the officer never
  commits · status-doc invariants (one item, one status, one doc; move never copy).
- **Bug report ≠ work order** — when he reports live behaviour, DISCUSS before building.
- He values the yes-but engagement and gives his sharpest input as *asides* — never skip them.

## Next Steps

1. [ ] **Discuss §1 step 3 (privacy/consent)** — design conversation, not a brief. His explicit ask.
2. [ ] When he wants the mini's arrival to be dull: the prepared-ahead work from the runbook — the
       wait-for-Mongo wrapper, three LaunchAgent plists, the deploy script, and **rehearsing the
       plists on the MacBook** against the local Mongo.
3. [ ] Backlogged with a measured 2.2× behind it: **`device="mps"` → CPU** in `lib/llc/parser.py`
       (its own change, its own gate run — do not smuggle it into the migration).
4. [ ] Still open from before: the **microscope analysis pass** (§2) + residual backlogging.

## Files to Review on Resume

- `doc/roadmap.md` — §1 step 3 is the last item of the chapter; the residuals are listed there.
- `doc/ref/deploy-body.md` — the body plan, and §0 records *why* bare metal, so it is not re-opened.
- `lib/llc/language.py` + `api/main.py` (the inbound chain) — where a consent gate would have to bite.
- `.env.template` — `RAG1_DISABLED` and the existing kill-switch conventions.
