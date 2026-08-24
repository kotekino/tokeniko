# ------------------------------------------------------------------------------------------------
# THE TRANSLATOR AT THE EARS — rag1-in + rag2-in (instrument arc #3, v1; 2026-07-16).
#
# The author's rulings, mechanized and asserted: D1b escalation-only (a sound parse is NEVER
# touched), D4 the proposer is a cloud small model but THE ZIP-VERIFIER disposes (every soundly-
# parsed leaf must survive the polish, flags intact), D2 an unverifiable polish falls through to
# the raw parse (unknown leaves never become beliefs; eval:unknown already asks). No live API in
# the gate — the normalizer call is stubbed; the detector/verifier run on REAL compiled zips.
# ------------------------------------------------------------------------------------------------
import pytest

from lib.llc.normalizer import detector_stumbles, verifier_preserves, _leaf_sound
from lib.core.kb_extract import _zip_leaves


# ---- the stumble detector (D1b: escalation-only) ---------------------------------------------------

def test_sound_sentence_never_escalates(compile_zip):
    assert detector_stumbles(compile_zip("a cat is a mammal")) is False
    assert detector_stumbles(compile_zip("all humans are mortal")) is False


def test_unknown_vocabulary_escalates(compile_zip):
    # OOV gibberish -> unknown leaf -> stumble
    assert detector_stumbles(compile_zip("a wug is a blicket")) is True


def test_tangle_wart_escalates(compile_zip):
    # the bold-test tangle signature: self-loop leaves («software is software») / bare-copula
    # predicates — the six-leaf monster's shape (census 2026-07-15)
    zp = compile_zip(
        "it is true. there are softwares that can think and software that can't think. "
        "probably all softwares can calculate"
    )
    assert detector_stumbles(zp) is True


# ---- the zip-verifier (rag2-in: the compiler disposes) ----------------------------------------------

def test_verifier_accepts_true_repair(compile_zip):
    # a typo'd original stumbles; the honest polish compiles sound and preserves what little was
    # sound before (nothing) -> accepted
    original = compile_zip("a catt is a mamal")
    polished = compile_zip("a cat is a mammal")
    ok, note = verifier_preserves(original, polished)
    assert ok, note


def test_verifier_rejects_dropped_leaf(compile_zip):
    # the original parses SOUND leaves; a "polish" that loses one is a meaning change -> rejected
    original = compile_zip("a cat is a mammal and a dog is an animal")
    polished = compile_zip("a cat is a mammal")
    ok, note = verifier_preserves(original, polished)
    assert not ok and "dropped" in note


def test_verifier_rejects_flipped_negation(compile_zip):
    # negation rides the conclusion key — a flipped negation is an altered leaf -> rejected
    original = compile_zip("a software does not reach truth")
    polished = compile_zip("a software reaches truth")
    ok, note = verifier_preserves(original, polished)
    assert not ok


def test_verifier_rejects_unrepaired_polish(compile_zip):
    # a polish that still stumbles repaired nothing -> rejected (the stumble must not just move)
    original = compile_zip("a wug is a blicket")
    polished = compile_zip("a wug is a blicket")
    ok, note = verifier_preserves(original, polished)
    assert not ok and "stumbles" in note


def test_verifier_rejects_invention(compile_zip):
    # ballooning: the polish may split a tangle, not free-associate
    original = compile_zip("a cat is a mammal")
    polished = compile_zip(
        "a cat is a mammal and a dog is an animal and a bird has feathers and a fish swims"
    )
    ok, note = verifier_preserves(original, polished)
    assert not ok and "balloons" in note


def test_verifier_accepts_flag_preserving_segmentation(compile_zip):
    # legitimate tangle-unwinding: the sound leaves survive with flags intact
    original = compile_zip("a cat is a mammal and a dog is an animal")
    polished = compile_zip("a cat is a mammal. a dog is an animal.")
    ok, note = verifier_preserves(original, polished)
    assert ok, note


# ---- the wired path (/input semantics via the service seam, normalizer stubbed) --------------------

def test_input_fallthrough_when_normalizer_off(_io, monkeypatch):
    # RAG1_DISABLED -> the raw parse stands exactly as before (no escalation attempted)
    import lib.llc.normalizer as norm
    monkeypatch.setenv("RAG1_DISABLED", "1")
    assert norm.normalizer_enabled() is False


def test_leaf_sound_signatures(compile_zip):
    # the detector's leaf-level signatures, pinned: sound / unknown / self-loop
    sound = _zip_leaves(compile_zip("a cat is a mammal").items)[0]
    assert _leaf_sound(sound) is True
    unknown = _zip_leaves(compile_zip("a wug is a blicket").items)[0]
    assert _leaf_sound(unknown) is False


