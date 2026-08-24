# ------------------------------------------------------------------------------------------------
# THE CONVERSATIONAL-CONTEXT ROOM + THE "DID YOU MEAN?" ASK — the room + ask (1a, 2026-07-25).
#
# The author's design, mechanized and asserted: a per-(user, channel) REFERENCE room (light state +
# timeseries-id references, no content duplication), the reply_tempo EMA (outlier-capped, seeded from
# a default), and the ASK reaction (open a pending + spawn the eval:did_you_mean -> tokeniko:ask idea,
# directedness-gated). asking ≠ believing — the yes/no/restate RESOLUTION is 1b (out of scope here).
# ------------------------------------------------------------------------------------------------
import json
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from lib.core.memory import EvalToken, MEMChannels, TokenikoAction


# ---- the room: create / fetch / upsert ------------------------------------------------------------

def test_room_create_fetch_upsert(_io):
    # get_exchange fetch-or-creates against the UNIQUE (user_uid, channel_id) compound key: a first
    # call mints the room, a second returns the SAME doc (never a duplicate), and a different pair is
    # a different room.
    from lib.core.io import get_exchange
    from lib.core.models import TKExchangeDoc
    uids = []
    try:
        a1 = get_exchange("soul@room-test:1", "chan-A")
        a2 = get_exchange("soul@room-test:1", "chan-A")
        assert a1.id == a2.id                              # same pair -> same room (upsert, no dup)
        assert a1.reply_tempo == 180.0                     # the seed (EXCHANGE_TEMPO_DEFAULT_S)
        assert a1.pending == []
        b = get_exchange("soul@room-test:1", "chan-B")     # same user, other channel -> other room
        assert b.id != a1.id
        c = get_exchange("soul@room-test:2", "chan-A")     # other user, same channel -> other room
        assert c.id != a1.id
        # exactly one room per pair
        assert TKExchangeDoc.find(
            {"user_uid": "soul@room-test:1", "channel_id": "chan-A"}).to_list().__len__() == 1
    finally:
        TKExchangeDoc.get_motor_collection().delete_many(
            {"user_uid": {"$in": ["soul@room-test:1", "soul@room-test:2"]}})


# ---- the reply_tempo EMA --------------------------------------------------------------------------

@pytest.fixture()
def tempo_speaker(_io):
    from lib.core.models import TKExchangeDoc, TKMemoryStakeholdersDoc
    sh = TKMemoryStakeholdersDoc(uid="tempo@room-test:9", name="tempo", isMe=False,
                                 channel=MEMChannels.DISCORD, trust=0.5).save()
    yield sh
    TKExchangeDoc.get_motor_collection().delete_many({"user_uid": sh.uid})
    TKMemoryStakeholdersDoc.get_motor_collection().delete_many({"uid": sh.uid})


def _turn(sh_id, dt, channel_id="tempo-chan"):
    # a lightweight processed turn — _update_tempo reads only sourceId / timestamp / channel key
    return SimpleNamespace(sourceId=sh_id, timestamp=dt,
                           metadata=json.dumps({"channel_id": channel_id}), channel=None)


def test_tempo_first_contact_seeds_default(tempo_speaker):
    from brain.thinking import _update_tempo
    from lib.core.io import get_exchange
    t0 = datetime.now(timezone.utc)
    _update_tempo(_turn(str(tempo_speaker.id), t0))
    room = get_exchange(tempo_speaker.uid, "tempo-chan")
    assert room.reply_tempo == 180.0                       # first contact -> the default stands (no sample)
    assert room.last_turn_at == int(t0.timestamp())        # the turn stamp is recorded for the next gap


def test_tempo_ema_folds_a_sample(tempo_speaker):
    # α·sample + (1-α)·tempo — a 30s gap after the seed pulls tempo toward 30: 0.3·30 + 0.7·180 = 135
    from brain.thinking import _update_tempo, EXCHANGE_TEMPO_ALPHA
    from lib.core.io import get_exchange
    t0 = datetime.now(timezone.utc)
    _update_tempo(_turn(str(tempo_speaker.id), t0))
    _update_tempo(_turn(str(tempo_speaker.id), datetime.fromtimestamp(t0.timestamp() + 30, timezone.utc)))
    room = get_exchange(tempo_speaker.uid, "tempo-chan")
    expected = EXCHANGE_TEMPO_ALPHA * 30 + (1 - EXCHANGE_TEMPO_ALPHA) * 180.0
    assert room.reply_tempo == pytest.approx(expected)     # ~135
    assert room.last_turn_at == int(t0.timestamp()) + 30


