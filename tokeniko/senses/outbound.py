# --------------------------------------------------------------
# senses/outbound.py — the OUTBOUND actions executor (#4 D3b). The carrier half of the brain→senses
# reply seam: the brain DECIDES (mints an Action with channel=discord, a target, and the composed
# text in the payload); senses CARRIES it to the socket — through the rag2-out voice gate (compose
# 2.0 slice 3): a long-enough composed reply gets ONE Haiku fluency pass, shipped ONLY if the
# API's zip-verifier proves the polish still compiles to the raw's meaning (consensus-with-the-
# compiler on the way out, mirroring rag1-in). ANY failure anywhere ships the raw verbatim.
#
# OWNERSHIP (no cross-process race, no new status): the brain's `actions_phase` consumes only
# channel=INTERNAL; this executor consumes only channel=discord. Disjoint filters over the SAME queue.
#
# MULTILINGUAL (§1 step 2): after the polish, the reply is spoken in the ROOM's language — the
# (soul, channel) exchange carries it, written at the ears where the message was heard. The gate is
# a ROUND TRIP through the SAME /voice/verify seam (back-translate, then compare English to
# English): no new verification machinery, and an unverified trip ships the English.
# THE NATIVE VOICE (§1 step 2b) demoted that round trip to the FALLBACK layer: the brain now
# composes off a per-language scaffold shelf and stamps the language on the payload, so a reply that
# is already native arrives here needing neither polish nor translation — this carrier's whole
# cloud path becomes a no-op for it. An English raw is untouched: everything below is as it was.
#
# DRY-RUN by default (`SENSES_DELIVER_DRYRUN`!=0): resolve + decompile + LOG the would-send, mark DONE,
# touch no socket — so the whole seam is verifiable without Discord credentials / risking live spam.
# Flip to live (and pass a real `sender`) once the inbound listener + a connected DiscordClient land.
# pipeline-light: never imports the parser (the verify consensus runs at the API — the one-compile
# seam); the ONLY cloud call is the rag2-out polish, gated + graceful (RAG2_OUT_DISABLED kills it).
# --------------------------------------------------------------
import asyncio
import json
import logging
import os
from typing import Awaitable, Callable, Optional

from lib.core.models import TKActionDoc, TKMemoryItemDoc, TKMemoryStakeholdersDoc
from lib.core.memory import ActionStatus, MEMChannels, TokenikoAction
from lib.discord.models import Destination
from lib.rag import RAG2_OUT, rag_call, rag_enabled
from senses.voicegate import _verify_voice  # the shared /voice/verify seam (blog.py uses it too)

logger = logging.getLogger("tokeniko-brain")

# below this length a reply is template-curated and fragment-shaped ("yes", "why is that?") —
# unpolishable by the verifier's own gate, so the Haiku call is never spent on it.
_POLISH_MIN_CHARS = int(os.getenv("SENSES_VOICE_POLISH_MIN_CHARS", "25"))


# ---- the rag2-out voice gate (compose 2.0 slice 3) ---------------------------------------------------
# polish + verify one composed reply; returns the text to ship (the polish ONLY when the compiler
# consensus holds — every other path is the raw, verbatim). Never raises.
async def _polish(raw: str) -> str:
    if not rag_enabled("RAG2_OUT_DISABLED") or len(raw) < _POLISH_MIN_CHARS:
        return raw
    polished = await rag_call(RAG2_OUT, raw)
    polished = (polished or "").strip()
    if not polished or polished == raw:
        return raw
    verdict = await asyncio.to_thread(_verify_voice, raw, polished)
    if verdict and verdict.get("ok"):
        logger.info("[outbound] rag2-out verified: %r -> %r", raw, polished)
        return polished
    logger.info("[outbound] rag2-out REJECTED (%s) — raw ships: %r",
                (verdict or {}).get("note", "unverifiable"), raw)
    return raw