# ---- the UNREPAIRABLE classifier (2026-07-17, basket item 4: pronoun-subject leaves) ----------------
# a pronoun-subject leaf is a COREFERENCE gap, not a surface one — the polish recompiles to the
# same leaf and the verifier rejects it every time. detector_unrepairable skips the escalation
# (saves the Haiku call); mixed stumbles (a typo beside the pronoun) still escalate.

@pytest.fixture(scope="session")
def compile_both(_io):
    import copy
    tok, ai = _io
    from lib.llc.parser import parser
    from lib.llc.compiler import compiler_compile

    def _c(sentence):
        rec = parser(sentence, tok, tok, ai)
        return compiler_compile(copy.deepcopy(rec))  # (TKLLC, TKZip)

    return _c


def test_pronoun_subject_leaf_is_unrepairable(compile_both):
    from lib.llc.normalizer import detector_unrepairable
    for s in ("a whale is a mammal and it feeds milk", "he sleeps", "it is important"):
        llc, zp = compile_both(s)
        assert detector_stumbles(zp) is True                    # it IS a stumble…
        assert detector_unrepairable(llc, zp) is True, s        # …but not a repairable one


def test_typo_stumble_still_escalates(compile_both):
    # a surface stumble (typos) must keep its Haiku chance — subject token is not a pronoun
    from lib.llc.normalizer import detector_unrepairable
    llc, zp = compile_both("the wrld is bg")
    assert detector_stumbles(zp) is True
    assert detector_unrepairable(llc, zp) is False


def test_sound_sentence_is_not_unrepairable(compile_both):
    # no unsound leaves at all -> False (the unrepairable gate only ever narrows escalation)
    from lib.llc.normalizer import detector_unrepairable
    llc, zp = compile_both("a cat is a mammal")
    assert detector_unrepairable(llc, zp) is False


def test_resolved_first_person_never_trips_the_gate(compile_both):
    # «I value logic» resolves through the identity bridge — sound, no stumble, no gate
    from lib.llc.normalizer import detector_unrepairable
    llc, zp = compile_both("I value logic")
    assert detector_stumbles(zp) is False
    assert detector_unrepairable(llc, zp) is False


# ---- the ears' hallucination chain — the strong verifier (2026-07-24) --------------------------------
# The live specimen (02:12Z): kotekino asked «tokeniko, what are you?»; Haiku ANSWERED as itself
# («I am a transcription normalizer…») and the prompt-soup sailed the structural gate (the wh
# original's only leaf was skippable — nothing constrained the polish). Three cuts: wh-aware
# soundness (a well-formed wh-question no longer stumbles → no escalation), the MOOD gate (a question
# that comes back a statement is trashed), and the SEMANTIC FLOOR (a polish that drifts in the 2925
# space is trashed regardless of structure). The specimen is the regression's ground truth.

_SPECIMEN_ORIGINAL = "tokeniko, what are you?"
_SPECIMEN_POLISH = ("I am a transcription normalizer for a reasoning engine. "
                    "I tidy the surface of messages without changing their meaning.")


def test_wh_question_does_not_escalate(compile_zip):
    # cut 2: a well-formed wh-question's gap IS the question, not a stumble — no burned Haiku call,
    # no exposure to the role-confusion hallucination
    assert detector_stumbles(compile_zip("what are you?")) is False
    assert detector_stumbles(compile_zip("what is a cat?")) is False


def test_wh_residual_families_do_not_escalate(compile_zip):
    # 2026-07-25: the subject-gap and copula-predicate families — the officer-reported residuals of
    # the ears build. Each empties a DIFFERENT gap role; one soundness rule (any known non-gap role)
    # covers all three, so neither escalates any longer.
    assert detector_stumbles(compile_zip("who is happy?")) is False       # subject IS the gap
    assert detector_stumbles(compile_zip("where is Rome?")) is False      # copula shape, location gap
    # and the leaf-level signatures behind them: sound despite the emptied role / the bare copula
    subj_gap = _zip_leaves(compile_zip("who is happy?").items)[0]
    assert _leaf_sound(subj_gap) is True                                  # no subject, but a predicate
    loc_gap = _zip_leaves(compile_zip("where is Rome?").items)[0]
    assert _leaf_sound(loc_gap) is True                                   # be.v.01 wart relaxed for wh
    # the carve-out holds: a NON-wh bare copula is still a wart (an assertion parse fault escalates)
    non_wh_copula = _zip_leaves(compile_zip("a wug is a blicket").items)[0]
    assert _leaf_sound(non_wh_copula) is False                            # unknown vocab, still unsound


def test_live_specimen_rejected(compile_zip):
    # the mother-of-all: the prompt-soup answer must be trashed at the source (mood and/or semantic)
    ok, note = verifier_preserves(compile_zip(_SPECIMEN_ORIGINAL), compile_zip(_SPECIMEN_POLISH))
    assert not ok, note