def test_tempo_ignores_over_ceiling_gap(tempo_speaker):
    # an at-work / overnight silence (a gap above EXCHANGE_GAP_CEIL) is NOT conversational rhythm —
    # dropped from the EMA (tempo unchanged) but last_turn_at still advances (next gap from the real
    # last turn, not a stale one).
    from brain.thinking import _update_tempo, EXCHANGE_GAP_CEIL
    from lib.core.io import get_exchange
    t0 = datetime.now(timezone.utc)
    _update_tempo(_turn(str(tempo_speaker.id), t0))
    later = t0.timestamp() + EXCHANGE_GAP_CEIL + 500       # well past the ceiling
    _update_tempo(_turn(str(tempo_speaker.id), datetime.fromtimestamp(later, timezone.utc)))
    room = get_exchange(tempo_speaker.uid, "tempo-chan")
    assert room.reply_tempo == 180.0                       # the outlier never poisoned the EMA
    assert room.last_turn_at == int(later)                 # but the clock moved forward


def test_tempo_self_turns_never_move_it(_io):
    # the rhythm is the HUMAN's cadence — tokeniko's own turns no-op (no room, no write)
    from brain.thinking import _update_tempo
    from lib.core.io import get_tokeniko
    me = get_tokeniko()
    _update_tempo(_turn(str(me.id), datetime.now(timezone.utc)))  # must not raise, must not mint a room
    from lib.core.models import TKExchangeDoc
    assert TKExchangeDoc.find_one({"user_uid": me.uid}).run() is None


# ---- the "did you mean?" ASK reaction -------------------------------------------------------------

@pytest.fixture()
def dym_world(_io):
    from lib.core.models import (TKBehaviorRuleDoc, TKExchangeDoc, TKIdeaDoc,
                                 TKMemoryItemDoc, TKMemoryStakeholdersDoc)
    # BOTH rules seeded: the did-you-mean ask AND the generic unknown-why — so a working dym path is
    # PROVEN to route the ask and SUPPRESS the why for the same item (they would otherwise co-fire).
    rules = [
        TKBehaviorRuleDoc(trigger=EvalToken.DID_YOU_MEAN.value,
                          action=TokenikoAction.ASK.value, urge=0.7),
        TKBehaviorRuleDoc(trigger=EvalToken.UNKNOWN.value,
                          action=TokenikoAction.WHY.value, urge=0.6),
    ]
    for r in rules:
        r.insert()
    sh = TKMemoryStakeholdersDoc(uid="asker@room-test:7", name="asker", isMe=False,
                                 channel=MEMChannels.DISCORD, trust=0.5).save()
    yield {"speaker": sh}
    triggers = [EvalToken.DID_YOU_MEAN.value, EvalToken.UNKNOWN.value]
    TKBehaviorRuleDoc.get_motor_collection().delete_many({"trigger": {"$in": triggers}})
    TKIdeaDoc.get_motor_collection().delete_many({"trigger": {"$in": triggers}})
    TKMemoryItemDoc.get_motor_collection().delete_many({"sourceId": str(sh.id)})
    TKExchangeDoc.get_motor_collection().delete_many({"user_uid": sh.uid})
    TKMemoryStakeholdersDoc.get_motor_collection().delete_many({"uid": sh.uid})


def _dym_item(speaker_id, reading="the cat is on the bed"):
    from lib.core.models import TKMemoryItemDoc
    item = TKMemoryItemDoc(
        original="the cat is on the mat", zip=None, sourceId=speaker_id,
        channel=MEMChannels.DISCORD, directedness=1.0, suggested_reading=reading,
        metadata=json.dumps({"channel_id": "dym-chan", "message_id": "m-9"}),
    )
    item.insert()
    return item