# ---- the room's LANGUAGE, on the way out (multilingual §1 step 2) -----------------------------------
# He answers in the language he was spoken to: the (soul, channel) room carries `lang` (written at
# the ears, where the message was heard), and the composed — already polished — English reply is
# translated into it before it hits the socket. The gate is a ROUND TRIP, and it reuses the EXISTING
# machinery rather than inventing a second verifier: translate EN->target, back-translate ->EN, and
# hand the back-translation to the /voice/verify seam. Both sides of THAT comparison are English, so
# it is the rag2-out contract verbatim — the compiler proving the meaning came home.
#   - identical round trip -> ship (a lossless trip needs no judge; and it is the ONLY gate a
#     FRAGMENT can pass — «yes»/«why is that?» are unverifiable by construction, and a mind that
#     could not say «sì» would be speaking English half the time);
#   - verified round trip   -> ship the translation;
#   - anything else         -> ship the English, exactly like a rejected polish. Graceful at every
#     step: no room, no language, no key, a dead API — the English ships and nothing breaks.
def _room_language(target_uid: Optional[str], channel_id: Optional[str]) -> Optional[str]:
    if not target_uid or not channel_id:
        return None
    try:
        from lib.core.io import find_exchange
        from lib.core.trust import resolve_canonical
        from lib.llc.language import is_english
        soul = resolve_canonical(target_uid)
        if soul is None or not soul.uid:
            return None
        room = find_exchange(soul.uid, str(channel_id))
        lang = getattr(room, "lang", None)
        return None if (not lang or is_english(lang)) else lang
    except Exception as error:
        logger.warning("[outbound] room language unreadable (%s) — english ships", error)
        return None


def _same_words(a: str, b: str) -> bool:
    keep = "".join(c for c in (a or "").lower() if c.isalnum() or c.isspace())
    other = "".join(c for c in (b or "").lower() if c.isalnum() or c.isspace())
    return keep.split() == other.split()


# the language the BRAIN composed the reply in (the plan stamps it on the payload, §1 step 2b) —
# None when it is English, when the action predates the field, or when the label is unreadable, and
# None is exactly today's behavior. A non-None answer means the text is ALREADY native: it must not
# be translated (there is nothing to translate it from — it is not English) and must not be polished
# (rag2-out and its verifier both speak English).
def _composed_lang(payload: Optional[dict]) -> Optional[str]:
    try:
        from lib.llc.language import is_english
        lang = (payload or {}).get("lang")
        return None if (not lang or is_english(lang)) else str(lang)
    except Exception:
        return None


async def _localize(english: str, target_uid: Optional[str], channel_id: Optional[str],
                    native: Optional[str] = None) -> str:
    from lib.llc.language import back_translate, translate_out, translator_enabled
    if native:
        # the NO-OP (§1 step 2b): the scaffold shelf already spoke this room's language, so the
        # round trip has nothing to do — zero cloud calls, zero latency, and the curated native
        # register reaches the person exactly as it was written.
        logger.info("[outbound] composed native (%s) — no round trip: %r", native, english)
        return english
    if not english or not target_uid or not channel_id or not translator_enabled():
        return english
    lang = await asyncio.to_thread(_room_language, target_uid, channel_id)
    if lang is None:
        return english
    translated = await translate_out(english, lang)
    if not translated or translated == english:
        return english
    back = await back_translate(translated)
    if not back:
        logger.info("[outbound] rag4-out round trip broke (no back-translation) — english ships: %r",
                    english)
        return english
    if _same_words(english, back):
        logger.info("[outbound] rag4-out %s (round trip lossless): %r -> %r", lang, english, translated)
        return translated
    verdict = await asyncio.to_thread(_verify_voice, english, back)
    if verdict and verdict.get("ok"):
        logger.info("[outbound] rag4-out %s verified: %r -> %r", lang, english, translated)
        return translated
    logger.info("[outbound] rag4-out %s REJECTED (%s) — english ships: %r",
                lang, (verdict or {}).get("note", "unverifiable"), english)
    return english


# the carrier's ONE voice seam: polish (unchanged), then speak the room's language. `target_uid` /
# `channel_id` are the room's key; without them (tests, an unaddressable action) the English ships
# and the behavior is byte-identical to before the multilingual step.
async def _voice_out(raw: str, target_uid: Optional[str] = None,
                     channel_id: Optional[str] = None, native: Optional[str] = None) -> str:
    return await _localize(await _polish(raw), target_uid, channel_id, native)

