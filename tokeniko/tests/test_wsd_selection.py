# ------------------------------------------------------------------------------------------------
# M3 — WSD SELECTION (the third harvest's sense misses, 2026-07-16).
#
# Fix A: `_wsd_mostFrequentVector` had NO order guarantee (bare find_one) — for "whale" it returned
# giant.n.04 the PERSON, so a repeated lemma pushed every centroid onto person-senses and even
# "fish" resolved to pisces.n.02 (the astrology sign). Fixed: most-frequent discipline in the
# context fetch + same-lemma tokens excluded from a token's centroid (self-evidence ≠ context).
#
# Fix B: the curated `preferred` flag — the WSD ladder is Lesk → preferred → centroid → WordNet
# order (textual evidence wins; curated human data outranks sparse-vector co-occurrence guessing;
# the centroid was confident-wrong in every documented episode: dog.n.03 0.83, giant.n.04 0.807,
# pisces.n.02 0.755). The flag rung is unit-tested with in-memory rows (KB writes are the
# operator's); the live-flag integration tests self-activate once curate_prefer_senses --apply ran.
# ------------------------------------------------------------------------------------------------
import pytest

from lib.core.kb_extract import _zip_leaves


def _all_senses(zp):
    out = set()
    for leaf in _zip_leaves(zp.items):
        out.update(leaf.senses.values())
    return out


# ---- fix A: the centroid self-poisoning regression -------------------------------------------------

def test_repeated_lemma_keeps_animal_senses(compile_zip):
    # the harvest specimen: two "whale" tokens poisoned each other's centroid -> giant.n.04 at
    # 0.807 and fish -> pisces.n.02. Both must resolve to the animals now.
    senses = _all_senses(compile_zip("a whale lives in the water but a whale is not a fish"))
    assert "whale.n.02" in senses
    assert "giant.n.04" not in senses
    assert "pisces.n.02" not in senses


def test_multisentence_animal_senses(compile_zip):
    # «yes. a fish breathes with gills. a whale breathes with lungs.» — the evening play's shape
    senses = _all_senses(compile_zip("a fish breathes with gills. a whale breathes with lungs."))
    assert "fish.n.01" in senses
    assert "whale.n.02" in senses
    assert "pisces.n.02" not in senses and "giant.n.04" not in senses


def test_keepset_copular_circularity_intact(compile_zip):
    # the 2026-07-11 guard must survive: subject not disambiguated by its copular partner
    assert "dog.n.01" in _all_senses(compile_zip("a dog is a reptile"))
    assert "cat.n.01" in _all_senses(compile_zip("a cat is a mammal"))
    # the partner's own modifiers still count as context (the financial bank)
    assert "depository_financial_institution.n.01" in _all_senses(
        compile_zip("the bank is a financial institution")
    )


# ---- fix B: the preferred rung (unit — in-memory rows, no KB writes) --------------------------------

def _tok(_io, text, lemma):
    import lib.llc.parser as P
    doc = P.nlp_stanza(text)
    return next(t for t in doc if t.lemma_.lower() == lemma)


def _row(word, sense, definition, preferred=False):
    from lib.core.models import TKDictionaryDoc
    return TKDictionaryDoc(word=word, pos="n", sense=sense, definition=definition,
                           preferred=preferred)


def test_preferred_wins_when_lesk_silent(_io, compile_zip):
    # no gloss overlap with the sentence -> the curated row wins over the WordNet order
    from lib.llc.parser import parser_disambiguateSense
    tok = _tok(_io, "a squid is a mammal", "squid")
    cands = [
        _row("squid", "squid.n.01", "squid prepared as food"),
        _row("squid", "squid.n.02", "fast-moving ten-armed cephalopod mollusk", preferred=True),
    ]
    assert parser_disambiguateSense(tok, cands).sense == "squid.n.02"


def test_lesk_beats_preferred(_io, compile_zip):
    # real textual evidence outranks the curated default: the gloss overlaps the sentence
    from lib.llc.parser import parser_disambiguateSense
    tok = _tok(_io, "the squid was served with lemon at dinner", "squid")
    cands = [
        _row("squid", "squid.n.01", "squid served as food at dinner"),
        _row("squid", "squid.n.02", "fast-moving ten-armed cephalopod mollusk", preferred=True),
    ]
    assert parser_disambiguateSense(tok, cands).sense == "squid.n.01"


def test_no_preferred_falls_through_to_prior(_io, compile_zip):
    # without a flag and without evidence, the own-lemma smallest-NN prior stands (unchanged)
    from lib.llc.parser import parser_disambiguateSense
    tok = _tok(_io, "a squid is a mammal", "squid")
    cands = [
        _row("squid", "squid.n.01", "squid prepared as food"),
        _row("squid", "squid.n.02", "fast-moving ten-armed cephalopod mollusk"),
    ]
    assert parser_disambiguateSense(tok, cands).sense == "squid.n.01"


# ---- fix B live (self-activating once the operator ran curate_prefer_senses --apply) ---------------

def _flag_live(word, pos, sense):
    from lib.core.models import TKDictionaryDoc
    d = TKDictionaryDoc.find_one({"word": word, "pos": pos, "preferred": True}).run()
    return d is not None and d.sense == sense


def test_live_preferred_squid(compile_zip, _io):
    if not _flag_live("squid", "n", "squid.n.02"):
        pytest.skip("curate_prefer_senses --apply not run yet (operator-gated)")
    assert "squid.n.02" in _all_senses(compile_zip("a squid is a fish or a mammal"))