def test_did_you_mean_opens_pending_and_asks(dym_world):
    from brain.thinking import _react_did_you_mean, EXCHANGE_WIN_K
    from brain import behavior
    from lib.core.io import get_exchange
    from lib.core.models import TKIdeaDoc
    sh = dym_world["speaker"]
    item = _dym_item(str(sh.id))
    assert _react_did_you_mean(item) is True

    # the room: exactly ONE open pending, REFERENCING the item by id, window = clamp(k·tempo)
    room = get_exchange(sh.uid, "dym-chan")
    assert len(room.pending) == 1
    p = room.pending[0]
    assert p.kind == "did_you_mean" and p.status == "open"
    assert p.ref_item_id == str(item.id)                   # a reference, never a copy of the text
    assert p.expires_at - p.opened_at == int(EXCHANGE_WIN_K * 180.0)  # 4 × the seed tempo = 720s

    # the idea: eval:did_you_mean -> tokeniko:ask, directed at the asker, carrying the reading
    idea = TKIdeaDoc.find_one({"trigger": EvalToken.DID_YOU_MEAN.value,
                               "source": str(item.id)}).run()
    assert idea is not None
    assert idea.action_token == TokenikoAction.ASK.value
    assert idea.target == str(sh.id)
    assert idea.answer == {"reading": "the cat is on the bed"}

    # the plan speaks the offered re-hearing VERBATIM (the fence), threaded into the room
    plan = behavior.plan_action(idea, "tokeniko-uid")
    assert plan is not None
    assert plan["payload"]["raw"] == "did you mean: the cat is on the bed?"
    assert plan["payload"]["destination"]["channel_id"] == "dym-chan"


def test_did_you_mean_pending_is_idempotent(dym_world):
    # opening is once-per-item — a re-tick over the same item never stacks a second pending
    from brain.thinking import _react_did_you_mean
    from lib.core.io import get_exchange
    sh = dym_world["speaker"]
    item = _dym_item(str(sh.id))
    _react_did_you_mean(item)
    _react_did_you_mean(item)
    room = get_exchange(sh.uid, "dym-chan")
    assert len(room.pending) == 1


def test_did_you_mean_replaces_the_unknown_why(dym_world, compile_zip):
    # the full think_one route: a processed item carrying suggested_reading spawns the did-you-mean
    # ask and SUPPRESSES the generic unknown-why (the dym branch short-circuits the content reaction),
    # even though the raw stumble grades UNKNOWN. Both rules are seeded (dym_world) — the why does NOT
    # fire.
    import time
    from brain.thinking import think_one
    from lib.core.models import TKBrainStateDoc, TKIdeaDoc, TKMemoryItemDoc
    sh = dym_world["speaker"]
    # a real stumbling zip (unknown vocab -> INSUFFICIENT) + the ASK candidate riding alongside
    item = TKMemoryItemDoc(
        original="a wug is a blicket", zip=compile_zip("a wug is a blicket"),
        sourceId=str(sh.id), channel=MEMChannels.DISCORD, directedness=1.0,
        suggested_reading="a pug is a dog",
        metadata=json.dumps({"channel_id": "dym-chan", "message_id": "m-10"}),
    )
    item.insert()
    bs = TKBrainStateDoc(key="dym-test-state", wake_at=time.time() - 5).insert()
    try:
        assert think_one(bs) is True
        dym_idea = TKIdeaDoc.find_one({"trigger": EvalToken.DID_YOU_MEAN.value,
                                       "source": str(item.id)}).run()
        assert dym_idea is not None and dym_idea.action_token == TokenikoAction.ASK.value
        # the why was SUPPRESSED for this item (asking ≠ believing — no content reflex fires)
        assert TKIdeaDoc.find_one({"trigger": EvalToken.UNKNOWN.value,
                                   "source": str(item.id)}).run() is None
    finally:
        TKBrainStateDoc.get_motor_collection().delete_many({"key": "dym-test-state"})


def test_did_you_mean_directedness_gating(_io):
    # directedness-gated by construction: the ask's urge × the item's directedness vs the 0.5 act
    # threshold — an ambient stumble (0.6) stays silent (0.7×0.6 = 0.42 < 0.5); an addressed one
    # (0.9) speaks (0.63 ≥ 0.5). No special case — the existing effective_urge mechanism.
    from brain.behavior import effective_urge, _AMBIENT_GRADE
    from brain.main import URGE_THRESHOLD
    idea = SimpleNamespace(urge=0.7, trigger=EvalToken.DID_YOU_MEAN.value)
    ambient = SimpleNamespace(directedness=_AMBIENT_GRADE)      # 0.6
    addressed = SimpleNamespace(directedness=0.9)
    assert effective_urge(idea, ambient) < URGE_THRESHOLD       # 0.42 -> quiet
    assert effective_urge(idea, addressed) >= URGE_THRESHOLD    # 0.63 -> speaks
