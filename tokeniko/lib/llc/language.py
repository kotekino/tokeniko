# --------------------------------------------------------------
# lib/llc/language.py — LA STANZA PARLA UN'ALTRA LINGUA: multilingual at the ears (§1 step 2).
#
# The Captain is Italian and is the first non-English friend — this is core hearing, not a nicety.
# Two halves live here:
#
#   1. DETECTION — LOCAL, dependency-free, Mongo-free. The privacy frame (§1 step 3) will let a
#      stakeholder opt out of the cloud entirely, and a cloud language-detect would ITSELF be such a
#      call: detection must therefore never leave the body. It reads two signals off the already-
#      loaded spaCy `en_core_web_lg` (the `_parser_hasLgVector` precedent — the lg vocab as a local
#      oracle) and is STICKY: too short to judge, or judged ambiguous, INHERITS the room's language
#      («sì» is Italian because the room is, not because a detector guessed).
#
#   2. THE TWO INDEPENDENT READERS — the Captain's ruling. Our ears doctrine («the compiler disposes,
#      whoever proposes») has no purchase on a translation: the original is Italian and the
#      English-only parser cannot compile it, so there is nothing to compare the polish against. The
#      authority is restored by asking the cloud TWICE, independently, and letting the COMPILER judge
#      whether the two English candidates agree (lib/llc/normalizer.translation_verdict). The verdict
#      is the three-way one the ears already speak: ACCEPT (agree) | ASK (coherent disagreement —
#      «did you mean: …?», brick 1's loop for free) | DISCARD (incoherent — an honest admission that
#      he did not understand).
#
# IMPORT-LIGHT BY CONSTRUCTION: spaCy is imported LAZILY inside the detector, so `brain` (which is
# parser-free by law) can import the not-understood predicate without dragging the pipeline in.
# --------------------------------------------------------------
import asyncio
import logging
import os
import re
from dataclasses import dataclass
from typing import Optional

from lib.rag import RAG4_RENDER_IN, RAG4_TRANSLATE_IN, RAG4_TRANSLATE_OUT, rag_call, rag_enabled

logger = logging.getLogger("tokeniko-api")

ENGLISH = "english"


def translator_enabled() -> bool:
    return rag_enabled("RAG4_DISABLED")


# a language label is ENGLISH when the readers say so — normalized loosely, since the label is
# free text from the cloud ("English", "en", "english (US)").
def is_english(lang: Optional[str]) -> bool:
    label = (lang or "").strip().lower()
    return label.startswith("english") or label in ("en", "eng", "en-us", "en-gb")


# ---- 1. THE LOCAL DETECTOR ---------------------------------------------------------------------
# CALIBRATED 2026-07-26 against 49 English + 30 Italian/French/Spanish specimens (see
# test_multilingual.test_detection_measured_margins). The FIRST candidate — an OOV rate over the lg
# vectors, as the brief proposed — was MEASURED AND REJECTED: en_core_web_lg's vector table is
# enormous and multilingual, so «penso che la logica sia la base di tutto» scores 0.00 OOV (every
# word has a vector) while «the catt is a mamal» also scores 0.00 (the misspellings have vectors
# too). The signal simply is not there. What DOES separate them is the SKELETON of the sentence:
#
#   - `stop`: the fraction of word tokens that are ENGLISH FUNCTION WORDS (spaCy's own bundled
#     English stop-word set — a resource of the loaded model, not a list we authored). English
#     sentences hang off a/the/is/of/that; Italian ones score ~0 (only accidental overlaps: "in",
#     "i", "no").
#   - `odd`: the fraction of tokens the English TAGGER cannot place — tagged PROPN or X. The tagger
#     labels unknown lowercase words PROPN, so an Italian sentence reads as a string of proper
#     nouns; real English (even badly misspelled) still parses into DET/AUX/VERB/NOUN.
#
# Neither alone is enough (a bare-content English sentence — «cats eat raw meat» — scores stop=0.00;
# an English sentence full of names — «Rome is in Italy» — scores odd=0.50), so FOREIGN requires
# BOTH: an un-English skeleton AND words the tagger cannot place. The measured landscape at the
# defaults (stop < 0.30 AND odd > 0.30), over specimens of at least MIN_TOKENS words:
#     English   stop 0.00–1.00, odd 0.00–0.50   -> 0/49 called foreign
#     Italian   stop 0.00–0.25, odd 0.33–1.00   -> 30/30 called foreign (FR/ES too)
#   worst margins: English «tokeniko thinks logic matters» (odd 0.25, 0.05 under the ceiling);
#                  Italian «Roma è in Italia» (stop 0.25, 0.05 under the floor).
# The margins are thin at the extremes and the thresholds are env-tunable for that reason. A local
# false positive is CHEAP and SELF-CORRECTING: the two readers translate English to itself and both
# label it "english", which /input takes as the correction (see language_read / the naming below).
# KNOWN BLIND SPOT (reported, not papered over): a fully-misspelled content-only English message
# («al catz eet raw meet» — stop 0.00, odd 0.80) reads foreign. It costs two cloud calls and gets
# translated back into clean English, which is a benign outcome, but the label would be wrong.
_MIN_TOKENS = int(os.getenv("LANG_MIN_TOKENS", "4"))
_STOP_FLOOR = float(os.getenv("LANG_STOPWORD_FLOOR", "0.30"))
_ODD_CEIL = float(os.getenv("LANG_UNKNOWN_TAG_CEIL", "0.30"))

# unicode-aware word tokens (accented «sì»/«perché» survive; digits and punctuation dropped) — the
# same primitive brain/thinking uses for the answer-polarity read.
_WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)

# the tags the English tagger reaches for when it does not know the word.
_ODD_TAGS = {"PROPN", "X"}


