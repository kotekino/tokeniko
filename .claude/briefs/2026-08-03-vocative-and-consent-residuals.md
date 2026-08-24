# Brief: the mention-vocative bug + three consent residuals (2026-08-03)

**To the 1st Officier, from the QM.** Four items, bundled into ONE trip and ONE gate run because the
gate costs ~17 minutes and cost is a design constraint. Item 1 is a **live bug corrupting real
input** and is the reason for the trip; items 2–3 are residuals from your own consent build, both
already ruled by the Captain; item 4 is the empirical record. The laws of the ship apply in full.

Your consent gate build is COMMITTED (`50f3541`) and live — the Captain restarted the daemons, the
sweep reconciled, the notice is posted in `#privacy`, and he has clicked ALLOW himself. All of item
1's evidence below was gathered from that live system.

---

## 1. THE MENTION-VOCATIVE BUG — the reason for this trip

**A statement addressed to tokeniko by @-mention has its SUBJECT silently replaced by tokeniko.**

Found live today. Four specimens, one variable isolated:

```
'tokeniko , the cat is a mammal'    -> ([the] cat be [a] mammal)   OK  cat.n.01 + mammal.n.01
'tokeniko the cat is a mammal'      -> (tokeniko be [a] mammal)    BUG subject stolen, cat LOST
'tokeniko il gatto è un mammifero'  -> (tokeniko be [a] mammal)    BUG (translation was PERFECT —
                                                    normalized: 'tokeniko the cat is a mammal')
'a feline is a mammal'              -> ([a] feline be [a] mammal)  OK  (no vocative at all)
```

**The comma is the only difference.** Multilingual is innocent — rag4 rendered the Italian
flawlessly, and the English parse then failed identically. Do not go looking in `language.py`.

**Why it matters more than it looks.** `@tokeniko` decodes to `tokeniko ` — a bare name, no
punctuation. Mentioning him is the MOST natural way anyone addresses him, and a stranger joining the
server will do it constantly. So for an unknown stretch of time, statements addressed to him by
mention have been compiled as claims ABOUT him. Two things kept it from being worse: the logic floor
REFUSED the false claim rather than storing it (he answered «that does not match what I know» — correct
reasoning on a corrupted input), and rag3 diagnosed it unprompted in the same minute:

> *"the subject 'il gatto' was lost: subject bound to tokeniko's identity instead of carrying
> cat.n.01... the predication now claims tokeniko is a mammal rather than the cat."*

**The mechanism.** `social_detect` (`lib/llc/social.py:51`) strips a leading «tokeniko» vocative —
but ONLY on the greeting path. A plain statement has no social head, so `social_detect` returns None,
nothing is stripped, and spaCy then reads `tokeniko the cat` as ONE noun phrase with *tokeniko* as
its head. The comma is what tells spaCy it is a vocative.

**THE FIX — the Captain's ruling, option A: fix it at the EARS, in the adapter.**

`_decode_mentions` (`lib/discord/client.py`, around line 39) knows it has just replaced `<@id>` with
a name. **If that mention LEADS the message and is not already followed by punctuation, insert a
comma.** This is not an inference — the wire told us it was an address rather than content, and we
are restoring the punctuation a human would have typed. That information exists at exactly this point
and is currently thrown away.

Constraints on the fix:
- **Only a LEADING mention.** A mention mid-sentence («I told @tokeniko yesterday») is content and
  must not be touched.
- **Only when punctuation is absent.** «@tokeniko, the cat…» and «@tokeniko: hello» are already fine;
  do not double it.
- **Any mention, or only tokeniko's own?** Your call, argued in your report. My lean is ANY leading
  mention — «@hellen the cat is a mammal» has the same shape and the same failure — but tokeniko's
  own name is the case we have evidence for. Take the narrower one if the broader has a downside I
  have not seen.
- **Do NOT touch the parser** (option B — strip a leading proper noun as a vocative regardless) was
  considered and rejected: without the mention signal it is guessing that a leading proper noun is an
  address, which is exactly the kind of inference that bites. If you find while building that A
  cannot work, report that rather than reaching for B.

**Verify the fix end-to-end**, not just at the unit: the fixed adapter output must compile to
`([the] cat be [a] mammal)`. A test that only asserts the string now contains a comma has not proved
the bug is dead.

---

