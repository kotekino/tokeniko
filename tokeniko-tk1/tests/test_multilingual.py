# ------------------------------------------------------------------------------------------------
# MULTILINGUAL AT THE EARS — the room's second tenant (§1 step 2, 2026-07-26).
#
# The Captain's rulings, mechanized and asserted: DETECTION IS LOCAL (never a cloud call — the
# privacy frame must be able to gate the cloud per stakeholder), the authority over a translation is
# the CONSENSUS OF TWO INDEPENDENT READINGS judged BY THE COMPILER (asking twice is what restores
# the authority a translation otherwise escapes), and a message that could not be read earns an
# HONEST ADMISSION rather than today's silent discard falling through to «why is that?».
#
# No live API in the gate — the readers are stubbed; the detector runs on REAL specimens and the
# verdict on REAL compiled zips.
#
# Section 8 is step 2b (THE NATIVE VOICE): the shelves themselves learn a second language, and the
# outbound translator is demoted from the primary path to the fallback layer.
# ------------------------------------------------------------------------------------------------
import json
import pathlib
import random
from types import SimpleNamespace

import pytest

from lib.core.memory import EvalToken, MEMChannels, TokenikoAction
from lib.llc.language import ENGLISH, is_english, language_not_understood, language_read


# ---- 1. THE LOCAL DETECTOR ----------------------------------------------------------------------
# The specimens the thresholds were calibrated on (2026-07-26). Kept here rather than inlined per
# test: they ARE the calibration, and a threshold moved without re-reading them is a threshold moved
# blind.
_ITALIAN = [
    "il gatto è un mammifero",
    "penso che la logica sia la base di tutto",
    "non sono d'accordo con te",
    "un cane è un animale e un gatto è un mammifero",
    "tutti gli uomini sono mortali",
    "mi chiamo Renzo e vivo in Italia",
    "il software può pensare?",
    "credo che tu sia un software",
    "i gatti mangiano carne cruda",
    "tutti gli uccelli hanno le piume",
    "questo non è vero",
    "che cosa sei tu?",
    "la logica è sacra",
    "tokeniko, che cosa sei?",
    "l'oro è un metallo",
    "un calcolatore non pensa mai",
    "Roma è in Italia",
    "gli uccelli hanno le piume e i pesci nuotano",
    "ieri ho letto un libro molto interessante",
    "secondo me la verità è importante",
]
_ENGLISH = [
    "a cat is a mammal",
    "all carnivores eat meat",
    "all humans are mortal",
    "everything that thinks exists",
    "Mari is a human",
    "kotekino is my creator",
    "the cat is on the mat",
    "gold is a metal",
    "what are you?",
    "where is Rome?",
    "i think logic is the base of everything",
    "tokeniko, what are you?",
    "tokeniko thinks logic matters",
    "a software can think",
    "not all birds fly",
    "cats eat raw meat",
    "I value logic",
    "a whale is a mammal and it feeds milk",
    "i do not agree with that claim",
    "Rome is in Italy",
    "a calculator never thinks",
    "my cat is white and gray",
    # the typo family — the whole point of a LOCAL detector: badly spelled English is still English
    # (its skeleton is English), and must never be shipped off to a translator.
    "the catt is a mamal",
    "the wrld is bg",
    "i thnk logik is the base of everythin",
    "a cat is a mamal and a dog is a animl",
    # OOV CONTENT is not a foreign language either (the ears' own gibberish specimen)
    "a wug is a blicket",
    "the zorf blicks a wug",
]


def test_italian_reads_foreign(_io):
    for sentence in _ITALIAN:
        read = language_read(sentence)
        assert read.foreign and read.measured, (sentence, read)


def test_english_never_reads_foreign(_io):
    # including the typo family: «the catt is a mamal» must stay English — its function words are
    # known and its skeleton parses, however the content words are spelled.
    for sentence in _ENGLISH:
        read = language_read(sentence)
        assert not read.foreign, (sentence, read)


def test_detection_measured_margins(_io):
    # pin the calibration the two thresholds rest on (LANG_STOPWORD_FLOOR 0.30 = the ENGLISH
    # FUNCTION-WORD ratio; LANG_UNKNOWN_TAG_CEIL 0.30 = the ratio the English tagger cannot place,
    # PROPN/X). FOREIGN requires BOTH — neither signal survives alone (a bare-content English
    # sentence scores stop≈0; an English sentence full of names scores odd≈0.5).
    #
    # measured 2026-07-26 over the corpora above (only specimens of ≥ LANG_MIN_TOKENS words):
    #   english   stop 0.00–1.00 · odd 0.00–0.50   -> 0/29 called foreign
    #   italian   stop 0.00–0.25 · odd 0.33–1.00   -> 20/20 called foreign
    #   worst margins (0.05 each side): english «tokeniko thinks logic matters» odd 0.25 (ceiling
    #   0.30); italian «Roma è in Italia» stop 0.25 (floor 0.30).
    #
    # NOTE the FIRST candidate — an OOV rate over the spaCy-lg vectors — was measured and REJECTED:
    # the lg vector table is enormous and multilingual, so «penso che la logica sia la base di
    # tutto» scores 0.00 OOV (every word has a vector) and «the catt is a mamal» scores 0.00 too
    # (the misspellings have vectors). That signal does not exist; this one does.
    from lib.llc.language import _MIN_TOKENS, _ODD_CEIL, _STOP_FLOOR, language_signals

    it = [language_signals(s) for s in _ITALIAN]
    en = [language_signals(s) for s in _ENGLISH]
    it = [(a, b) for a, b, n in it if n >= _MIN_TOKENS]
    en = [(a, b) for a, b, n in en if n >= _MIN_TOKENS]

    # every Italian specimen clears BOTH gates (an un-English skeleton AND unplaceable words)…
    assert max(stop for stop, _ in it) < _STOP_FLOOR
    assert min(odd for _, odd in it) > _ODD_CEIL
    # …and no English one clears both (each is saved by at least one axis)
    assert not [1 for stop, odd in en if stop < _STOP_FLOOR and odd > _ODD_CEIL]
    # the margins are real but THIN at the extremes — pinned so a threshold move is a deliberate act
    assert _STOP_FLOOR - max(stop for stop, _ in it) >= 0.04
    assert min(odd for _, odd in it) - _ODD_CEIL >= 0.02


def test_short_message_inherits_the_room(_io):
    # the minimum-token guard: «sì» is Italian because the ROOM is, not because a detector guessed.
    # Never MEASURED, whatever the room says — the signals are meaningless on two words.
    for short in ("sì", "sì, esatto", "grazie mille", "yes", "ok"):
        in_italian = language_read(short, room_lang="italian")
        in_english = language_read(short, room_lang=ENGLISH)
        cold = language_read(short, room_lang=None)
        assert in_italian.foreign and not in_italian.measured, short
        assert not in_english.foreign and not in_english.measured, short
        assert not cold.foreign and not cold.measured, short   # no room, no guess


