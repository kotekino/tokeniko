"""THE MENTION-VOCATIVE BUG — a statement addressed to tokeniko had its SUBJECT stolen.

Found live 2026-08-03. `@tokeniko` decodes to a bare «tokeniko » with no punctuation, so
«@tokeniko the cat is a mammal» reached the parser as «tokeniko the cat is a mammal» — one noun
phrase headed by *tokeniko*. The comma is the ONLY difference between the two readings:

    'tokeniko , the cat is a mammal'   -> ([the] cat be [a] mammal)   cat.n.01 + mammal.n.01
    'tokeniko the cat is a mammal'     -> (tokeniko be [a] mammal)    subject stolen, cat LOST
    'tokeniko il gatto è un mammifero' -> (tokeniko be [a] mammal)    same — the translation was
                                                                     PERFECT (multilingual cleared)
    'a feline is a mammal'             -> ([a] feline be [a] mammal)  no vocative, no bug

So for as long as it stood, every statement addressed to him by mention — the most natural way
anyone addresses him — was compiled as a claim ABOUT him. Two things kept it from being worse: the
logic floor REFUSED the false claim rather than storing it, and rag3 diagnosed it unprompted.

THE FIX IS AT THE EARS (the Captain's ruling): the adapter knows it just replaced `<@id>` with a
name, so a LEADING mention of HIS OWN id gets back the comma a human would have typed. That is not
inference — the wire carried the signal and the adapter was throwing it away. What is asserted
below is the END of the bug, not the presence of a comma: the fixed path must COMPILE right.
"""
from types import SimpleNamespace

import pytest

from lib.core.tk import TKQuantifier
from lib.discord.client import _decode_mentions

_ME_ID = 1518880846826831922
ME = SimpleNamespace(id=_ME_ID, name="tokeniko")
OTHER = SimpleNamespace(id=42, name="hellen")


def _decode(content, mentions=(ME,), me_id=_ME_ID):
    return _decode_mentions(content, list(mentions), me_id=str(me_id))


# ---- the adapter (pure; no gateway, no Mongo) --------------------------------------------------

def test_a_leading_mention_of_him_is_restored_to_a_vocative():
    assert _decode(f"<@{_ME_ID}> the cat is a mammal") == "tokeniko, the cat is a mammal"
    assert _decode(f"<@!{_ME_ID}> every bird has feathers") == "tokeniko, every bird has feathers"


def test_existing_punctuation_is_never_doubled():
    # «@tokeniko, …» and «@tokeniko: …» already read as an address — the human punctuated it.
    assert _decode(f"<@{_ME_ID}>, the cat is a mammal") == "tokeniko, the cat is a mammal"
    assert _decode(f"<@{_ME_ID}>: hello") == "tokeniko: hello"
    assert _decode(f"<@{_ME_ID}>! hello") == "tokeniko! hello"


def test_a_mid_sentence_mention_is_content_and_is_left_alone():
    # «I told @tokeniko yesterday» names him, it does not address him — the comma would corrupt it.
    assert _decode(f"I told <@{_ME_ID}> the cat is a mammal") == "I told tokeniko the cat is a mammal"
    assert _decode(f"I agree with <@{_ME_ID}>") == "I agree with tokeniko"


def test_a_bare_mention_gets_no_comma():
    # nothing follows, so there is nothing to separate — «tokeniko,» would be a broken utterance.
    assert _decode(f"<@{_ME_ID}>") == "tokeniko"
    assert _decode(f"  <@{_ME_ID}>   ") == "tokeniko"


def test_only_HIS_mention_earns_the_comma():
    """The narrow scope, and it is narrow on EVIDENCE rather than caution.

    Measured on the live pipeline: «hellen the cat is a mammal» never suffered the theft (it splits
    into a stray leaf beside an intact clause, not a false claim), while «hellen, is a machine»
    LOSES its subject where «hellen is a machine» compiles clean. For anyone but him the comma
    would therefore cost more than it buys — and «@someone is …», the mention as SUBJECT, is a
    perfectly ordinary thing to write."""
    assert _decode("<@42> the cat is a mammal", mentions=(OTHER,)) == "hellen the cat is a mammal"
    assert _decode(f"<@42> <@{_ME_ID}> hello", mentions=(OTHER, ME)) == "hellen tokeniko hello"