## 2. THE MICROSCOPE'S DENIAL HANDLING — a permanent no-progress loop

Live symptom, every 60 seconds, forever:

```
[rag:rag3-judge] denied — no consent for 6a6aaf2ce133c5b8acf60c08
[rag:rag3-judge] denied — no consent for 6a6aaf2ce133c5b8acf60c08
```

That id is the **`unknown` stakeholder** — a placeholder for an unidentified source, not a person.
`judge()` returns None on a denial, and `microscope_pass` (`senses/microscope.py:191`) treats every
None as *leave unjudged, the next pass retries*. So denied items are retried forever, the queue never
drains, and the log fills indefinitely.

**The Captain's ruling (the QM's lean, approved): distinguish the two failures.** They wear the same
`None` today but are entirely different animals:
- **An API failure** (down / timeout / malformed) SHOULD retry — the next pass may well succeed.
- **A consent denial** will not change until a human presses a button. Retrying it every minute is
  pure waste.

So a denial must **mark the item as not judgeable and move on**, rather than retry. Shape is yours;
the constraint is that it must be **reversible** — if that person later consents, their items should
become judgeable again rather than being permanently written off. (A distinct verdict row, a
`skipped` marker, a reason field — whatever fits `TKZipDebugDoc` most honestly. It must not look like
a judged mismatch in any query that counts leads.)

**Also worth your judgement, and I want your opinion rather than a decision:** should a PLACEHOLDER
stakeholder have a consent state at all? `unknown` is not someone who can be asked. It may be more
honest to treat an unidentifiable source as *unjudgeable* rather than as *denied pending consent*.
Report what you find about where `unknown` sourceIds come from — if they are numerous, that is its
own finding.

---

## 3. ADMIN AUTO-CONSENT — ruled, with an honesty constraint

**The Captain's argument, and he is right:** admins BYPASS all channel permissions, so the `#privacy`
gate structurally cannot reach them. They would sit at *unasked* forever — not because they declined,
but because the mechanism cannot touch them. An act that cannot be forced needs another way to be
expressed, so the admin grant itself carries the meaning: *«our server, our rules — an admin can
administer the server AND thereby accepts our privacy terms.»* The population is two people who both
know the project.

**Build it:**
- `DiscordMember` gains `is_admin: bool` — the adapter reads it from the member's guild permissions
  (`administrator`). The adapter is the only layer that can see discord.py's resolved permissions,
  exactly as it is for `mentions_me`.
- In the reconciliation, an admin resolves to **allowed**, whatever roles they hold. An admin who
  explicitly holds the DENY role is a real conflict — my lean is that the **explicit role WINS** (a
  deliberate click is a stronger signal than a permission bit, and it preserves «you can always change
  your mind»), but argue it if you disagree.
- **THE HONESTY CONSTRAINT (mine, and non-negotiable): record it as auto-granted.**
  `consent_text_version = "auto:admin"` rather than `"v1"`, plus a distinct log line. The ledger must
  never claim someone pressed a button when nobody did — *true history be it* applies to consent
  records too. A later reader must be able to tell the two apart at a glance.
- The `_is_tokeniko` guard still wins over everything: his own account is never mirrored, admin or not.

---

## 4. THE EMPIRICAL RECORD — `doc/ref/test-feedback.md`

Add item 1's diagnostic in the file's established observed → diagnosis → action shape. **Include all
four specimens with their raw renders** — the isolation is the valuable part, and it is the cleanest
one-variable diagnostic we have run. Note explicitly that multilingual was cleared, so nobody
re-investigates the translator, and credit rag3: this is the microscope earning its keep on a bug
neither of us had noticed.

---

## Out of scope — do not do these

- Do not touch `lib/llc/language.py` or anything multilingual (cleared by the specimens above).
- Do not implement option B (the parser-side vocative strip).
- Do not restart the daemons — the Captain's hand, and they are LIVE right now.
- Do not commit or push.
- No `--apply` KB writes; sandbox DB only.
- Do not change the consent TEXT or its version.

## Gates

`PYTHONPATH=. ../.venv/bin/python -m pytest tests/ -q` fully green (784 + your new ones, 1 xfailed
expected). Report: the vocative fix's end-to-end verification, your call on any-mention vs
tokeniko-only, your opinion on the `unknown` placeholder question, the admin/deny-role conflict
ruling, and anything the brief did not cover.