def test_detection_is_sticky_and_self_correcting(_io):
    # a confidently-ENGLISH turn re-reads the room to english (measured, so /input may write it
    # back); an AMBIGUOUS one is never measured, so the room's language is left exactly as it was.
    english_turn = language_read("the cat is on the mat", room_lang="italian")
    assert english_turn.measured and not english_turn.foreign and english_turn.lang == ENGLISH
    ambiguous = language_read("cats eat raw meat", room_lang="italian")     # stop≈0, odd≈0
    assert not ambiguous.measured and ambiguous.lang == "italian"           # inherits, writes nothing


def test_detection_is_local(_io, monkeypatch):
    # the privacy frame (§1 step 3) must be able to gate every cloud call per stakeholder — a cloud
    # language-detect would BE such a call. With the cloud disarmed entirely, detection still works.
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("RAG4_DISABLED", "1")
    from lib.llc.language import translator_enabled
    assert translator_enabled() is False
    assert language_read("il gatto è un mammifero").foreign is True


def test_english_label_normalization():
    for label in ("english", "English", "EN", "eng", "English (US)", "en-GB"):
        assert is_english(label), label
    for label in ("italian", "Italiano", "french", None, ""):
        assert not is_english(label), label


# ---- 2. THE CONSENSUS OF TWO INDEPENDENT READINGS -----------------------------------------------
# The compiler judges whether the two readings agree — the same three-way verdict the ears already
# speak, over the same primitives (no duplicated comparison logic).

def test_agreeing_readings_accept(compile_zip):
    from lib.llc.normalizer import translation_verdict
    # two renderings of the same Italian that compile to the same claims -> ACCEPT
    verdict, note = translation_verdict(
        compile_zip("a cat is a mammal and a dog is an animal"),
        compile_zip("a cat is a mammal. a dog is an animal."))
    assert verdict == "ACCEPT", note


def test_identical_readings_are_unanimous(compile_zip):
    from lib.llc.normalizer import translation_verdict
    verdict, note = translation_verdict(compile_zip("a cat is a mammal"),
                                        compile_zip("a cat is a mammal"))
    assert verdict == "ACCEPT" and "unanimous" in note


def test_unanimous_fragment_is_still_understood(compile_zip):
    # «sì» -> «yes» from both readers: a FRAGMENT the verifier would refuse as unsound, yet the two
    # independent readings are identical — there is nothing to adjudicate. Without this tier every
    # short answer in Italian would earn «I did not understand», which is the opposite of the truth.
    from lib.llc.normalizer import translation_verdict
    verdict, note = translation_verdict(compile_zip("yes"), compile_zip("yes"))
    assert verdict == "ACCEPT" and "unanimous" in note


def test_coherent_disagreement_asks(compile_zip):
    # both readings compile soundly but say DIFFERENT things, close enough to be a plausible
    # re-hearing -> ASK (brick 1's «did you mean: …?» loop, reused whole)
    from lib.llc.normalizer import translation_verdict
    verdict, note = translation_verdict(compile_zip("the cat is on the mat"),
                                        compile_zip("the cat is on the bed"))
    assert verdict == "ASK", note


def test_far_apart_readings_discard(compile_zip):
    from lib.llc.normalizer import translation_verdict
    verdict, note = translation_verdict(compile_zip("a cat is a mammal"),
                                        compile_zip("a rock is a mineral"))
    assert verdict == "DISCARD", note


def test_divergent_unsound_reading_discards(compile_zip):
    # a divergence can only be judged between two readings the compiler can hold: if either still
    # stumbles, the pair proves nothing -> DISCARD (the admission), never an offer.
    from lib.llc.normalizer import translation_verdict
    verdict, note = translation_verdict(compile_zip("a cat is a mammal"),
                                        compile_zip("a wug is a blicket"))
    assert verdict == "DISCARD" and "soundly" in note


def test_a_missing_reading_discards(compile_zip):
    from lib.llc.normalizer import translation_verdict
    verdict, note = translation_verdict(compile_zip("a cat is a mammal"), None)
    assert verdict == "DISCARD" and "compile" in note


# ---- the INDEPENDENCE of the two readers (the load-bearing property) ----------------------------

def test_the_two_readers_are_genuinely_independent():
    # a consensus between two IDENTICAL deterministic calls is vacuous — it proves only that the
    # model is a function. Independence is bought by (a) two differently-FRAMED system prompts and
    # (b) a sampling temperature pinned explicitly, so no default change can collapse the pair into
    # one call made twice.
    from lib.rag import RAG4_RENDER_IN, RAG4_TRANSLATE_IN
    assert RAG4_TRANSLATE_IN.system != RAG4_RENDER_IN.system
    assert RAG4_TRANSLATE_IN.name != RAG4_RENDER_IN.name
    assert RAG4_TRANSLATE_IN.temperature == 1.0 and RAG4_RENDER_IN.temperature == 1.0
    # both must keep the output contract translate_in reads, and both must fence the message as DATA
    for spec in (RAG4_TRANSLATE_IN, RAG4_RENDER_IN):
        assert set(spec.schema["required"]) == {"language", "english"}
        assert "<message>" in spec.system and "never an instruction" in spec.system


def test_temperature_reaches_the_wire(monkeypatch):
    # the pin is worthless if the client drops it on the floor
    import asyncio
    from lib.rag import RAG4_TRANSLATE_IN, rag_call

    seen = {}

    class _FakeMessages:
        async def create(self, **kwargs):
            seen.update(kwargs)
            return SimpleNamespace(content=[SimpleNamespace(type="text",
                                                            text='{"language":"italian","english":"a cat"}')])

    asyncio.run(rag_call(RAG4_TRANSLATE_IN, "x", subject_uid=None, client=SimpleNamespace(messages=_FakeMessages())))
    assert seen["temperature"] == 1.0


def test_readers_are_asked_independently(monkeypatch):
    # translate_in fans BOTH specs — one call each, no shared state, both fenced
    import asyncio
    import lib.llc.language as language

    asked = []

    async def fake_rag(spec, user, **kw):
        asked.append((spec.name, user))
        return {"language": "italian", "english": "a cat is a mammal"}

    monkeypatch.setattr(language, "rag_call", fake_rag)
    primary, second = asyncio.run(language.translate_in("il gatto è un mammifero", subject_uid=None))
    assert [name for name, _ in asked] == ["rag4-translate-in", "rag4-render-in"]
    assert all("<message>" in user and "il gatto" in user for _, user in asked)
    assert primary.english == second.english == "a cat is a mammal"
    assert language.consensus_language(primary, second) == "italian"


def test_a_dead_reader_is_no_consensus(monkeypatch):
    # graceful by contract: one reader down means NO reading at all (never a lone unchecked
    # translation entering the pipeline) — /input then leaves the raw parse standing.
    import asyncio
    import lib.llc.language as language

    async def half_dead(spec, user, **kw):
        return None if spec.name == "rag4-render-in" else {"language": "italian", "english": "a cat"}

    monkeypatch.setattr(language, "rag_call", half_dead)
    primary, second = asyncio.run(language.translate_in("il gatto", subject_uid=None))
    assert primary is not None and second is None