def test_without_his_identity_the_decoder_behaves_exactly_as_before():
    # me_id=None is the pre-2026-08-03 contract: decode and collapse, nothing else. Kept so the
    # function stays usable (and testable) by a caller that has no gateway identity to hand.
    assert _decode_mentions(f"<@{_ME_ID}> the cat is a mammal", [ME]) == "tokeniko the cat is a mammal"


def test_unresolved_ids_and_plain_text_are_unchanged():
    assert _decode_mentions("I agree with <@999> here", []) == "I agree with here"
    assert _decode_mentions("no mentions at all", None) == "no mentions at all"
    # a LEADING id that resolves to nobody is dropped, and drops no comma with it
    assert _decode("<@999> the cat is a mammal", mentions=()) == "the cat is a mammal"


def test_the_adapter_hands_its_own_id_to_the_decoder():
    """The wiring, not the logic: _to_message must pass the bot's id or the fix is dead code."""
    import discord
    from lib.discord.client import DiscordClient

    client = DiscordClient.__new__(DiscordClient)              # no token, no gateway
    client._client = discord.Client(intents=discord.Intents.default())
    client._client._connection.user = SimpleNamespace(id=_ME_ID, name="tokeniko")

    raw = SimpleNamespace(
        id=1, author=SimpleNamespace(id=222, name="renzo"), channel=SimpleNamespace(id=333),
        guild=SimpleNamespace(id=9), content=f"<@{_ME_ID}> the cat is a mammal",
        mentions=[ME], reference=None, attachments=[],
    )
    assert client._to_message(raw).content == "tokeniko, the cat is a mammal"


# ---- END TO END: the fixed adapter output must COMPILE right -----------------------------------
# A comma in a string proves nothing. What the bug destroyed was the compiled structure, so that is
# what is asserted: the subject is the CAT, and tokeniko is nowhere in the predication.

def test_the_addressed_statement_compiles_to_a_claim_about_the_cat(compile_zip, leaves):
    heard = _decode(f"<@{_ME_ID}> the cat is a mammal")
    lvs = leaves(compile_zip(heard))
    assert len(lvs) == 1
    leaf = lvs[0]
    assert leaf.senses.get("subject") == "cat.n.01"            # the stolen subject, returned
    assert leaf.senses.get("predicate") == "mammal.n.01"
    # and the theft's own signature is gone: nothing in the clause is bound to his identity
    assert "tokeniko" not in (leaf.identities or {}).values()


def test_the_quantifier_survives_the_address(compile_zip, leaves):
    # the theft did not stop at the subject — «tokeniko every bird has feathers» compiled to
    # (tokeniko have feather): the universal went with it.
    leaf = leaves(compile_zip(_decode(f"<@{_ME_ID}> every bird has feathers")))[0]
    assert leaf.senses.get("subject") == "bird.n.01"
    assert leaf.quantifier == TKQuantifier.UNIVERSAL


def test_an_addressed_question_keeps_its_gap(compile_zip, leaves):
    # questions were hit too: «tokeniko what is a cat» compiled to (be [a] cat what).
    leaf = leaves(compile_zip(_decode(f"<@{_ME_ID}> what is a cat")))[0]
    assert leaf.dubitative == 1.0
    assert leaf.senses.get("subject") == "cat.n.01"


@pytest.mark.parametrize("raw,expected_subject", [
    (f"<@{_ME_ID}> the sky is blue", "sky.n.01"),
    (f"<@{_ME_ID}> a feline is a mammal", "feline.n.01"),
])
def test_other_addressed_statements_keep_their_subjects(compile_zip, leaves, raw, expected_subject):
    leaf = leaves(compile_zip(_decode(raw)))[0]
    assert leaf.senses.get("subject") == expected_subject


# ---- THE PLAIN-TEXT HALF (§2 cluster C2, 2026-08-11) -------------------------------------------
# The adapter above only ever sees the `<@id>` markup. Typing his name as plain text — the normal
# thing in a DM, and shorter than an @mention — walked straight into the original theft, so
# «tokeniko a sheep loves rain» still compiled to (tokeniko love rain) with the sheep GONE. That
# repair is per-transport (ATProto and the planned console inherit nothing), so the plain-text half
# lives at the PARSER — one funnel for every channel and for the brain: `_parser_leadingVocativeRetry`,
# a third sibling to the degenerate-parse and inverted-question recoveries, same contract (rewrite +
# re-parse + verify, never dep surgery).
#
# It fires on ONE measured signal: the token after the name. A DETERMINER/quantifier means the theft
# is happening; an AUX or a finite VERB means the name is the SUBJECT and the comma must stay out —
# «tokeniko is a machine that thinks» is in the corpus, and the prior art above already measured what
# an unconditional comma costs («hellen, is a machine» loses its subject). Both directions are
# asserted below on COMPILED STRUCTURE, and the one shape no signal separates is xfailed, not hidden.