# tokeniko's own stakeholder id (the sourceId of his recorded speech), resolved lazily once.
_self_id: Optional[str] = None


def _tokeniko_id() -> Optional[str]:
    global _self_id
    if _self_id is None:
        me = TKMemoryStakeholdersDoc.find_one({"isMe": True}).run()  # Bunnet: .run() executes
        _self_id = str(me.id) if me is not None else None
    return _self_id


# SELF-SPEECH → MEMORY (senses B1, 2026-07-09): a DELIVERED outbound message is a biographical event —
# record it as a zip-less memory item (sourceId=tokeniko, targetId=the recipient). zip=None keeps it
# INVISIBLE to the reaction loop (think/wonder filter zip!=None) while making conversational context
# DERIVABLE from the timeseries (the open-why: "did I recently ask this speaker something?"). metadata
# carries the SENT message id (the structural hook an inbound reply threads back to) + what it replied
# to. Live sends only — a dry-run says nothing, so it records nothing.
def _record_self_speech(action, dest: Destination, text: str, sent_message_id: str) -> None:
    try:
        me = _tokeniko_id()
        if me is None:
            return
        TKMemoryItemDoc(
            original=text,
            zip=None,
            sourceId=me,
            targetId=action.targetId,
            channel=MEMChannels.DISCORD,
            metadata=json.dumps({
                "channel_id": dest.channel_id or "",
                "message_id": sent_message_id,
                "reply_to": dest.reply_to,
            }),
        ).insert()
    except Exception as error:
        logger.warning("[outbound] self-speech record failed (%s) — delivery unaffected", error)

POLL_INTERVAL = float(os.getenv("SENSES_OUTBOUND_POLL", "2"))   # seconds between idle polls


# the delivery flags are read LAZILY (call time, not import time): senses/main.py imports this module
# BEFORE load_dotenv() runs, so a module-level read sees a bare environment and silently stays in
# dry-run whatever .env says (bit us at go-live, 2026-07-09). Lazy also means the flag is honored
# without touching code.
def _dryrun() -> bool:
    return os.getenv("SENSES_DELIVER_DRYRUN", "1") != "0"        # default: dry-run (no live send)


# the senders the executor can be handed (None in dry-run). channel adapter -> (Destination, text) -> id.
Sender = Callable[[Destination, str], Awaitable[str]]


# resolve the action's recipient to a Discord Destination, or None if unaddressable.
#   1. explicit per-message coords in payload["destination"] — the FORWARD path: the (deferred) inbound
#      listener stamps the origin channel_id / reply_to message_id here for an in-channel threaded reply.
#   2. fallback: DM the participant via the discord id carried in the stakeholder's contextKey
#      ("channel:talker_uid") — enough to prove the seam before inbound exists.
def _resolve_destination(target_uid: Optional[str], payload: dict) -> Optional[Destination]:
    dest = payload.get("destination")
    if isinstance(dest, dict):
        try:
            return Destination(**dest)
        except Exception:
            return None
    if not target_uid:
        return None
    sh = TKMemoryStakeholdersDoc.find_one({"uid": target_uid}).run()  # Bunnet: .run() executes
    if sh is None or not sh.contextKey or ":" not in sh.contextKey:
        return None
    platform_id = sh.contextKey.split(":", 1)[1]
    if not platform_id:
        return None
    try:
        return Destination(user_id=platform_id)
    except Exception:
        return None