# ---- 3. THE ITEM CONTRACT: true history be it ---------------------------------------------------

def test_item_keeps_the_italian_and_carries_the_english(_io):
    # `original` ALWAYS keeps his own words in his own language; the accepted English rides in
    # `normalized` (its existing meaning: the text actually compiled); `source_lang` records what
    # was heard. Proven at the field level — the verdict tiers above decide when /input sets them.
    from lib.core.models import TKMemoryItemDoc
    item = TKMemoryItemDoc(original="il gatto è un mammifero", zip=None,
                           sourceId="lang-store-test",
                           normalized="the cat is a mammal", source_lang="italian")
    item.insert()
    try:
        fetched = TKMemoryItemDoc.get(item.id).run()
        assert fetched.original == "il gatto è un mammifero"   # true history be it
        assert fetched.normalized == "the cat is a mammal"
        assert fetched.source_lang == "italian"
        assert language_not_understood(fetched) is False       # it WAS understood
    finally:
        TKMemoryItemDoc.get_motor_collection().delete_many({"sourceId": "lang-store-test"})


def test_not_understood_is_derivable_not_a_flag():
    # the state needs NO new boolean: a translation was attempted (source_lang) and nothing usable
    # came back (no normalized English, no offerable reading).
    def item(**kw):
        return SimpleNamespace(source_lang=None, normalized=None, suggested_reading=None, **kw)
    assert language_not_understood(item()) is False                      # an English message
    assert language_not_understood(SimpleNamespace(source_lang="italian", normalized=None,
                                                   suggested_reading=None)) is True
    assert language_not_understood(SimpleNamespace(source_lang="italian",
                                                   normalized="the cat is a mammal",
                                                   suggested_reading=None)) is False   # ACCEPT
    assert language_not_understood(SimpleNamespace(source_lang="italian", normalized=None,
                                                   suggested_reading="the cat is a mammal")) is False  # ASK


# ---- 3b. THE WIRED CHAIN (/input end to end, the readers stubbed) -------------------------------

@pytest.fixture()
def wired(_io, monkeypatch):
    # the real /input handler over the real pipeline, with the two readers stubbed and rag1 muted
    # (the English tidy is a separate instrument with its own gate — isolate the language step).
    import api.main as main
    from lib.core.models import TKExchangeDoc, TKMemoryItemDoc, TKMemoryStakeholdersDoc
    tok, ai = _io
    main.app.state.tokeniko, main.app.state.ai_client = tok, ai
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.delenv("RAG4_DISABLED", raising=False)
    monkeypatch.setenv("RAG1_DISABLED", "1")
    talker = "cavaliere@lang-test:5"
    yield main, talker
    sh = TKMemoryStakeholdersDoc.find_one({"uid": talker}).run()
    if sh is not None:
        TKMemoryItemDoc.get_motor_collection().delete_many({"sourceId": str(sh.id)})
        from lib.core.trust import resolve_canonical
        soul = resolve_canonical(str(sh.id))
        if soul is not None:
            TKExchangeDoc.get_motor_collection().delete_many({"user_uid": soul.uid})
        TKMemoryStakeholdersDoc.get_motor_collection().delete_many({"uid": talker})


def _readers(monkeypatch, first: str, second: str, lang: str = "italian"):
    import lib.llc.language as language

    async def fake_rag(spec, user, **kw):
        return {"language": lang,
                "english": first if spec.name == "rag4-translate-in" else second}

    monkeypatch.setattr(language, "rag_call", fake_rag)


def _ingest(main, talker, sentence):
    import asyncio
    from lib.core.models import TKMemoryItemDoc
    out = asyncio.run(main.process(tokens=sentence, talker=talker, talker_name="cavaliere",
                                   channel=MEMChannels.DISCORD.value, directedness=1.0,
                                   metadata=json.dumps({"channel_id": "sala-chan"})))
    assert out["status"] == "complete", out
    return TKMemoryItemDoc.find({"original": sentence}).sort("-timestamp").limit(1).to_list()[0]


def test_input_accepts_agreeing_readings(wired, monkeypatch):
    # the whole chain: Italian in -> two agreeing readings -> the ENGLISH is what compiles, the
    # ITALIAN is what is remembered, and the room learns the language.
    main, talker = wired
    _readers(monkeypatch, "a cat is a mammal", "a cat is a mammal")
    item = _ingest(main, talker, "il gatto è un mammifero")
    assert item.original == "il gatto è un mammifero"      # true history be it
    assert item.normalized == "a cat is a mammal"          # the text actually compiled
    assert item.source_lang == "italian"
    assert item.zip is not None and item.suggested_reading is None
    assert language_not_understood(item) is False
    # the zip really is the ENGLISH one: a mammal sense is in it, and it is no longer a stumble
    from lib.llc.normalizer import detector_stumbles
    assert detector_stumbles(item.zip) is False

    from lib.core.io import get_exchange
    from lib.core.trust import resolve_canonical
    soul = resolve_canonical(item.sourceId)
    room = get_exchange(soul.uid, "sala-chan")
    assert room.lang == "italian" and room.lang_set_by == str(item.id)


def test_input_offers_a_coherent_disagreement(wired, monkeypatch):
    # the readers part ways coherently -> the PRIMARY rides as suggested_reading and the raw
    # (Italian) parse still stands: asking is not believing.
    main, talker = wired
    _readers(monkeypatch, "the cat is on the mat", "the cat is on the bed")
    item = _ingest(main, talker, "il gatto è sul tappeto in cucina")
    assert item.source_lang == "italian"
    assert item.suggested_reading == "the cat is on the mat"
    assert item.normalized is None                        # nothing was believed
    assert language_not_understood(item) is False         # …but something WAS offered


def test_input_admits_an_unreadable_message(wired, monkeypatch):
    # the readings do not hold together -> nothing usable: the item is stored from its raw parse,
    # the not-understood state is derivable, and the failure joins the triage corpus as its OWN
    # category (an untranslatable message is a diagnostic lead, not a hallucination).
    main, talker = wired
    from lib.core.models import TKZipDebugDoc
    _readers(monkeypatch, "a cat is a mammal", "a rock is a mineral")
    item = _ingest(main, talker, "tutti gli uomini sono mortali")
    try:
        assert item.source_lang == "italian"
        assert item.normalized is None and item.suggested_reading is None
        assert language_not_understood(item) is True
        lead = TKZipDebugDoc.find_one({"item_id": str(item.id)}).run()
        assert lead is not None
        assert lead.category == "ears-translation" and lead.severity == "medium"
        assert lead.verdict == "mismatch" and lead.confidence == 1.0
        assert "a rock is a mineral" in lead.note        # both readings ride in the note
    finally:
        TKZipDebugDoc.get_motor_collection().delete_many({"item_id": str(item.id)})


