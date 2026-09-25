# parser/compiler — THE NAME QUESTION, REOPENED AND WIDENED, 2026-09-16 09:59

*The ambiguous markers closed with two errors, and both were «Anna». I parked them as «the
named-individual hole, which has its answer waiting». **The Captain refused the parking** and widened
the scope in the same breath:*

> *«Regarding names (personal names): as a general rule, I know that spacy (and spacy-stanza) can
> determine if a name is present. In tk1 we have a db of possible names (which is partial and we can
> reason over that). The casing (although it's not grant) is also an indicator. We should dedicate an
> entire point to name resolution: a public personality, a name of a company, a geographical location
> (for which we have in tk1 a very exhaustive location map, we should definitely reuse), a possible
> mini neural network (to start our ecosystem of mini nn, where a split decision should be taken and
> learning from experience).»*
>
> *«Note on that: the mini nn should be inside a framework that abstracts them, and we should
> introduce them exactly when a curation is not entirely possible, when the decisions can change over
> time.»*

**This is E3b, and E3 closes first.**

---

## WHY THE PARKING WAS WRONG, IN MY OWN TERMS

I wrote that the hole «already has its answer waiting — a type-centroid vector plus a context-scoped
identity». **That is the SHAPE of the answer and not the answer.** The shape says where a resolved
name goes; it says nothing about the four questions that have to be answered before anything is
resolved:

1. **Is this token a name at all?** («kotekino is my creator» — lower case, and a name.)
2. **A name of WHAT?** A person · a public figure · a company · a place · none of the above.
3. **WHICH one?** «Paris» is a city in France and a town in Ontario; «Anna» is a person and an Indian
   coin.
4. **Have I met this one before?** — a different question from 3, and the one that carries identity.

The marker bench only ever felt question 2, and only for `with`. The Captain is right that this is a
point of its own and not a footnote to the thirteen.

## WHAT tk1 ALREADY BUILT — TRANSCRIBED, BECAUSE IT LIVES ONLY IN CODE COMMENTS

*The rule that produced `CLAUDE.md`: an origin that cannot be read is not documentation. Everything
below is in `tokeniko-tk1/lib/llc/parser.py`, `lib/core/places.py` and `lib/llc/compiler/c_entities.py`
as comments beside the code, and nowhere in any roadmap. It is transcribed here so E3b argues with it
rather than re-deriving it.*

### 1. The places table — the asset he means, and it is large

> *«The places table (~4.7M docs, author-curated at first ingestion) is a hand-built spatial
> ontology: every place carries TWO complete containment chains — `path_admin` (political: europe →
> italy → lazio → rome) and `path_geo` (physical: universe → … → earth → eurasia) — plus a `type`
> column (city/country/planet/… — an is_a statement) and sparse `physical_features` cross-links (rome
> ON the italian peninsula).»* — `lib/core/places.py`

**MEASURED AGAINST THE LIVE v1 BODY, 2026-09-16, read-only** — because a comment is not a count:

    places                4,674,701 docs
      type                21 values EXACTLY, as the comment claims — archipelago · city · continent ·
                          country · desert · drainage_basin · galaxy · galaxy_cluster · hydrographic ·
                          island · landmass · mountain_range · ocean · peninsula · plain · planet ·
                          plateau · region · root · star_system · terrestrial
      category            2 values — `administrative` · `geographical`. A SECOND closed axis the
                          comment does not mention, and it is the one that says which chain is primary
      location            4,670,544 rows carry coordinates — 99.9%, so «has a point» is nearly total
      physical_features   2,566,998 rows — 54.9%, so «sparse» is accurate and a reader must expect None

    rome  ->  type=city · category=administrative
              path_admin  europe → italy → lazio → rome
              path_geo    universe → local group → milky way → solar system → earth → eurasia
              location    [12.51133, 41.89193]
              physical_features  italian peninsula · north european plain

Three things make it more than a gazetteer:

- **the `type` column is a CLOSED SET of about 21 values, and it is an `is_a` statement.** That is
  the same property that let the closed classes be a table and UD be a gate: both ends finite.
- **a place's type is mapped to a dictionary SENSE**, and that sense's vector is the place's semantic
  centroid — `country` → the country sense, unmapped compounds (`drainage_basin`, `star_system`) →
  `location.n.01`, *«honest, never noise»*.
- **it is read LAZILY and never materialized.** `places.py`'s own words: *«make the chains
  REASONING-LIVE without ever materializing the 4.7M-doc firehose into the relations collection (the
  cascade-noise lesson: read the curated table lazily)»*. That is the tk2 ruling about feeding
  CURATED fuel to the chainer, already applied once in tk1, at this exact table.

### 2. The NER gate, and both of the ways it failed

tk1 mints an individual from spaCy's entity label plus a type centroid:

    PERSON -> person.n.01        GPE / LOC / FAC -> location.n.01     ORG -> organization.n.01
    NORP   -> group.n.01         PRODUCT / WORK_OF_ART -> artifact.n.01   EVENT -> event.n.01

*«a proper noun NER-typed to a known type centroid becomes an entity-linked individual: it gets the
type centroid as its SEMANTIC vector (meaning = geometry — NEVER a random/noise vector into the
grounded space) + a context-scoped IDENTITY uid (identity = symbolic, kept separate).»*

**FAILURE ONE — the gate lets gibberish in.** The mint is guarded by `has_vector` *«so OOV gibberish
(which spaCy mislabels as GPE/…) never mints an individual»*. The label alone was not enough.

**FAILURE TWO — the gate keeps known names out.** *«the lowercase-known-name no-op («kotekino is my
creator» — stanza tags it PROPN but gives no NER type, so the minting gate rightly refuses; yet
kotekino is not unknown)»*. The repair was a second path — RECOGNITION against the names he already
holds — which *«can never create an identity, so OOV gibberish stays unlinkable»*.

**This is exactly the Captain's «casing is an indicator, although it's not grant», met twice from
opposite sides.** A capital is weak evidence FOR and its absence is no evidence AGAINST.

### 3. The names list — «partial, and we can reason over that», and the reasoning is forced

**`tokeniko.names` — 21,975 rows, ONE column: `name`.** A flat, lower-cased roster of personal-name
spellings, forenames and surnames together. It holds `anna`. It does not hold `kotekino`.

**It would fix the marker bench's two errors immediately, and that is the trap.** «I ate with Anna»
goes comitative the moment `anna` is known to be a personal name — and then measured against the two
other tables it turns out membership cannot be a TEST:

    of the 21,975 names, ALSO a place name          6,170   28.1%
                         ALSO a WordNet common noun 3,333   15.2%
                         both                       1,862

**`paris` is in the names list.** So is `abbey`, `ace`, `acacia`. A rule that read membership as
«this is a person» would make «go to Paris» a recipient and «cut with an ace» a companion. The list
is **evidence with a 28% collision rate against one table alone**, which is the definition of a
signal that must be weighed rather than tested — and therefore the sharpest possible statement of
why the Captain wants a net here rather than another rule.

*(One housekeeping find: the roster contains the string `TRUE`, which is a spreadsheet boolean that
survived an ingestion. The list needs a cleaning pass before it is trusted for anything.)*

### 4. The names he has MET, and how ambiguity is already refused

`tokeniko_mem.stakeholders` — **18 rows**, and every one of them is biography: participants (people
he talks WITH) and individuals (people he was told ABOUT), each with a `kind`, a `contextKey`, a `uid`, an `ner_type` and a stored vector. On a name
known under several identities the order is: *(1) the individual scoped to THIS talker's context,
(2) a participant — a real interlocutor with a global identity, (3) a unique individual from another
context; genuinely ambiguous → None (never guess an identity)*.

**That abstention is already the right instinct and it is already written down.** E3b inherits it.

### 5. The prominence problem, logged by tk1 and never solved

> *«NB: name lookup is not disambiguated by prominence, so homonyms resolve to whichever the places
> knowledge base returns first (e.g. "Paris" may be Paris, Ontario).»*

**This is the Captain's «public personality» in its geographical clothes**, and it is the case that
cannot be curated: which Paris a stranger means depends on who is speaking, what else is in the
sentence, and what the world currently talks about. It is the natural first home for the micro-nn.

## THE SPACY QUESTION DOES NOT REOPEN REQUIREMENT 2

Req 2 was amended on 2026-09-15 to say that spaCy's models are **not a second opinion** on a
dependency parse, because *«stanza tries to be as close to UD2 as possible while spaCy is more
creative»*. Nothing here disturbs that, and the difference must be stated so nobody reads it as a
reversal:

- **Dependencies** are read against a PUBLISHED STANDARD (UD2), so a second reader that does not aim
  at the standard is noise. One reader, and UD2 is the check.
- **Entity recognition is not a UD task at all.** There is no UD relation for «this is a company».
  It is a separate model output with its own label set (OntoNotes' 18 types), and stanza ships its
  own NER processor — so the honest first measurement is *stanza's NER against spaCy's on the same
  text*, which is a question E3b owes and E3 never asked.

**And an NER label is never a verdict here.** It is a CANDIDATE — tk1 proved that twice — which is
precisely the shape a micro-nn is allowed to rank (micro-nn req 7: ranks among already-legal options,
never mints one).

## THE MICRO-NN NOTE IS BIGGER THAN THIS POINT

The Captain's aside is a **governance rule for the whole ecosystem**, and it answers a question the
micro-nn chapter left open — *when is a micro-nn the right answer at all?* The chapter has six
declared sites and a fence, and no admission criterion. His is:

> **introduce one exactly where curation is not entirely possible, and where the decision can change
> over time.**

**Both clauses are load-bearing, and they are the same two tests that have already been run by hand
in this project.** A closed class *can* be curated completely, so it is a table (`db/0008`). UD's 37
relations *can* be enumerated, so the gate can be complete. «Which Paris did he mean» can be
curated for the hundred places we have seen and never for the next one — and the answer moves, because
what is prominent this year is not what was prominent last year. That is the first genuine case the
project has met.

It also explains the two tests' ORDER. Curation is tried first and the net is admitted only where
curation demonstrably cannot finish — which is why this note transcribes tk1's table before proposing
a net, and why the net's job is to rank the table's candidates rather than to replace it.

## THE BOUNDARY, BECAUSE THE CAPTAIN DREW IT YESTERDAY

> *«Everything that belongs to tk2 memory (inherited from tk1 memory) should belong to migration.»*

So the two tk1 tables go to different epics, and the difference is whether they are **biography**:

- **the places table is an ASSET, not biography.** Author-curated reference data, static, about the
  world and not about him. It belongs on the inheritance ledger beside the curated senses, and E3b
  may use it directly.
- **the stakeholders are BIOGRAPHY.** Who he has met and who he was told about is his life, and E9
  migrates it. E3b builds the MECHANISM that reads such a table and owes it a shape; it does not move
  a single row.

## WHAT E3b OWES

Stated as questions, because none of them is answered yet and the requirements method is one line
each once they are:

1. **Is it a name?** — stanza NER vs spaCy NER, measured on the same text; casing as evidence and not
   as a test; the two failure directions tk1 recorded as the bench's first cases.
2. **A name of what?** — **ANSWERED the same day, and by the reason I had not reached.** I argued for
   our own inventory on four engineering grounds; the Captain's was the first standing law: *«with our
   inventory as db (not code!), we can modify it keeping the logic: everything is KB. If we rely on a
   third party we lose this ability.»* So it is not merely OUR set instead of OntoNotes' — **it is a
   set in ROWS instead of a set in code**, which my own proposal had not gone as far as. See req 17.
3. **Which one?** — the places table as the curated half; prominence as the half that cannot be
   curated; the abstention as the default.
4. **Have I met it?** — recognition against a names table, with tk1's preference order and its
   «genuinely ambiguous → never guess».
5. **The first micro-nn instance** — a declaration (input schema · output kind · reward source)
   against the framework, ranking candidates the curation produced, under the shared fence.
6. **What a name IS in a zip** — a box whose `head` is a named individual: the type centroid is the
   SEMANTIC content and the uid is the IDENTITY, and the two never merge. `db/0012` gives the
   markers a third thing to read the day this lands, which is how «went with Anna» becomes comitative
   without a rule about Anna.