def test_mood_flip_rejected(compile_zip):
    # cut 1: an interrogative original that comes back a bare statement changed meaning wholesale
    ok, note = verifier_preserves(compile_zip("what is a cat?"), compile_zip("a cat is a mammal"))
    assert not ok and "mood" in note


def test_genuine_tidy_survives_the_floor(compile_zip):
    # the floor must NOT strangle the instrument: a real segmentation (semantic proximity ~1.0)
    # still ACCEPTS — see test_semantic_floor_measured_margins for the numbers
    ok, note = verifier_preserves(
        compile_zip("a cat is a mammal and a dog is an animal"),
        compile_zip("a cat is a mammal. a dog is an animal."))
    assert ok, note


def test_semantic_floor_measured_margins(compile_zip):
    # pin the calibration the floor rests on (RAG1_SEMANTIC_FLOOR default 0.6). measured 2026-07-24:
    #   genuine segmentation ~1.00  |  wholesale drift ~0.03  |  wh/no-anchor -> abstain (None)
    from lib.llc.normalizer import _semantic_proximity, _semantic_floor
    def prox(a, b):
        return _semantic_proximity(_zip_leaves(compile_zip(a).items), _zip_leaves(compile_zip(b).items))
    floor = _semantic_floor()
    # a genuine tidy sits far ABOVE the floor
    assert prox("a cat is a mammal. a dog is an animal.",
                "a cat is a mammal and a dog is an animal") > floor
    # wholesale semantic drift sits far BELOW it (both sides have a sound anchor)
    drift = prox("a cat is a mammal", "a rock is a mineral")
    assert drift is not None and drift < floor
    # the no-anchor case (the wh original carries no sound semantic anchor) ABSTAINS — the mood +
    # structural gates carry that verdict, not the geometry
    assert prox(_SPECIMEN_ORIGINAL, _SPECIMEN_POLISH) is None


# ---- the wall's catches are visible leads (the addendum, 2026-07-24) --------------------------------
# Every verifier REJECTION writes ONE microscope row (TKZipDebugDoc) into the standing triage corpus:
# RED (high) when the polish CHANGED MEANING (mood/semantic), medium for a structural miss. A
# deterministic finding (confidence 1.0, no cloud judge). The write is best-effort — it must never
# block the ears from hearing.

def test_ears_rejection_logs_high_severity_lead(compile_zip, _io):
    # the live specimen: a meaning-changing rejection -> a RED lead in the corpus
    from api.main import _log_ears_rejection
    from lib.core.models import TKZipDebugDoc
    orig, pol = compile_zip(_SPECIMEN_ORIGINAL), compile_zip(_SPECIMEN_POLISH)
    ok, note = verifier_preserves(orig, pol)
    assert not ok
    item_id = "ears-test-high-0001"
    try:
        _log_ears_rejection(item_id, _SPECIMEN_ORIGINAL, note, _SPECIMEN_POLISH, orig, pol)
        row = TKZipDebugDoc.find_one({"item_id": item_id}).run()
        assert row is not None
        assert row.verdict == "mismatch" and row.category == "ears-hallucination"
        assert row.severity == "high"          # a mood/semantic rejection = meaning changed
        assert row.confidence == 1.0 and row.addressed is False
        assert "transcription normalizer" in row.note   # the polished text rides in the note
    finally:
        TKZipDebugDoc.find({"item_id": item_id}).delete().run()


def test_ears_rejection_logs_medium_severity_lead(compile_zip, _io):
    # a structural miss (a dropped sound leaf) is a bad polish, not necessarily a hallucination -> medium
    from api.main import _log_ears_rejection
    from lib.core.models import TKZipDebugDoc
    orig = compile_zip("a cat is a mammal and a dog is an animal")
    pol = compile_zip("a cat is a mammal")
    ok, note = verifier_preserves(orig, pol)
    assert not ok and "dropped" in note
    item_id = "ears-test-medium-0001"
    try:
        _log_ears_rejection(item_id, "a cat is a mammal and a dog is an animal", note,
                            "a cat is a mammal", orig, pol)
        row = TKZipDebugDoc.find_one({"item_id": item_id}).run()
        assert row is not None and row.severity == "medium"
        assert row.category == "ears-hallucination"
    finally:
        TKZipDebugDoc.find({"item_id": item_id}).delete().run()


def test_ears_rejection_write_failure_never_blocks(_io):
    # the ears keep hearing even if the notebook is full: a broken zip makes the write throw INSIDE
    # the helper, which must SWALLOW it (never propagate to /input)
    from api.main import _log_ears_rejection
    _log_ears_rejection("ears-test-bad", "x", "polish drifts semantically (0.10 < floor 0.60)",
                        "y", None, None)  # must not raise