def test_input_leaves_english_untouched(wired, monkeypatch):
    # an English exchange is byte-identical to before the multilingual step: no reader is asked, no
    # source_lang is recorded, and the room simply learns that this room speaks English.
    main, talker = wired
    import lib.llc.language as language

    async def never(spec, user, **kw):
        raise AssertionError("an English message must never reach a translator")

    monkeypatch.setattr(language, "rag_call", never)
    item = _ingest(main, talker, "the cat is on the mat")
    assert item.source_lang is None and item.normalized is None
    assert item.original == "the cat is on the mat" and item.zip is not None
    from lib.core.io import get_exchange
    from lib.core.trust import resolve_canonical
    room = get_exchange(resolve_canonical(item.sourceId).uid, "sala-chan")
    assert room.lang == ENGLISH


def test_input_takes_the_readers_correction(wired, monkeypatch):
    # a LOCAL false positive is cheap and self-correcting: both independent readers name the
    # message English, so the original words stand untouched and the room stays English.
    main, talker = wired
    _readers(monkeypatch, "al catz eet raw meet", "al catz eet raw meet", lang="english")
    item = _ingest(main, talker, "al catz eet raw meet")   # the known blind spot: reads foreign
    assert item.source_lang is None and item.normalized is None
    assert item.original == "al catz eet raw meet"
    from lib.core.io import get_exchange
    from lib.core.trust import resolve_canonical
    room = get_exchange(resolve_canonical(item.sourceId).uid, "sala-chan")
    assert room.lang == ENGLISH


def test_input_falls_through_when_a_reader_is_down(wired, monkeypatch):
    # graceful by contract: no consensus is possible, so nothing is claimed — the raw parse stands
    # exactly as today and NOTHING is recorded (no half-heard language, no false admission).
    main, talker = wired
    import lib.llc.language as language

    async def dead(spec, user, **kw):
        return None

    monkeypatch.setattr(language, "rag_call", dead)
    item = _ingest(main, talker, "tutti gli uccelli hanno le piume")
    assert item.source_lang is None and item.normalized is None
    assert language_not_understood(item) is False     # never an admission the ears did not earn


# ---- 4. THE ROOM'S SECOND TENANT ----------------------------------------------------------------

@pytest.fixture()
def lang_room(_io):
    from lib.core.models import TKExchangeDoc, TKMemoryStakeholdersDoc
    sh = TKMemoryStakeholdersDoc(uid="parla@lang-test:1", name="parla", isMe=False,
                                 channel=MEMChannels.DISCORD, trust=0.5).save()
    yield sh
    TKExchangeDoc.get_motor_collection().delete_many({"user_uid": sh.uid})
    TKMemoryStakeholdersDoc.get_motor_collection().delete_many({"uid": sh.uid})


def test_room_language_written_and_read(lang_room):
    from api.main import _room_language_write, _room_read
    from lib.core.io import get_exchange
    sh = lang_room
    metadata = json.dumps({"channel_id": "lang-chan", "message_id": "m-1"})

    # cold: the api READS the room without minting one (a room is born of a processed turn)
    room, soul_uid, key = _room_read(sh, metadata, MEMChannels.DISCORD)
    assert room is None and soul_uid == sh.uid and key == "lang-chan"

    _room_language_write(soul_uid, key, "italian", "item-1")
    room = get_exchange(sh.uid, "lang-chan")
    assert room.lang == "italian"
    assert room.lang_set_by == "item-1"          # a REFERENCE to the item that decided it
    # …and the next message in that room now reads its language back
    again, _, _ = _room_read(sh, metadata, MEMChannels.DISCORD)
    assert again.lang == "italian"
    assert language_read("sì", again.lang).foreign is True    # the short turn inherits it

    # self-correcting: a confidently-English turn moves it back, referencing its own item
    _room_language_write(soul_uid, key, ENGLISH, "item-2")
    room = get_exchange(sh.uid, "lang-chan")
    assert room.lang == ENGLISH and room.lang_set_by == "item-2"


def test_room_language_write_is_a_no_op_when_unchanged(lang_room):
    from api.main import _room_language_write
    from lib.core.io import get_exchange
    sh = lang_room
    _room_language_write(sh.uid, "lang-chan", "italian", "item-1")
    before = get_exchange(sh.uid, "lang-chan").updated_at
    _room_language_write(sh.uid, "lang-chan", "italian", "item-9")
    room = get_exchange(sh.uid, "lang-chan")
    assert room.lang_set_by == "item-1" and room.updated_at == before   # no churn, no re-reference


def test_room_key_is_one_definition(_io):
    # api / senses / brain must agree on what "the same room" is — one definition, three callers
    from brain.context import channel_key
    from lib.core.io import exchange_channel_key
    meta = json.dumps({"channel_id": "c-42"})
    item = SimpleNamespace(metadata=meta, channel=MEMChannels.DISCORD)
    assert channel_key(item) == exchange_channel_key(meta, MEMChannels.DISCORD) == "c-42"
    bare = SimpleNamespace(metadata=None, channel=MEMChannels.API)
    assert channel_key(bare) == exchange_channel_key(None, MEMChannels.API) == "api"


# ---- 5. THE ADMISSION ---------------------------------------------------------------------------

@pytest.fixture()
def admission_world(_io):
    from lib.core.models import (TKBehaviorRuleDoc, TKExchangeDoc, TKIdeaDoc,
                                 TKMemoryItemDoc, TKMemoryStakeholdersDoc)
    # BOTH rules seeded: the admission AND the generic unknown-why — so a working admission path is
    # PROVEN to route the honest reply and SUPPRESS the nonsense one (they would otherwise co-fire).
    for rule in (TKBehaviorRuleDoc(trigger=EvalToken.NOT_UNDERSTOOD.value,
                                   action=TokenikoAction.ASK.value, urge=0.7),
                 TKBehaviorRuleDoc(trigger=EvalToken.UNKNOWN.value,
                                   action=TokenikoAction.WHY.value, urge=0.6),
                 TKBehaviorRuleDoc(trigger=EvalToken.QUESTION.value,
                                   action=TokenikoAction.ANSWER.value, urge=0.9)):
        rule.insert()
    sh = TKMemoryStakeholdersDoc(uid="muto@lang-test:7", name="muto", isMe=False,
                                 channel=MEMChannels.DISCORD, trust=0.5).save()
    yield {"speaker": sh}
    triggers = [EvalToken.NOT_UNDERSTOOD.value, EvalToken.UNKNOWN.value, EvalToken.QUESTION.value]
    TKBehaviorRuleDoc.get_motor_collection().delete_many({"trigger": {"$in": triggers}})
    TKIdeaDoc.get_motor_collection().delete_many({"trigger": {"$in": triggers}})
    TKMemoryItemDoc.get_motor_collection().delete_many({"sourceId": str(sh.id)})
    TKExchangeDoc.get_motor_collection().delete_many({"user_uid": sh.uid})
    TKMemoryStakeholdersDoc.get_motor_collection().delete_many({"uid": sh.uid})


def _unread_item(speaker_id, compile_zip, original="questo non è vero", lang="italian"):
    # what /input stores on a DISCARD: the raw (foreign) parse stands, source_lang records the
    # attempt, and neither an English nor an offerable reading exists.
    from lib.core.models import TKMemoryItemDoc
    item = TKMemoryItemDoc(
        original=original, zip=compile_zip(original), sourceId=speaker_id,
        channel=MEMChannels.DISCORD, directedness=1.0, source_lang=lang,
        metadata=json.dumps({"channel_id": "muto-chan", "message_id": "m-1"}),
    )
    item.insert()
    return item