def test_live_preferred_calculator(compile_zip, _io):
    if not _flag_live("calculator", "n", "calculator.n.02"):
        pytest.skip("curate_prefer_senses --apply not run yet (operator-gated)")
    assert "calculator.n.02" in _all_senses(compile_zip("a calculator is a software"))


def test_live_preferred_fish_residual(compile_zip, _io):
    # the pisces residual: a meta-sentence whose centroid ranked the fish SIGN above the fish
    if not _flag_live("fish", "n", "fish.n.01"):
        pytest.skip("curate_prefer_senses --apply not run yet (operator-gated)")
    senses = _all_senses(
        compile_zip("this imply that fish, mammals and other kind of animals can live in water")
    )
    assert "pisces.n.02" not in senses


def test_live_preferred_bit(compile_zip, _io):
    # batch 2 (the second-harvest strays): context-less "bits" read bit.n.02 the FRAGMENT; the
    # plain reading in tokeniko's world is the information unit — and bit.n.06 is_a
    # unit_of_measurement.n.01 is already in the graph, so the definition grounds
    if not _flag_live("bit", "n", "bit.n.06"):
        pytest.skip("curate_prefer_senses --apply not run yet (operator-gated)")
    assert "bit.n.06" in _all_senses(compile_zip("a coin stores bits"))


# ---- BATCH 3 + THE LESK BAR (§2 microscope pass, 2026-08-10) ---------------------------------------
# The pass found 43 `wrong-sense` leads in the 2026-07-17→08-09 corpus — all POST-M3, and confirmed
# live by replay («you are right!» still picked the direction of the sun). 21 lemmas were curated;
# the two that did NOT flip exposed a second mechanism, locked below.

@pytest.mark.parametrize("word,pos,sense,sentence", [
    ("right",    "a", "correct.a.01",    "you are right!"),                       # 6 leads
    ("property", "n", "property.n.02",   "every thing that exists have more than one property"),
    ("gold",     "n", "gold.n.03",       "gold is shiny"),
    ("think",    "v", "think.v.03",      "a software sometimes thinks"),
    ("wrong",    "a", "incorrect.a.01",  "a person is wrong when he says false"),
    ("value",    "n", "value.n.02",      "a coin has value"),
    ("wake",     "v", "wake_up.v.02",    "you were asleep but now you woke up"),
    ("opposite", "s", "opposite.s.03",   "some properties are opposite"),
    ("base",     "v", "establish.v.08",  "trust is certainty based on past experience"),
    ("trust",    "n", "reliance.n.01",   "tokeniko, do you know what trust is?"),
])
def test_live_preferred_batch3(compile_zip, _io, word, pos, sense, sentence):
    if not _flag_live(word, pos, sense):
        pytest.skip("curate_prefer_senses --apply not run yet (operator-gated)")
    assert sense in _all_senses(compile_zip(sentence))


# ---- GLOSS-FREQUENCY WEIGHTING (§2 microscope pass, 2026-08-10) ------------------------------------
# Lesk counted a bare set intersection, so every shared word weighed the same — and the two sides were
# filtered ASYMMETRICALLY (the context drops stopwords, the gloss did not). One match on `usually` beat
# a curated human ruling. The FIRST attempted cure was a minimum overlap COUNT, and
# `test_lesk_beats_preferred` above refuted it: «served with lemon at DINNER» is ALSO a one-word
# overlap, and that one is real evidence. The discriminator is informativeness, not count.

def test_gloss_frequency_set_drops_noise_and_keeps_evidence(_io):
    """The CALIBRATION, locked. Frequency does not separate noise from evidence cleanly — `person`
    (2.40%) is more common than `usually` (1.95%) and carries meaning — so 1.0% is a measured
    compromise, and these are the words it must land on either side of. Margins are tight on purpose:
    `water` sits 0.14 points under the bar and M3's pisces residual rests on it, so anyone moving this
    constant should see exactly what they are risking."""
    from lib.llc.parser import _gloss_common_words
    common = _gloss_common_words()
    for noise in ("usually", "especially"):          # 1.95%, 2.62% — decided senses on nothing
        assert noise in common, f"{noise} must not count as evidence"
    for evidence in ("water", "food", "mammal", "dinner", "clothing", "polite"):
        assert evidence not in common, f"{evidence} is evidence and must survive the bar"


def test_live_person_survives_the_usually_overlap(compile_zip, _io):
    # THE SPECIMEN: «a human body (USUALLY including the clothing)» outscored the curated «a human
    # being» on the single word `usually`, and Lesk returns before the curated rung is consulted.
    if not _flag_live("person", "n", "person.n.01"):
        pytest.skip("curate_prefer_senses --apply not run yet (operator-gated)")
    senses = _all_senses(compile_zip("because polite people usually say hello when they meet someone"))
    assert "person.n.01" in senses and "person.n.02" not in senses


@pytest.mark.xfail(reason="Lesk false friend, not a frequency problem: `correct` is as rare as "
                          "`mammal` (0.07% vs 0.08%) so it survives any frequency bar, but "
                          "decent.s.01's «socially or conventionally correct» is a different SENSE "
                          "of the word than the speaker's. Sense-blindness is intrinsic to Lesk; "
                          "only a sense-aware method would catch it. Input is also degenerate — two "
                          "interjections, no proposition. Filed, deliberately not chased.",
                   strict=False)
def test_live_nice_is_not_socially_correct(compile_zip, _io):
    senses = _all_senses(compile_zip("nice! correct!"))
    assert "nice.a.01" in senses and "decent.s.01" not in senses
