# parser/compiler — THE SUBJECT'S ROLE, AND THE DRILL CORRECTED, 2026-09-18 14:00

*Ten of the drill gate's twelve disagreements were one question: `nsubj` is a POSITION, and its role
depends on what is predicated of it. «The cat CHASED» is an agent, «I LOVE» an experiencer, «God
EXISTS» a patient. The station wrote `agent` for every subject and its own comment deferred the
question. Req 22.*

**Drill gate: 49 agreed · 13 DISAGREED → 59 agreed · 3 DISAGREED. Roles 102/128 → 115/141.**

---

## THE PRINCIPLE WAS ALREADY WRITTEN — E2, RULING 2

> *«I kicked the dog (I act) vs I fear the dog (it happens to me)… Verbs of feeling and thinking are
> the ones tokeniko will use about himself most.»* — `tkzip/202609111051_notes.md`

And ruling 1 merges VerbNet's Theme into `patient`. Nothing new was needed from the format; the
station only had to apply what the format already said.

## THE BENCH — EVERY SUBJECT THE DRILL HOLDS, NOT ONLY THE TEN

49 subjects paired with a hand-compiled row. The 38 that agreed are the controls.

**Copular adjectives separate perfectly** — through their related NOUN, because WordNet files almost
every adjective under one class (`adj.all`):

    noun.state      happy · hungry ×2 · tired              -> experiencer   4/4
    noun.attribute  dead · late ×2 · wrong · cute · green  -> patient       6/6
    a copular NOUN  mind · asia · friend                   -> patient       3/3

**Verbs do not separate by any published instrument.** The verb's supersense contradicted itself in
the drill three times (`think` agent against `learn`/`trust`/`understand` experiencer; `disagree`
experiencer against `tell` agent; `exist` patient against `live` agent). VerbNet's subject role did
worse: it files motion verbs as `Theme`, so *walk*, *go*, *stay*, *finish* would all have become
patients against E2's agents.

## THE CONTRADICTIONS WERE ASKED — AND THE QM ANSWERED THEM

The Captain's question back: *«We did it together, actually you did it and I acknowledged. So I ask
you the same question.»* The QM judged each against ruling 2, and he acknowledged:

- **`exist` → patient STANDS.** `exist-3`'s note: one zip shape with «there is». Existing is not acting.
- **`disagree` → experiencer STANDS.** `aw-16` is a position held. WordNet files the primary sense
  `verb.communication`; the resource is coarse here, and this is the table's one exception row.
- **`think` → agent WAS AN ERROR.** Ruling 2 names thinking; the case's note argues the IMPLY, never
  the role. **`live` → agent WAS AN ERROR.** A state, not an act — VerbNet files it with `exist`.
  `stay` keeps agent: it is controllable («what I did was stay home»).

A full scan — the gate never compares a VARIABLE — found the rest of the family: four more `think`
rows, and the drill contradicting itself on `learn` and on perception («to SEE the sea» against
«PERCEPTION» as agent). **Twelve rows in nine sentences amended**, dated in the bar doc. The Captain
ruled perception a CLASS and `develop` a named miss.

## THE RULE — ROWS, IN THE MARKERS' OWN VOCABULARY

`language_subject_roles` (`db/0018`), run by `MarkerSelector`, which gained two probes: the head's
`lemma` (for exceptions) and the supersense of the noun an adjective is `derived` with.

    verb      disagree                                            -> experiencer   (the exception)
              verb.emotion · verb.cognition · verb.perception     -> experiencer
              verb.stative                                        -> patient
              otherwise                                           -> agent
    copular   a noun complement                                   -> patient
              an adjective whose noun is noun.state               -> experiencer
              otherwise                                           -> patient

**The relation outranks the rule (req 12).** A clause with a direct object has its patient already,
so its subject cannot also be one. «Sam spent forty dollars» read `spend` by its primary sense («pass
time», stative) and pushed the dollars out; the UD gate caught it, and the rule now yields.

**`noun.feeling` is NOT in, and was for one draft.** Ruling 2's words suggested it; it has no drill
witness, and it made «Be QUIET!» an experiencer. *A class enters on a witness, not on a principle.*

The three places that read a subject's role read this one rule: `_role_of`, the imperative's
understood subject (task 2d), and the attitude's holder — which had taken the `agent` box and would
have gone empty the moment «Anna THINKS that…» made Anna an experiencer.

## WHAT IT CANNOT DO, NAMED

- **Sense-dependent verbs** — `develop` («develops cancer» / «develops software»), `lie` («be
  located» is its primary sense, so «he LIED» reads a patient). The role follows the sense, and the
  station never picks one (req 11). Binding is the evaluator's.
- **Stimulus-subject psych verbs** — «the dog FRIGHTENS me» is `verb.emotion`, and the dog is no
  experiencer. Exception rows when a witness arrives.
- **Agentive perception** — «look», «watch», «listen». Likewise.
- **The provenance debt deepens** — the supersense is still read live from WordNet (req 15's debt).

## AND ONE MORE PROVIDER DEFECT, ABSTAINED — `q-2`

Stanza labels the only object of «I trust **you**» as `iobj`, which UD reserves for the
double-object clause («she gave ME a raise»). The station now **abstains on a lone `iobj`** rather
than reading a recipient the sentence does not have: a role left open is half-understood, a
recipient invented is wrongly understood (req 8), and compensating for a provider is what `q-5`
ruled against. *The first attempt was too strict and the gate said so within a minute: «I asked ANNA
"Where do you live?"» IS a double-object clause whose second object is the quotation, and abstaining
there broke the rotation in `q-7` and `q-9`. A clause counts as the other object.*

## WHAT REMAINS IN THE RATCHET — THREE

    aw-15   no DomainRow yet                                        E3 unfinished
    aw-19   «I ate with Anna» — the named-individual hole           E3b
    t-ws-7  «an animal or A MIND» read as one noun phrase            provider defect, abstained