def test_admission_replaces_the_whole_content_path(admission_world, compile_zip):
    import time
    from brain.thinking import think_one
    from lib.core.models import TKBrainStateDoc, TKIdeaDoc
    sh = admission_world["speaker"]
    item = _unread_item(str(sh.id), compile_zip)
    bs = TKBrainStateDoc(key="lang-test-state", wake_at=time.time() - 5).insert()
    try:
        assert think_one(bs) is True
        admission = TKIdeaDoc.find_one({"trigger": EvalToken.NOT_UNDERSTOOD.value,
                                        "source": str(item.id)}).run()
        assert admission is not None
        assert admission.action_token == TokenikoAction.ASK.value
        assert admission.target == str(sh.id)          # directed at the person he could not read
        # nothing was understood, so NOTHING was reacted to: no why, no verdict, no trust echo
        assert TKIdeaDoc.find_one({"trigger": EvalToken.UNKNOWN.value,
                                   "source": str(item.id)}).run() is None
        assert TKIdeaDoc.find({"source": str(item.id)}).to_list().__len__() == 1
    finally:
        TKBrainStateDoc.get_motor_collection().delete_many({"key": "lang-test-state"})


def test_an_unread_question_is_never_answered(admission_world, compile_zip):
    # the gate stands BEFORE the mood branch: a foreign question compiles to a garbage zip that
    # still ends in «?» — answering it would be «I do not know» to a message never heard.
    import time
    from brain.thinking import think_one
    from lib.core.models import TKBrainStateDoc, TKIdeaDoc
    sh = admission_world["speaker"]
    item = _unread_item(str(sh.id), compile_zip, original="che cosa sei tu?")
    bs = TKBrainStateDoc(key="lang-test-q-state", wake_at=time.time() - 5).insert()
    try:
        assert think_one(bs) is True
        assert TKIdeaDoc.find_one({"trigger": EvalToken.QUESTION.value,
                                   "source": str(item.id)}).run() is None
        assert TKIdeaDoc.find_one({"trigger": EvalToken.NOT_UNDERSTOOD.value,
                                   "source": str(item.id)}).run() is not None
    finally:
        TKBrainStateDoc.get_motor_collection().delete_many({"key": "lang-test-q-state"})


def test_admission_opens_no_pending(admission_world, compile_zip):
    # an admission is NOT an offer to confirm — a rephrase is simply a new message. The room stays
    # exactly as it was (nothing to bind, nothing to lapse).
    from brain.thinking import _react_not_understood
    from lib.core.models import TKExchangeDoc
    sh = admission_world["speaker"]
    item = _unread_item(str(sh.id), compile_zip)
    assert _react_not_understood(item) is True
    assert TKExchangeDoc.find_one({"user_uid": sh.uid, "channel_id": "muto-chan"}).run() is None


def test_admission_speaks_the_honest_line():
    from brain.compose import compose_raw
    from lib.core.voice import _FALLBACK
    raw = compose_raw(TokenikoAction.ASK.value, EvalToken.NOT_UNDERSTOOD.value, None)
    assert raw == _FALLBACK["not_understood"]
    assert raw and "{" not in raw          # slot-less: there is nothing to name


def test_admission_is_exempt_from_the_curiosity_cooldown(admission_world):
    # the admission rides tokeniko:ask, which is throttled ONE-per-teacher-per-window for the
    # CURIOSITY question. Swallowing «I did not understand that» inside that window would leave the
    # human talking to a wall — so the admission is exempt, like the did-you-mean before it, while
    # the curiosity ask still throttles.
    import time
    from brain.behavior import plan_action
    from lib.core.memory import ActionType
    from lib.core.models import TKActionDoc, TKIdeaDoc
    sh = admission_world["speaker"]
    target = str(sh.id)
    recent = TKActionDoc(action_type=ActionType.SEND_MESSAGE, sourceId="me", targetId=target,
                         channel=MEMChannels.DISCORD,
                         payload={"action_token": TokenikoAction.ASK.value},
                         createdAt=int(time.time())).insert()
    try:
        def _idea(trigger):
            return TKIdeaDoc(trigger=trigger, action_token=TokenikoAction.ASK.value, urge=0.7,
                             target=target)
        assert plan_action(_idea(EvalToken.NOT_UNDERSTOOD.value), "me") is not None   # exempt
        assert plan_action(_idea(EvalToken.LEARNED.value), "me") is None              # throttled
    finally:
        TKActionDoc.get_motor_collection().delete_many({"_id": recent.id})


# ---- 6. THE OUTBOUND VOICE ----------------------------------------------------------------------

def _run(coro):
    import asyncio
    return asyncio.run(coro)


@pytest.fixture()
def out_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.delenv("RAG4_DISABLED", raising=False)
    monkeypatch.setenv("RAG2_OUT_DISABLED", "1")   # isolate the language step from the polish
    from senses import outbound
    return outbound


def _stub_translation(monkeypatch, translated: str, back: str):
    import lib.llc.language as language

    async def fake_out(text, lang, subject_uid=None):
        return translated

    async def fake_back(text, subject_uid=None):
        return back

    monkeypatch.setattr(language, "translate_out", fake_out)
    monkeypatch.setattr(language, "back_translate", fake_back)


def test_verified_round_trip_ships_the_translation(out_env, monkeypatch):
    outbound = out_env
    monkeypatch.setattr(outbound, "_room_language", lambda uid, chan: "italian")
    _stub_translation(monkeypatch, "non sono d'accordo con questo",
                      "I do not agree with this claim")
    monkeypatch.setattr(outbound, "_verify_voice", lambda raw, back: {"ok": True, "note": "verified"})
    out = _run(outbound._voice_out("I do not agree with that claim", "uid", "chan"))
    assert out == "non sono d'accordo con questo"


def test_unverified_round_trip_ships_the_english(out_env, monkeypatch):
    # the voice may change language, NEVER meaning — exactly like a rejected polish
    outbound = out_env
    monkeypatch.setattr(outbound, "_room_language", lambda uid, chan: "italian")
    _stub_translation(monkeypatch, "sono d'accordo con questo", "I agree with this claim")
    monkeypatch.setattr(outbound, "_verify_voice",
                        lambda raw, back: {"ok": False, "note": "sound leaf dropped/altered"})
    raw = "I do not agree with that claim"
    assert _run(outbound._voice_out(raw, "uid", "chan")) == raw


def test_lossless_round_trip_needs_no_judge(out_env, monkeypatch):
    # a FRAGMENT is unverifiable by construction (verifier_voice refuses an unsound raw) — so «yes»
    # could never become «sì» through the judge. An IDENTICAL round trip is a stronger proof than
    # the judge could give, and it is what lets him answer in the room's language at all.
    outbound = out_env
    monkeypatch.setattr(outbound, "_room_language", lambda uid, chan: "italian")
    _stub_translation(monkeypatch, "sì", "Yes.")
    called = []
    monkeypatch.setattr(outbound, "_verify_voice",
                        lambda raw, back: called.append(1) or {"ok": False})
    assert _run(outbound._voice_out("yes", "uid", "chan")) == "sì"
    assert called == []                       # no judge was needed, none was asked


