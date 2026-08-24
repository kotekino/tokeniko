# ------------------------------------------------------------------------------------------------
# The dictionary curation batch (2026-07-14 portrait, cluster C) — WSD selection fixes + coverage.
#   A: Lesk excludes the QUERY TOKEN from the sentence side («gold is shiny» — glazed.a.03 won on
#      its gloss merely MENTIONING "shiny"; self-reference is not context fit).
#   B: a copular participle predicate («I am well RESTED») tries the surface form's ADJECTIVE
#      senses first (stanza lemmatizes to the dynamic verb, so rested.a.01 was never a candidate).
#      NARROWED to the VBN tag on 2026-08-11 — see the §2 section below for both directions.
#   C: bit.n.06 (the information unit) curated into the dictionary (the ingestion's max_per_pos=3
#      cap cut it — the coin incident). Exact-sense asserts here are INTENTIONAL: the curated
#      selection is the regression target (unlike the band-assert default for drifting WSD).
# ------------------------------------------------------------------------------------------------
import pytest

from lib.core.tkzip import TKZipContent


def _senses(zp):
    out = {}
    def walk(item):
        c = item.content
        if isinstance(c, TKZipContent):
            out.update(c.senses)
        elif isinstance(c, list):
            for ch in c:
                walk(ch)
    walk(zp.items)
    return out


def test_shiny_is_not_glazed(compile_zip):
    # the self-mention exclusion: glazed.a.03 ("having a shiny surface") must not win on the word
    # "shiny" alone; the prior then picks the sense that IS shiny (glistening.s.01, lemma shiny).
    senses = _senses(compile_zip("gold is shiny"))
    assert senses.get("predicate") != "glazed.a.03"
    assert ".v." not in (senses.get("predicate") or "")


def test_rested_is_stative(compile_zip):
    # the copular participle routes to the adjective ("not tired; refreshed"), never rest.v.*
    senses = _senses(compile_zip("This morning I am well rested"))
    pred = senses.get("predicate") or ""
    assert ".v." not in pred
    assert pred.startswith("rested.")


# ---- the stative-participle gate, NARROWED TO VBN (§2 microscope, 2026-08-11) -----------------------
# The gate above was written for «I am well RESTED» but keyed on `VerbForm=Part`, which every PRESENT
# participle also carries — so the whole progressive family walked into it and came out adjectival:
# «the cat is sleeping» → dormant.s.02 «lying with head on paws as if sleeping». It now keys on the
# VBN tag. Both directions are locked below, and the price is xfailed at the bottom rather than hidden:
# a named cost belongs where the next person will read it.

@pytest.mark.parametrize("sentence,lemma", [
    ("the door is closed", "closed."),
    ("the cup is broken", "broken."),
])
def test_past_participle_state_stays_adjectival(compile_zip, sentence, lemma):
    # the gate's REASON TO EXIST: a VBN state must still reach the surface form's adjective sense
    # (stanza lemmatizes to the dynamic verb, so close.v.*/break.v.* is all the pool would offer).
    pred = _senses(compile_zip(sentence)).get("predicate") or ""
    assert ".v." not in pred, f"{sentence!r} lost its stative reading: {pred}"
    assert pred.startswith(lemma)


@pytest.mark.parametrize("sentence,forbidden", [
    ("the cat is sleeping", "dormant.s.02"),        # «lying with head on paws as if sleeping»
    ("the dog is swimming", "liquid.s.01"),         # «filled or brimming with tears»
    ("it is raining", "raining.s.01"),              # «falling in drops or as if falling like rain»
    ("the machine is not thinking", "intelligent.s.03"),   # «endowed with the capacity to reason»
])
def test_progressive_is_a_verb_not_an_adjective(compile_zip, sentence, forbidden):
    # a PRESENT participle under a copula is an ongoing action: it belongs to the verb pool. The
    # forbidden sense is the exact one the too-wide gate used to hand back (measured, not guessed).
    pred = _senses(compile_zip(sentence)).get("predicate") or ""
    assert pred != forbidden, f"{sentence!r} still resolves the over-fire sense {forbidden}"
    assert ".v." in pred, f"{sentence!r} predicate is not a verb sense: {pred}"


@pytest.mark.xfail(reason="THE PRICE OF THE VBN NARROWING, paid knowingly (author's ruling, "
                          "2026-08-11). A handful of VBG participles ARE predicative adjectives and "
                          "the tagger calls them VERB, so they lose the adjective route with the "
                          "progressives: «the water is running» takes run.v.01 («move fast by using "
                          "one's feet») and «the rule is binding» bind.v.02 («create social or "
                          "emotional ties»). The trade was measured at 13 everyday progressives "
                          "fixed against these 3 idioms lost (+3 borderline: deafening, blinding, "
                          "lasting) — and no syntactic signal separates the two VBG readings, so "
                          "the only honest fix is semantic, not another tag test. NB the second "
                          "case needs its full stop: stanza tags `binding` JJ in «the rule is "
                          "binding» and VBG in «the rule is binding.», so without the period the "
                          "cost never materializes (bound.a.01) — the tag itself is punctuation-"
                          "sensitive, which is one more reason no tag test can be the real fix.",
                   strict=False)
@pytest.mark.parametrize("sentence", ["the water is running", "the rule is binding."])
def test_predicative_vbg_idiom_keeps_its_adjective(compile_zip, sentence):
    pred = _senses(compile_zip(sentence)).get("predicate") or ""
    assert ".v." not in pred


def test_bit_is_the_information_unit(compile_zip):
    # the curated coverage row: bit resolves to the information unit next to "information"
    senses = _senses(compile_zip("a bit is a unit of information"))
    assert senses.get("subject") == "bit.n.06"


def test_lesk_context_overlap_still_wins(compile_zip):
    # the original Lesk design case must survive the exclusion: disambiguating "cat" next to
    # "mammal" still finds the animal (the overlap word is CONTEXT, not the query word).
    senses = _senses(compile_zip("a cat is a mammal"))
    assert senses.get("subject") == "cat.n.01"
