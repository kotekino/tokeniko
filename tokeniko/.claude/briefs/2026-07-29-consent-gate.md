# Brief: the consent gate — privacy/consent (2026-07-29, §1 step 3, the chapter's last brick)

**To the 1st Officier, from the QM.** This closes §1. It is the first design in tokeniko whose
constraint is **ethical** rather than logical or geometric: before a stranger's words may reach a
third party, that stranger must have said yes. The laws of the ship apply in full.

**Scope split (read this first).** You build the MACHINERY. The **consent text is FROZEN** — it is
the Captain's, reproduced verbatim in §6 below; do not reword it, do not "improve" it, do not
translate it. The **server-side configuration is the Captain's hand** (channel permissions, role
ordering, the Developer-Portal intent toggle) — you write the runbook section for it, you do not
and cannot perform it. **You never commit.**

## Why (the design spine)

A user's sentence reaches Anthropic through more paths than translation. **rag1 (the normalizer)
fires on any STUMBLING parse** — a native English speaker with typos touches the cloud. So consent
cannot be a just-in-time offer at the moment translation would help; it must be a **precondition of
talking at all**.

The enforcement must be **leak-proof by construction**, not by discipline. Per-path checks are
correct until the day someone adds path number six. Every Claude call in this codebase already
funnels through ONE function — `rag_call` (`lib/rag/client.py:55`) — so the gate goes there, and
the question it asks is not *"which instrument is this?"* but **"whose words am I about to send?"**

That framing catches a back door a direction-based rule would miss, and it is the single strongest
argument for this design: **the «did you mean…?» ask contains the user's own sentence.** It is
classified as *outbound* — tokeniko's own speech — but the payload literally carries the user's
words back out. Under "inbound gated, outbound free", an opted-out Italian speaker's sentence ships
to the cloud through the localizer. Under the payload rule it is gated automatically, no special
case required. **The honest unit of privacy is the sentence, not the direction of travel.**

## The Captain's rulings

- **Route C — a gated `#privacy` channel.** A newcomer sees ONLY `#privacy`; two buttons; **either
  answer unlocks the server.** Consent is mandated at joining and delivered by *server furniture*,
  not by tokeniko asking. (Rules Screening was rejected — it can only express accept-or-leave.
  Discord Onboarding was rejected — it requires Community enablement and **cannot re-ask existing
  members**, which collides with the re-consent rule below.)
- **Unasked behaves exactly as denied.** Three states, two of which are identical at the gate.
  Nothing leaks in the window between someone's first word and their answer.
- **Bluesky is OUT of this frame entirely.** His reasoning, and it is right: a bsky post is
  *already published to the world* and we are one reader among thousands — the expectation of
  privacy was settled by the act of posting. Consent belongs to the closed room. Do not add a flag,
  a prompt, or a gate on the ATProto path.
- **Change the text → erase every consent and ask again.** Non-negotiable, and the mechanism makes
  it nearly free (§4).
- **The legal text is ENGLISH ONLY**, now and for any future legal document. One authoritative text
  means no translation discrepancy. Do NOT curate `#privacy` scaffolds in other languages.
- **The microscope is out of the NOTICE** — a debug instrument, disabled before the public opening,
  so it is not described to users. **QM's reading, flagged to him: out of the notice is not out of
  the gate.** Build it gated (§5, row 7) — it costs one kwarg and gives the process control a code
  backstop. If he overrules, the change is deleting one argument.

## Build

### 1. The gate — `lib/rag/client.py`

`rag_call` gains a **REQUIRED keyword-only argument**, no default:

```
async def rag_call(spec, user, *, subject_uid: Optional[str], client=None)
```

Required-with-no-default is the whole point: a future instrument **cannot be added without its
author consciously deciding whose words it carries.** `subject_uid=None` must be typed out. This is
the leak-proof property expressed in the signature rather than in a comment. Every existing call
site must therefore be updated (§5) — that is intended, not collateral.

Semantics:
- `subject_uid=None` → the payload is tokeniko's own content → proceed.
- `subject_uid="<uid>"` → consult the consent reader → proceed only on an explicit **True**.

**The consent reader is INJECTED**, following this codebase's established idiom (the evaluator's
`relations=`/`part_of=`/`antonyms=` readers). `lib/rag/` stays DB-agnostic; the process wires the
real reader at init. **The default reader denies everything** — an unwired process is a silent
process, never a leaking one. Log a denial at INFO as `[rag:<name>] denied — no consent for <uid>`;
it must be visible without being alarming.

Return `None` on denial — the existing "graceful None, never raises" contract. Every call site
already handles `None`; verify each one, do not assume.

### 2. The mirror — `lib/core/memory.py` + `lib/core/models.py`

Three fields on `MEMStakeholder`, beside `trust`/`imprint`:

- `rag_consent: Optional[bool] = None` — None = unasked = **denied at the gate**.
- `consent_at: Optional[int] = None` — epoch seconds.
- `consent_text_version: Optional[str] = None` — which text they agreed to.