def test_an_english_room_is_byte_identical(out_env, monkeypatch):
    # nothing changes for an English exchange: no room language, no cloud call, the same string
    outbound = out_env
    monkeypatch.setattr(outbound, "_room_language", lambda uid, chan: None)
    import lib.llc.language as language

    async def never(*args, **kw):
        raise AssertionError("no translation call may happen in an English room")

    monkeypatch.setattr(language, "translate_out", never)
    raw = "you are right — I no longer hold that all software are minds"
    assert _run(outbound._voice_out(raw, "uid", "chan")) == raw
    assert _run(outbound._voice_out(raw)) == raw          # and with no room key at all


def test_translator_kill_switch_ships_the_english(out_env, monkeypatch):
    outbound = out_env
    monkeypatch.setenv("RAG4_DISABLED", "1")
    monkeypatch.setattr(outbound, "_room_language",
                        lambda uid, chan: pytest.fail("the kill-switch must precede the room read"))
    raw = "I do not agree with that claim"
    assert _run(outbound._voice_out(raw, "uid", "chan")) == raw


def test_room_language_reader_ignores_english_and_missing_rooms(lang_room, out_env):
    from api.main import _room_language_write
    outbound = out_env
    sh = lang_room
    assert outbound._room_language(sh.uid, "voce-chan") is None       # no room yet
    _room_language_write(sh.uid, "voce-chan", ENGLISH, "item-1")
    assert outbound._room_language(sh.uid, "voce-chan") is None       # english is not a translation
    _room_language_write(sh.uid, "voce-chan", "italian", "item-2")
    assert outbound._room_language(sh.uid, "voce-chan") == "italian"


def test_the_blog_stays_english_by_construction():
    # the public journal is written in English and must never be routed through the chat carrier's
    # voice seam. Asserted STRUCTURALLY, not by a special case: blog.py does not import outbound at
    # all (it shares only the /voice/verify seam through voicegate), and the two executors drain
    # DISJOINT channels — PUBLIC vs DISCORD.
    import senses.blog as blog
    import senses.blog_outbound as blog_outbound
    import senses.outbound as outbound
    from lib.core.memory import MEMChannels

    source = pathlib.Path(blog.__file__).read_text()
    assert "senses.outbound" not in source and "_voice_out" not in source.replace(
        "# PER-LINE consensus (the rag2-out contract, blog-side — mirrors _voice_out exactly): each", "")
    assert not hasattr(blog, "_voice_out") and not hasattr(blog_outbound, "_voice_out")
    blog_src = pathlib.Path(blog_outbound.__file__).read_text()
    assert MEMChannels.PUBLIC.value in blog_src and "senses.outbound" not in blog_src
    assert MEMChannels.DISCORD.value in pathlib.Path(outbound.__file__).read_text()


# ---- 7. THE MIMICRY FENCE (the Captain's ruling on the translated-turn coupling) ----------------

@pytest.fixture()
def mimic_speaker(_io, monkeypatch):
    from lib.core.models import TKMemoryStakeholdersDoc, TKScaffoldDoc
    sh = TKMemoryStakeholdersDoc(uid="specchio@lang-test:3", name="specchio", isMe=False,
                                 channel=MEMChannels.DISCORD, trust=0.9).save()
    # clear the gates that are not under test here (momentum + the Lane B classifier)
    import brain.context as context
    import brain.mimicry as mimicry
    monkeypatch.setattr(context, "talker_depth", lambda key, uid: 99)
    monkeypatch.setattr(mimicry, "_lane_b_category", lambda zip_obj: "agree")
    yield sh
    TKScaffoldDoc.get_motor_collection().delete_many({"scope": sh.uid})
    TKMemoryStakeholdersDoc.get_motor_collection().delete_many({"uid": sh.uid})


def _mimic_item(sh, original, zip_obj, source_lang=None):
    return SimpleNamespace(sourceId=str(sh.id), original=original, zip=zip_obj, social=None,
                           metadata=json.dumps({"channel_id": "mimic-chan"}),
                           channel=MEMChannels.DISCORD, source_lang=source_lang)


def test_a_translated_turn_lends_no_phrasing(mimic_speaker, compile_zip):
    # the template is `original` VERBATIM — on a translated turn that is the SOURCE language, while
    # the zip that matched is English. An unlabelled Italian row in an English shelf is a guessed
    # string: nothing is learned from a translated turn until the language-aware version exists.
    from brain.mimicry import mimic_observe
    from lib.core.models import TKScaffoldDoc
    sh = mimic_speaker
    item = _mimic_item(sh, "sono d'accordo", compile_zip("that fits what I believe"),
                       source_lang="italian")
    assert mimic_observe(item) is False
    assert TKScaffoldDoc.find({"scope": sh.uid}).to_list() == []


def test_an_english_turn_still_lends_phrasing(mimic_speaker, compile_zip):
    from brain.mimicry import mimic_observe
    from lib.core.models import TKScaffoldDoc
    sh = mimic_speaker
    template = "yeah that tracks for me too"
    TKScaffoldDoc.get_motor_collection().delete_many({"template": template})
    try:
        assert mimic_observe(_mimic_item(sh, template,
                                         compile_zip("that fits what I believe"))) is True
        row = TKScaffoldDoc.find_one({"scope": sh.uid, "template": template}).run()
        assert row is not None and row.provenance == f"mimic:{sh.uid}"
    finally:
        TKScaffoldDoc.get_motor_collection().delete_many({"template": template})


# ---- VERBATIM acts: unpolished, but NOT untranslated (the author's ruling, 2026-07-26) ------------
# The anecdote and the reduct skip the POLISHER (their register is the point — a side-note's «by the
# way» is discourse framing the zip cannot see, and a reduct's quoted premises must not be reworded).
# They do NOT skip LOCALIZATION: a reply in Italian carrying an English aside is not one voice. For a
# non-English teacher it is in fact the faithful choice — their words were translated INTO English at
# the ears, so quoting the premise back in their own tongue lands nearer what they actually said.

def test_verbatim_acts_are_localized_but_never_polished(out_env, monkeypatch):
    from lib.core.memory import TokenikoAction
    outbound = out_env
    polished = []

    async def fake_polish(raw, subject_uid=None):
        polished.append(raw)                      # must never be reached for a VERBATIM act
        return "polished away"

    monkeypatch.setattr(outbound, "_polish", fake_polish)
    monkeypatch.setattr(outbound, "_room_language", lambda uid, chan: "italian")
    _stub_translation(monkeypatch, "a proposito, l'oro è bello", "by the way, gold is beautiful")
    monkeypatch.setattr(outbound, "_verify_voice", lambda raw, back: {"ok": True, "note": "verified"})

    # the gating expression exactly as deliver_one computes it (the test_voice_out precedent)
    raw = "by the way, gold is beautiful"
    payload = {"action_token": TokenikoAction.MENTION.value, "raw": raw}
    _VERBATIM = {TokenikoAction.MENTION.value, TokenikoAction.REDUCT.value}
    polishable = raw and payload.get("action_token") not in _VERBATIM
    spoken = _run(outbound._voice_out(raw, "uid", "chan") if polishable
                  else outbound._localize(raw, "uid", "chan"))

    assert spoken == "a proposito, l'oro è bello"   # localized…
    assert polished == []                            # …and never handed to the polisher