# ---- the two-tier floor at the ears: ACCEPT | ASK | DISCARD (the room + ask, 1a) --------------------
# asking ≠ believing — the strong wall still trashes a drifting polish (DISCARD), but a polish that is
# a COHERENT, semantically-plausible ALTERNATIVE reading is neither believed nor discarded: it is
# OFFERED as a question (ASK). verifier_verdict is built ON TOP of verifier_preserves (the accept wall
# is unchanged), so every test above stays valid — this only exercises the added middle tier.

def test_verdict_accept_is_the_old_accept(compile_zip):
    # a genuine segmentation still passes the accept wall -> ACCEPT (behaves exactly as verifier_preserves)
    from lib.llc.normalizer import verifier_verdict
    verdict, _ = verifier_verdict(
        compile_zip("a cat is a mammal and a dog is an animal"),
        compile_zip("a cat is a mammal. a dog is an animal."))
    assert verdict == "ACCEPT"


def test_verdict_ask_offerable_reading(compile_zip):
    # a coherent alternative reading (a locative re-hearing, one swapped content word) sits in the
    # ask band [ASK_FLOOR, SEM_FLOOR) -> ASK (offer it, don't believe it)
    from lib.llc.normalizer import verifier_verdict
    verdict, note = verifier_verdict(compile_zip("the cat is on the mat"),
                                     compile_zip("the cat is on the bed"))
    assert verdict == "ASK", note


def test_verdict_discard_far_drift(compile_zip):
    # a wholesale drift (below the ask floor, both sides sound) is trashed at the source -> DISCARD
    from lib.llc.normalizer import verifier_verdict
    verdict, note = verifier_verdict(compile_zip("a cat is a mammal"),
                                     compile_zip("a rock is a mineral"))
    assert verdict == "DISCARD", note


def test_verdict_discard_prompt_soup(compile_zip):
    # the live specimen (a mood flip, no shared semantic anchor) must land DISCARD, never ASK — a
    # hallucination is trashed, not offered
    from lib.llc.normalizer import verifier_verdict
    verdict, note = verifier_verdict(compile_zip(_SPECIMEN_ORIGINAL), compile_zip(_SPECIMEN_POLISH))
    assert verdict == "DISCARD", note


def test_ask_floor_measured_margins(compile_zip):
    # pin the calibration RAG1_ASK_FLOOR rests on (default 0.12, the second/lower floor under the
    # accept floor 0.60). measured 2026-07-25 on whole-zip semantic centroids:
    #   far drift        «cat is a mammal»     vs «rock is a mineral»   ~0.03  (DISCARD, below the floor)
    #   taxon re-hearing «gold is a metal»     vs «gold is a mineral»   ~0.20  (ASK, inside the band)
    #   locative re-hear «cat is on the mat»   vs «cat is on the bed»   ~0.35  (ASK, inside the band)
    from lib.llc.normalizer import _semantic_proximity, _ask_floor, _semantic_floor
    from lib.core.kb_extract import _zip_leaves

    def prox(a, b):
        return _semantic_proximity(_zip_leaves(compile_zip(a).items), _zip_leaves(compile_zip(b).items))

    ask_floor, sem_floor = _ask_floor(), _semantic_floor()
    assert ask_floor < sem_floor  # the ask floor is the SECOND, lower floor
    # the far drift sits BELOW the ask floor (with margin) -> DISCARD
    drift = prox("a cat is a mammal", "a rock is a mineral")
    assert drift is not None and drift < ask_floor
    # the offerable re-hearings sit INSIDE the band [ask_floor, sem_floor) -> ASK
    for a, b in [("gold is a metal", "gold is a mineral"),
                 ("the cat is on the mat", "the cat is on the bed")]:
        p = prox(a, b)
        assert p is not None and ask_floor <= p < sem_floor, (a, b, p)


def test_input_stores_suggested_reading_only_on_ask(_io):
    # the /input contract (1a): the ASK candidate rides on the item as suggested_reading (stored
    # exactly once, here — the room only references its id); ACCEPT/DISCARD leave it None. Proven at
    # the field level: the model round-trips the reading, and the verdict tiers above decide when
    # /input sets it. The raw parse ALWAYS stands (original/zip unchanged — asking ≠ believing).
    from lib.core.models import TKMemoryItemDoc
    item = TKMemoryItemDoc(original="the cat is on the mat", zip=None,
                           sourceId="dym-store-test",
                           suggested_reading="the cat is on the bed")
    item.insert()
    try:
        fetched = TKMemoryItemDoc.get(item.id).run()
        assert fetched is not None
        assert fetched.suggested_reading == "the cat is on the bed"
        assert fetched.original == "the cat is on the mat"  # true history — the raw words stand
    finally:
        TKMemoryItemDoc.get_motor_collection().delete_many({"sourceId": "dym-store-test"})