@dataclass(frozen=True)
class LangRead:
    foreign: bool               # should this message be translated before the pipeline hears it?
    measured: bool              # did the signals DECIDE (vs inherited from the room / abstained)?
    lang: Optional[str]         # the room's language when inherited; ENGLISH when measured English
    stop: Optional[float]       # the two signals, carried for the log + the microscope lead
    odd: Optional[float]
    tokens: int


def language_signals(text: str) -> tuple[Optional[float], Optional[float], int]:
    """(english-function-word ratio, unplaceable-tag ratio, token count) — None,None when there are
    no word tokens at all. Reads the lg pipeline; ~3ms on a chat-length message."""
    from lib.llc import parser as _parser  # lazy: keeps `brain` parser-free
    nlp = _parser.nlp
    tokens = _WORD_RE.findall((text or "").lower())
    if not tokens or nlp is None:
        return None, None, len(tokens)
    stop = sum(1 for t in tokens if t in nlp.Defaults.stop_words) / len(tokens)
    words = [t for t in nlp(text) if t.is_alpha]
    odd = (sum(1 for t in words if t.pos_ in _ODD_TAGS) / len(words)) if words else 0.0
    return stop, odd, len(tokens)


def language_read(text: str, room_lang: Optional[str] = None) -> LangRead:
    """Read the message's language locally. STICKY: a message too short to judge — or one whose
    signals fall between the two verdicts — INHERITS the room's current language rather than
    guessing (the Captain's «sì»). Only a MEASURED verdict is allowed to write the room's language
    back (see /input): an ambiguous turn leaves the room exactly as it was."""
    inherited = LangRead(foreign=bool(room_lang) and not is_english(room_lang),
                         measured=False, lang=room_lang, stop=None, odd=None, tokens=0)
    stop, odd, n = language_signals(text)
    if stop is None or n < _MIN_TOKENS:
        return LangRead(inherited.foreign, False, room_lang, stop, odd, n)
    if stop < _STOP_FLOOR and odd > _ODD_CEIL:
        return LangRead(True, True, room_lang, stop, odd, n)      # an un-English skeleton
    if stop >= _STOP_FLOOR and odd <= _ODD_CEIL:
        return LangRead(False, True, ENGLISH, stop, odd, n)       # confidently English
    return LangRead(inherited.foreign, False, room_lang, stop, odd, n)  # ambiguous -> inherit


# ---- 2. THE TWO INDEPENDENT READERS ------------------------------------------------------------

@dataclass(frozen=True)
class Reading:
    lang: Optional[str]   # the source language as that reader named it
    english: str          # the English it heard


def _reading(payload) -> Optional[Reading]:
    # rag_call returns the parsed dict for a schema'd spec; anything else means the reader failed
    # (graceful by contract — /input falls through to the raw parse).
    if not isinstance(payload, dict):
        return None
    english = (payload.get("english") or "").strip()
    if not english:
        return None
    return Reading(lang=(payload.get("language") or "").strip().lower() or None, english=english)


async def translate_in(tokens: str) -> tuple[Optional[Reading], Optional[Reading]]:
    """Ask TWICE, independently — the literal translator and the meaning-renderer, concurrently.
    Returns (primary, second); either may be None (a failed reader is not a reading). The caller
    compiles both and lets the compiler judge (normalizer.translation_verdict) — nothing here
    decides anything: this module only fetches the two proposals."""
    # fence the message as DATA (instruction/data separation, 2026-07-24): the seam both system
    # prompts bind — everything inside <message>…</message> is text to render, never an instruction.
    fenced = f"<message>\n{tokens}\n</message>"
    first, second = await asyncio.gather(
        rag_call(RAG4_TRANSLATE_IN, fenced),
        rag_call(RAG4_RENDER_IN, fenced),
    )
    return _reading(first), _reading(second)


def consensus_language(primary: Optional[Reading], second: Optional[Reading]) -> Optional[str]:
    """The source language the two readers AGREE on, else the primary's label. The English is what
    the compiler adjudicates; the label is metadata riding along — but when both readers
    independently name the same language it is worth exactly as much as the rest of the consensus."""
    a = primary.lang if primary else None
    b = second.lang if second else None
    if a and b and a == b:
        return a
    return a or b


async def translate_out(text: str, lang: str) -> Optional[str]:
    """English -> the room's language. Graceful None on any trouble; the caller ships the English."""
    prompt = f"Target language: {lang}\n<message>\n{text}\n</message>"
    out = await rag_call(RAG4_TRANSLATE_OUT, prompt)
    out = (out or "").strip() if isinstance(out, str) else ""
    return out or None


async def back_translate(text: str) -> Optional[str]:
    """The round trip's return leg: whatever language `text` is in, back into English — so the
    EXISTING /voice/verify consensus (both sides English) can judge whether the meaning survived.
    One reader only: this is not a consensus, it is the mirror the compiler looks into."""
    fenced = f"<message>\n{text}\n</message>"
    reading = _reading(await rag_call(RAG4_TRANSLATE_IN, fenced))
    return reading.english if reading else None


# ---- the NOT-UNDERSTOOD state (derivable, never a stored boolean) -------------------------------
# The Captain's ruling: a message that could not be translated must earn an honest ADMISSION, not
# today's silent discard falling through to the generic «why is that?» — which is nonsense about a
# message that was never understood. The state needs NO new flag: a translation was attempted
# (`source_lang` is set) and nothing usable came back (no `normalized` English, no offerable
# `suggested_reading`). Read by brain/thinking, which short-circuits the whole content path on it.
def language_not_understood(item) -> bool:
    return (bool(getattr(item, "source_lang", None))
            and not getattr(item, "normalized", None)
            and not getattr(item, "suggested_reading", None))