def test_verbatim_acts_stay_english_in_an_english_room(out_env, monkeypatch):
    # the no-room / English-room case: _localize is a no-op, so behavior is byte-identical to before
    outbound = out_env
    monkeypatch.setattr(outbound, "_room_language", lambda uid, chan: None)
    raw = "by the way, gold is beautiful"
    assert _run(outbound._localize(raw, "uid", "chan")) == raw


# ---- 8. THE NATIVE VOICE (§1 step 2b, 2026-07-26) ------------------------------------------------
# Promoted from the icebox by the Captain's live test: the verdicts were RIGHT and the language was
# WRONG — «I cannot tell; I lack the knowledge» came back in English inside an Italian conversation,
# because a curated FRAGMENT is unsound by construction and the round-trip gate above can only ship
# what it can verify. The answer is not a better verifier: a scaffold is our OWN string, so the
# shelves are CURATED per language and the translator is demoted to the fallback layer. What is
# asserted here is the MACHINERY (the field, the gate, the threading, the carrier no-op) — the
# curated rows themselves are the seed script's, and these fixtures stand in for them.
_IT_IDK = "non lo so"
_EN_IDK = "I cannot tell; I lack the knowledge"


@pytest.fixture()
def native_shelf(_io):
    from lib.core.models import TKScaffoldDoc
    rows = [
        TKScaffoldDoc(category="answer_idk", template=_EN_IDK),
        TKScaffoldDoc(category="answer_idk", template=_IT_IDK, lang="italian"),
        # a SLOTTED category: english-only, exactly as the Captain's v1 fence leaves it — its
        # {retracted} payload is stored English, so the whole reply composes English and travels
        # through the translator like it did yesterday (his consistency ruling).
        TKScaffoldDoc(category="concede_retract", template="I no longer hold that {retracted}",
                      slots=["retracted"]),
    ]
    for row in rows:
        row.insert()
    yield rows
    for row in rows:
        row.delete()


def test_the_italian_shelf_answers_an_italian_room(native_shelf):
    from lib.core.voice import creative_compose_lang
    text, spoken = creative_compose_lang("answer_idk", lang="italian", rng=random.Random(1))
    assert (text, spoken) == (_IT_IDK, "italian")


def test_an_english_room_never_sees_the_italian_row(native_shelf):
    from lib.core.voice import creative_compose_lang
    # every english spelling the ears may hand us, and the unlabelled ask (= today's callers)
    for asked in (None, ENGLISH, "English", "en"):
        picks = {creative_compose_lang("answer_idk", lang=asked, rng=random.Random(seed))
                 for seed in range(20)}
        assert picks == {(_EN_IDK, ENGLISH)}


def test_a_category_with_no_native_row_falls_back_to_the_english_shelf(native_shelf):
    # the Captain's FALLBACK CHAIN: the slotted concede has no italian row, so the italian ask is
    # answered off the english shelf — and it says so, which is what keeps the carrier translating.
    from lib.core.voice import creative_compose_lang
    text, spoken = creative_compose_lang("concede_retract", {"retracted": "«a cat is a dog»"},
                                         lang="italian", rng=random.Random(1))
    assert text == "I no longer hold that «a cat is a dog»"
    assert spoken == ENGLISH


def test_lang_defaults_to_english_so_nothing_migrates(_io):
    # the whole point of the default: a row written before the field — no `lang` key in mongo at
    # all — keeps speaking. It is english, so it answers an english ask AND serves as the italian
    # ask's fallback; no migration, no recompile.
    from lib.core.models import TKScaffoldDoc
    from lib.core.voice import creative_compose_lang
    assert TKScaffoldDoc(category="answer_idk", template="x").lang == ENGLISH
    old = {"category": "answer_idk", "template": "the row from before the field", "slots": [],
           "intensity_band": [0.0, 1.0], "arousal_band": [0.0, 1.0], "weight": 1.0,
           "provenance": "seed", "trusted": 1.0, "enabled": True, "used": 0, "createdAt": 0}
    TKScaffoldDoc.get_motor_collection().insert_one(old)
    try:
        for asked in (None, "italian"):
            assert creative_compose_lang("answer_idk", lang=asked, rng=random.Random(2)) == (
                "the row from before the field", ENGLISH)
    finally:
        TKScaffoldDoc.get_motor_collection().delete_many({"template": old["template"]})


def test_the_never_mute_floor_survives_the_language_gate(_io):
    # an over-narrow gate must degrade to a wider shelf, never to silence: no rows at all (in any
    # language) still speaks the hardwired string — in English, and honestly labelled as such.
    from lib.core.voice import _FALLBACK, creative_compose_lang
    assert creative_compose_lang("answer_idk", lang="italian") == (_FALLBACK["answer_idk"], ENGLISH)


def test_the_blog_shelf_is_never_asked_for_another_language(_io):
    # the public journal's language is fixed (the Captain's ruling): blog.py composes without a
    # `lang`, so an italian blog row — should one ever be seeded — is simply unreachable.
    from lib.core.models import TKScaffoldDoc
    from lib.core.voice import creative_compose
    rows = [TKScaffoldDoc(category="blog_lead_dream", template="While I slept, I untangled something."),
            TKScaffoldDoc(category="blog_lead_dream", template="Mentre dormivo, ho sciolto un nodo.",
                          lang="italian")]
    for row in rows:
        row.insert()
    try:
        picks = {creative_compose("blog_lead_dream", {}, rng=random.Random(seed))
                 for seed in range(20)}
        assert picks == {"While I slept, I untangled something."}
    finally:
        for row in rows:
            row.delete()


# ---- the threading: the room's language reaches the COMPOSER, at plan time ----------------------

@pytest.fixture()
def native_room(_io):
    from lib.core.models import TKExchangeDoc, TKMemoryItemDoc, TKMemoryStakeholdersDoc
    sh = TKMemoryStakeholdersDoc(uid="nativo@lang-test:9", name="nativo", isMe=False,
                                 channel=MEMChannels.DISCORD, trust=0.5,
                                 contextKey="discord:9").save()
    yield sh
    TKMemoryItemDoc.get_motor_collection().delete_many({"sourceId": str(sh.id)})
    TKExchangeDoc.get_motor_collection().delete_many({"user_uid": sh.uid})
    TKMemoryStakeholdersDoc.get_motor_collection().delete_many({"uid": sh.uid})