@pytest.mark.parametrize("heard,expected_subject", [
    ("tokeniko a sheep loves rain", "sheep.n.01"),          # the live report, 2026-08-11
    ("tokeniko the cat is a mammal", "cat.n.01"),
    ("tokeniko every bird has feathers", "bird.n.01"),
    ("tokeniko all minds are machines", "mind.n.01"),
    ("TOKENIKO the cat is a mammal", "cat.n.01"),            # people capitalize; the gate does not care
])
def test_a_plain_text_address_keeps_its_subject(compile_zip, leaves, heard, expected_subject):
    lvs = leaves(compile_zip(heard))
    assert len(lvs) == 1
    leaf = lvs[0]
    assert leaf.senses.get("subject") == expected_subject
    # the theft's signature is gone: nothing in the clause is bound to his identity
    assert "tokeniko" not in (leaf.identities or {}).values()


def test_the_quantifier_survives_a_plain_text_address(compile_zip, leaves):
    # the mention half lost the universal with the subject; the plain-text half must not either
    leaf = leaves(compile_zip("tokeniko every bird has feathers"))[0]
    assert leaf.senses.get("subject") == "bird.n.01"
    assert leaf.quantifier == TKQuantifier.UNIVERSAL


@pytest.mark.parametrize("heard", [
    "tokeniko is a machine",
    "tokeniko is a machine that thinks",
    "tokeniko is my creator",
    "tokeniko is not a person",
    "tokeniko thinks",
    "tokeniko has a body",
    "tokeniko loves rain",
    "tokeniko knows the answer",
])
def test_him_as_the_subject_is_never_rewritten(compile_zip, leaves, heard):
    """THE GUARD, and the reason the repair is gated on the next token rather than on the name.

    A leading «tokeniko» is often a genuine SUBJECT — statements about him are how he is taught who
    he is. Measured before the fix went in: inserting the comma regardless costs the subject in 5 of
    these 8 («tokeniko, is my creator» → no subject at all), which is the same harm the mention half
    measured on «hellen, is a machine». So a finite verb or auxiliary after the name means HANDS OFF,
    and what must hold here is that he is still the one being talked ABOUT."""
    leaf = leaves(compile_zip(heard))[0]
    assert "tokeniko" in (leaf.identities or {}).values()


@pytest.mark.parametrize("heard,expected_subject", [
    ("tokeniko what is a cat", "cat.n.01"),      # stanza already tags the name `discourse` here
    ("tokeniko my cat is dead", "cat.n.01"),
])
def test_an_address_that_already_parsed_right_is_left_alone(compile_zip, leaves, heard,
                                                            expected_subject):
    # the third condition: the name must currently OCCUPY a predication role for the repair to run —
    # a wh-question and a possessive-headed subject were never stolen, so nothing is rewritten.
    leaf = leaves(compile_zip(heard))[0]
    assert leaf.senses.get("subject") == expected_subject


def test_another_name_stays_out_of_scope(compile_zip, leaves):
    # the repair keys on HIS OWN name (the parser already holds the identity), exactly as the adapter
    # keys on his own id — «hellen a sheep loves rain» never suffered the theft and is untouched.
    leaf = leaves(compile_zip("hellen a sheep loves rain"))[0]
    assert leaf.senses.get("subject") == "sheep.n.01"
    assert "tokeniko" not in (leaf.identities or {}).values()


@pytest.mark.xfail(reason="THE RESIDUE, named. An aux-fronted polar question addressed to him — "
                          "«tokeniko is the sky blue?» — keeps the theft, because its next token is "
                          "the same «is» that opens «tokeniko is a machine»: no signal separates the "
                          "two, and inserting the comma there is where the measured harm lives. "
                          "Curing it needs the inversion test (two constituents after the copula), "
                          "not a tag read. Sibling shape «tokeniko are all minds machines?» is a "
                          "SEPARATE parse bug — the comma does not cure it either (the subject is "
                          "lost with or without one).", strict=False)
def test_an_aux_fronted_polar_question_addressed_to_him(compile_zip, leaves):
    leaf = leaves(compile_zip("tokeniko is the sky blue?"))[0]
    assert leaf.senses.get("subject") == "sky.n.01"
    assert "tokeniko" not in (leaf.identities or {}).values()