# deliver ONE pending discord action (oldest-first). grab (PENDING->PROCESSING) before any await so a
# crash mid-delivery doesn't leave it re-grabbable as PENDING. Returns True iff it handled one.
async def deliver_one(sender: Optional[Sender] = None) -> bool:
    pending = (
        TKActionDoc.find(
            {"status": ActionStatus.PENDING.value, "channel": MEMChannels.DISCORD.value}
        )
        .sort("createdAt")
        .limit(1)
        .to_list()
    )
    if not pending:
        return False
    action = pending[0]
    action.status = ActionStatus.PROCESSING
    action.save()

    payload = action.payload or {}
    raw = (payload.get("raw") or "").strip()
    # the rag2-out voice gate (compose 2.0 slice 3): one verified fluency pass, or the raw
    # verbatim — the voice can gain fluency, never lose meaning. The ANECDOTE skips the polish
    # (premiere find, 2026-07-17): its side-note register («by the way, …») is discourse framing
    # the zip cannot see — Haiku stripped it and the verifier CORRECTLY passed the result
    # («Gold is beautiful.»): meaning preserved, charm lost. For a side-note the register IS the
    # point, and the scaffold text is already curated English — ship it verbatim.
    # The REDUCT skips it too (roadmap §0 slice 1): the quoted premises MUST reach the teacher
    # verbatim — they can only answer «which is false?» if they recognize their own taught
    # sentence — and the «a» or «b» structure is the r.a.a. itself; a polish that rewords either
    # corrupts the question. The scaffold text is already curated English — ship it verbatim.
    # A NATIVE reply (composed off a non-English scaffold shelf, §1 step 2b) skips the polish for a
    # third, harder reason than register: rag2-out's prompt and the zip-verifier behind it are both
    # English, so there is nothing here that could judge «non lo so» — and the row is curated text
    # already. It skips the translation too (see _localize): it is not English to translate FROM.
    _VERBATIM = {TokenikoAction.MENTION.value, TokenikoAction.REDUCT.value}
    native = _composed_lang(payload)
    polishable = raw and payload.get("action_token") not in _VERBATIM and native is None
    # the destination is resolved FIRST now: its channel id is half the room's key, and the room is
    # what says which language to speak (§1 step 2). VERBATIM means UNPOLISHED, NOT UNTRANSLATED
    # (the author's ruling, 2026-07-26): a side-note or a reductio still reaches the person in the
    # language of their room — a reply in Italian carrying an English aside is not one voice. The
    # register argument above is about the POLISHER (which strips discourse framing and rewords a
    # quoted premise); localization is round-trip verified, so meaning comes home either way. For a
    # non-English teacher it is in fact the FAITHFUL choice: their words were translated INTO English
    # at the ears, so quoting the premise back in their own tongue lands nearer what they actually
    # said. An English room is untouched — _localize is a no-op without a room language.
    dest = _resolve_destination(action.targetId, payload)
    channel_id = getattr(dest, "channel_id", None)
    spoken = (await _voice_out(raw, action.targetId, channel_id, native) if polishable
              else await _localize(raw, action.targetId, channel_id, native))

    if dest is None or not spoken:
        logger.warning(
            "[outbound] action %s undeliverable (dest=%s, spoken=%r) -> FAILED",
            str(action.id), dest, spoken,
        )
        action.status = ActionStatus.FAILED
        action.save()
        return True

    if _dryrun() or sender is None:
        logger.info("[outbound] DRY-RUN would send to %s: %r  (raw=%r)",
                    dest, spoken, payload.get("raw", ""))
        action.status = ActionStatus.DONE
        action.save()
        return True

    try:
        msg_id = await sender(dest, spoken)
        logger.info("[outbound] sent to %s (msg=%s): %r", dest, msg_id, spoken)
        _record_self_speech(action, dest, spoken, msg_id)  # B1: spoken words are biography
        action.status = ActionStatus.DONE
    except Exception as error:
        logger.warning("[outbound] send failed for action %s (%s) -> FAILED", str(action.id), error)
        action.status = ActionStatus.FAILED
    action.save()
    return True


# the executor loop (a cancellable while-loop, mirroring the other senses tasks). Drains back-to-back
# while there is work, then idles at POLL_INTERVAL.
async def outbound_executor_task(sender: Optional[Sender] = None) -> None:
    logger.info("📤 Outbound executor started (dry-run=%s)", _dryrun())
    try:
        while True:
            try:
                did = await deliver_one(sender)
            except Exception as error:
                logger.error("[outbound] executor error: %s", error)
                did = False
            await asyncio.sleep(0 if did else POLL_INTERVAL)
    except asyncio.CancelledError:
        logger.info("📤 Outbound executor interrupted...")