def _room_item(sh, compile_zip, room_lang):
    # the perceived turn (its metadata carries the channel id = half the room's key) + the room the
    # ears wrote the language into, exactly as /input leaves them.
    from api.main import _room_language_write
    from lib.core.models import TKMemoryItemDoc
    item = TKMemoryItemDoc(
        original="what is a mind?", zip=compile_zip("what is a mind?"), sourceId=str(sh.id),
        channel=MEMChannels.DISCORD, directedness=1.0,
        metadata=json.dumps({"channel_id": "nativo-chan", "message_id": "m-7"}),
    )
    item.insert()
    if room_lang:
        _room_language_write(sh.uid, "nativo-chan", room_lang, str(item.id))
    return item


def _idk_plan(sh, item):
    from brain.behavior import plan_action
    from lib.core.evaluation import AnswerVerdict
    from lib.core.models import TKIdeaDoc
    idea = TKIdeaDoc(trigger=EvalToken.QUESTION.value, action_token=TokenikoAction.ANSWER.value,
                     urge=0.9, target=str(sh.id), source=str(item.id),
                     answer={"verdict": AnswerVerdict.UNKNOWN.value})
    return plan_action(idea, "me")


def test_a_plan_for_an_italian_room_composes_native(native_shelf, native_room, compile_zip):
    # the seam: composition happens at plan time, so the room must be resolved there — and it can
    # be, off the source item's own metadata through io.exchange_channel_key (the one definition).
    plan = _idk_plan(native_room, _room_item(native_room, compile_zip, "italian"))
    assert plan is not None
    assert plan["payload"]["raw"] == _IT_IDK
    assert plan["payload"]["lang"] == "italian"       # what the carrier reads to stay its hand


def test_a_plan_for_an_english_room_is_byte_identical(native_shelf, native_room, compile_zip):
    plan = _idk_plan(native_room, _room_item(native_room, compile_zip, ENGLISH))
    assert plan["payload"]["raw"] == _EN_IDK
    assert plan["payload"]["lang"] == ENGLISH


def test_a_plan_with_no_room_at_all_stays_english(native_shelf, native_room, compile_zip):
    # find_exchange never mints: a pair that never had a room plans exactly as it did yesterday
    from lib.core.models import TKExchangeDoc
    plan = _idk_plan(native_room, _room_item(native_room, compile_zip, None))
    assert plan["payload"]["raw"] == _EN_IDK
    assert TKExchangeDoc.find_one({"user_uid": native_room.uid,
                                   "channel_id": "nativo-chan"}).run() is None


# ---- the carrier: a native reply is neither polished nor translated -----------------------------

def test_the_composed_language_is_read_off_the_payload(out_env):
    outbound = out_env
    assert outbound._composed_lang({"lang": "italian"}) == "italian"
    assert outbound._composed_lang({"lang": ENGLISH}) is None      # english = nothing to stay
    assert outbound._composed_lang({"raw": "yes"}) is None         # an action from before the field
    assert outbound._composed_lang(None) is None


def test_a_native_reply_is_never_translated_again(out_env, monkeypatch):
    # the no-op: zero cloud calls, zero latency, the curated register reaching the person verbatim
    outbound = out_env
    import lib.llc.language as language

    async def never(*args, **kw):
        raise AssertionError("a native reply must never see the translator")

    monkeypatch.setattr(language, "translate_out", never)
    monkeypatch.setattr(outbound, "_room_language",
                        lambda uid, chan: pytest.fail("a native reply needs no room read"))
    assert _run(outbound._localize(_IT_IDK, "uid", "chan", "italian")) == _IT_IDK


def test_an_english_row_in_an_italian_room_still_travels(out_env, monkeypatch):
    # the fallback layer, intact: the categories with no native shelf (every slotted one, v1) keep
    # taking the round trip exactly as they did before this step.
    outbound = out_env
    monkeypatch.setattr(outbound, "_room_language", lambda uid, chan: "italian")
    _stub_translation(monkeypatch, "non lo so", "I do not know")
    monkeypatch.setattr(outbound, "_verify_voice", lambda raw, back: {"ok": True, "note": "verified"})
    assert _run(outbound._localize("I do not know", "uid", "chan", None)) == "non lo so"


def test_a_native_reply_is_never_polished(out_env, monkeypatch):
    # rag2-out's prompt AND the zip-verifier behind it are both English — there is nothing that
    # could judge «non lo so», and the row is curated text already.
    outbound = out_env
    polished = []

    async def fake_polish(raw, subject_uid=None):
        polished.append(raw)
        return "polished away"

    monkeypatch.setattr(outbound, "_polish", fake_polish)
    # the gating expression exactly as deliver_one computes it (the test_voice_out precedent)
    payload = {"action_token": TokenikoAction.ANSWER.value, "raw": _IT_IDK, "lang": "italian"}
    raw = payload["raw"]
    _VERBATIM = {TokenikoAction.MENTION.value, TokenikoAction.REDUCT.value}
    native = outbound._composed_lang(payload)
    polishable = raw and payload.get("action_token") not in _VERBATIM and native is None
    spoken = _run(outbound._voice_out(raw, "uid", "chan", native) if polishable
                  else outbound._localize(raw, "uid", "chan", native))
    assert spoken == _IT_IDK and polished == []


def test_the_native_reply_reaches_the_socket_whole(_io, out_env, monkeypatch):
    # end to end through the real carrier: a native action ships its curated Italian verbatim, with
    # no polish call and no translation call anywhere in between.
    from lib.core.memory import ActionStatus, ActionType
    from lib.core.models import TKActionDoc
    import lib.llc.language as language
    outbound = out_env
    monkeypatch.setenv("SENSES_DELIVER_DRYRUN", "0")

    async def never(*args, **kw):
        raise AssertionError("a native reply must never reach the cloud")

    monkeypatch.setattr(language, "translate_out", never)
    monkeypatch.setattr(outbound, "rag_call", never)
    action = TKActionDoc(
        action_type=ActionType.SEND_MESSAGE, sourceId="tokeniko-uid", targetId="nativo@lang-test:9",
        channel=MEMChannels.DISCORD,
        payload={"action_token": TokenikoAction.ANSWER.value, "raw": _IT_IDK, "lang": "italian",
                 "destination": {"channel_id": "nativo-chan", "reply_to": "m-7"}},
    ).insert()
    sent = []

    async def sender(dest, content):
        sent.append((dest, content))
        return "msg-777"

    try:
        # drain until OUR action is handled (the queue is oldest-first and shared with the sandbox)
        for _ in range(5):
            if TKActionDoc.get(action.id).run().status != ActionStatus.PENDING:
                break
            _run(outbound.deliver_one(sender))
        assert TKActionDoc.get(action.id).run().status == ActionStatus.DONE
        assert (_IT_IDK, "nativo-chan") in [(text, dest.channel_id) for dest, text in sent]
    finally:
        TKActionDoc.get_motor_collection().delete_many({"_id": action.id})
        from lib.core.models import TKMemoryItemDoc
        TKMemoryItemDoc.get_motor_collection().delete_many({"targetId": "nativo@lang-test:9"})