**Do NOT resolve through `canonical_uid`.** Trust unifies a soul's channel bodies; consent
deliberately does not — it is an act performed *in a room*, and agreeing on Discord is not agreeing
elsewhere. This is a deliberate asymmetry with the trust ledger; note it in the model comment so a
future reader does not "fix" it.

Do NOT create a consent-episodes collection. The trust ledger earned its collection; this does not
yet. Three fields make the record honest at almost no cost.

### 3. The Discord adapter — `lib/discord/`

Verified against live documentation 2026-07-29; none of this is guessed.

- **`constants.py`** — `intents.members = True`. This is a **privileged** intent: it must ALSO be
  toggled in the Developer Portal (Bot → Privileged Gateway Intents), exactly like `message_content`
  already is. Extend that existing comment rather than writing a new one. Add `MANAGE_ROLES`
  (`1 << 28`) to `INVITE_PERMISSIONS`; update the arithmetic comment.
- **`client.py:42`** — `discord.Client` is constructed directly, so there is no `setup_hook` to hang
  persistent-view registration on. Add that seam (subclass, or assign the coroutine to the instance
  — your call, whichever reads more like the surrounding code).
- **`models.py`** — `DiscordMessage` needs no consent field. The engine reads the mirror, never the
  message. Two sources of truth is how they drift.

### 4. The `#privacy` view — a new module under `senses/`

**THE TRAP, and a hard acceptance criterion.** A plain `View` dies when the daemon restarts — and
restarts are routine (every deploy, every `task senses`). After one, the buttons would silently do
nothing and clicks would land on a message discord.py no longer recognises. All three conditions
are required:

1. `timeout=None` on the view;
2. an explicit `custom_id` on **every** component (include the text version, e.g.
   `consent:v1:allow` / `consent:v1:deny`);
3. re-registered via `Client.add_view()` **in `setup_hook`, not `on_ready`.**

discord.py raises `ValueError` if (1) and (2) are unmet — a loud failure, good. **(3) fails
silently** — that is the one to guard with a test.

Behaviour:
- **Click** → assign this button's role, remove the other, write the mirror, reply **ephemerally**
  confirming the choice in one sentence. Ephemeral: the channel does not become a log of who chose
  what.
- **Assignment fails** (hierarchy misconfigured → `discord.Forbidden`) → tell the user plainly that
  it did not work, write **NOTHING** to the mirror, log an ERROR naming the likely cause. Fails
  closed.
- **`on_member_update`** → reconcile the mirror from the event's roles array (the payload carries
  it; no fetch needed).
- **`on_member_remove`** → mirror to `None`. Consent was given in the room; leaving withdraws it.
- **Startup reconciliation** — sweep guild members once at `setup_hook` and reconcile the mirror
  against actual roles. Cheap on a small server, and it makes the mirror **self-healing** rather
  than merely hopeful: it repairs a hand-edited role, a missed event, or a restart-window gap.
- **A re-consent helper** — an admin-only path (or a documented script) that strips both roles from
  all members and clears every mirror, for when the text version bumps. This is what makes the
  Captain's rule cheap; it does not need to be pretty, it needs to exist and be documented.

**Role hierarchy is a hard constraint, quoted from Discord's docs:** *"A bot can grant roles to
other users that are of a lower position than its own highest role."* `MANAGE_ROLES` alone is not
enough — tokeniko's own role must sit ABOVE both consent roles. Server-side, the Captain's hand;
your job is the runbook line and the `Forbidden` handling.

### 5. The call-site audit — all 9 sites, each decided

Every one must be updated (the argument is required). Classify by **whose words the payload
carries**, not by direction:

| # | Site | Instrument | `subject_uid` |
|---|---|---|---|
| 1 | `lib/llc/normalizer.py:357` | RAG1_NORMALIZER | **the speaker** — their raw sentence |
| 2 | `lib/llc/language.py:162` | RAG4_TRANSLATE_IN | **the speaker** |
| 3 | `lib/llc/language.py:163` | RAG4_RENDER_IN | **the speaker** |
| 4 | `lib/llc/language.py:192` | RAG4_TRANSLATE_IN (round-trip) | **audit** — trace what text this verifies; if it is tokeniko's own composed reply, `None`; if it re-sends the user's words, the speaker |
| 5 | `lib/llc/language.py:182` | RAG4_TRANSLATE_OUT | **conditional — THE BACK DOOR.** `None` for ordinary replies; **the speaker** whenever the payload embeds their words (the «did you mean…?» ask). If threading that distinction is awkward, pass the speaker — over-gating costs a localized reply, under-gating costs the whole design. |
| 6 | `senses/outbound.py:52` | RAG2_OUT | **same conditional as #5**, same tie-break |
| 7 | `senses/microscope.py:139` | RAG3_JUDGE | **the speaker** (see the ruling above — QM's reading, one kwarg to reverse) |
| 8 | `senses/blog.py:526` | BLOG_POLISH | `None` — **but AUDIT and report**: confirm a blog draft cannot contain a verbatim user quotation. The derivative line is *verbatim never leaves; ideas tokeniko formed are his own*. If a draft can quote, say so in your report; do not silently gate it, and do not silently leave it. |
| 9 | `lib/llc/decompiler.py:157` | RAG2_DECOMPILE | **audit** — trace the callers. A symbolic rendering of a user's compiled sentence is close enough to verbatim to gate; a debug round-trip on tokeniko's own content is not. Report what you find. |

Rows 4, 8 and 9 are **investigations, not instructions.** Report what you find; if the honest answer
differs from my guess, take the honest one and say so.

### 6. The consent text — FROZEN, copy verbatim

Stored as `v1`. Where it lives in code is yours to choose (a module constant reads best); the
*characters* are not yours to choose.

```
### Before we talk

tokeniko is an experiment: a small artificial mind that reads what you write, tries to understand
it, and remembers.

**What happens to your words, always.** He stores them, and what he understood from them,
permanently, on a private machine in a house in Osaka, Japan — not in the cloud. He is built to
remember; that is the point of him. Your messages are never sold, never advertised against, and
never published. He does write publicly about what he is learning — those are his own thoughts, not
your words.

**The one choice you have to make.** When a message is badly typed, or written in a language other
than English, tokeniko can only understand it by sending **that message's text** to a service run
by **Anthropic**, a company in the United States. Nothing else travels with it — not your name, not
your history, not your other messages.

Anthropic states that data sent this way is not used to train their models, and is deleted within
30 days — or kept up to 2 years if their automated safety systems flag it.

- **Allow the translator** — tokeniko can understand you when you write in your own language, or in
  a hurry, and can answer you in your language.
- **Keep my words here** — nothing of yours ever leaves this machine. tokeniko will understand
  clear English only, and will tell you honestly when he cannot understand you.

**Either choice lets you in.** You can change your mind whenever you like: come back here and press
the other button. Changing it stops anything further from being sent — anything already sent has
already been sent.
```

Button labels: **"Allow the translator"** and **"Keep my words here"**. Both name a *gain* — that is
deliberate and approved; do not "balance" them into allow/deny.

### 7. What denial actually does — verify, do not build

Every blocked path must land on a fallback that **already exists and is already tested**. Confirm
each, and report any that does not hold:

- rag1 denied → the raw parse stands unchanged (today's `RAG1_DISABLED` behaviour,
  `tests/test_translator.py:94`).
- rag4-in denied → the **local** skeleton detector still names the language → the curated native
  admission fires. Zero cloud calls. This is what lets an opted-out Italian be told, *in Italian*,
  that he cannot be understood — the English-only notice's gap, closed by machinery that already
  shipped.
- outbound denied → the scaffold ships verbatim, already a first-class path.

**The gate must introduce no new failure modes; it only routes to old ones.** If you find a path
where denial produces silence, a crash, or an English wall where a native admission was possible,
that is a finding — report it before working around it.

## Tests — `tests/test_consent.py` (new)

1. **Unasked denies** — mirror `None` → each user-carrying instrument returns `None`, no HTTP.
2. **Denied denies** — explicit `False`, same.
3. **Allowed proceeds** — `True` → the call is made (fake client).
4. **Unwired reader denies** — no reader configured + a `subject_uid` → denied. The fail-closed
   default.
5. **`subject_uid=None` proceeds** with no reader — tokeniko's own content is never gated.
6. **THE BACK DOOR** — a «did you mean…?» ask for a denied user makes **no** cloud call and still
   produces a reply.
7. **Persistent view** — `timeout is None`, every child has a `custom_id`, and the view is
   registered from `setup_hook`. Guards the silent failure.
8. **Flip** — allow → deny → allow; the mirror follows, `consent_at` moves.
9. **Startup reconciliation** — a mirror contradicting the roles is corrected by the sweep.
10. **Leave clears** — `on_member_remove` → mirror `None`.
11. **Assignment failure fails closed** — `Forbidden` → mirror untouched.

Discord objects are faked; no live gateway in tests. Sandbox DB as always.

## Runbook — a section in `doc/ref/deploy-body.md`

The Captain's-hand steps, written so he can follow them without reading code: create the two roles;
place tokeniko's role **above** both; create `#privacy` visible to `@everyone` with the rest of the
server visible only to the two consent roles; toggle **SERVER MEMBERS** in the Developer Portal;
re-invite the bot with the new permission integer. Note that **a photo of the machine will be
pinned** in that channel once the hardware arrives and is painted — the channel works without it.

## Out of scope — do not do these

- Do not write, reword, or translate the consent text.
- Do not touch the ATProto/Bluesky path.
- Do not build a consent-episodes collection.
- Do not add a language picker or multilingual `#privacy` copy.
- Do not perform any server configuration.
- Do not commit.

## Gates

`PYTHONPATH=. ../.venv/bin/python -m pytest tests/ -q` fully green, plus the new file. Report: the
audit findings for rows 4/8/9, anything in §7 that did not hold, and any place where the frozen text
did not fit the medium (Discord's 2000-character message limit is the obvious one — if it does not
fit, **report it, do not edit the text**).
