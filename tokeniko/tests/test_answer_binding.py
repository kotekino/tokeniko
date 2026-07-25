# ------------------------------------------------------------------------------------------------
# THE "DID YOU MEAN?" ANSWER BINDING — the room + ask (1b, 2026-07-25).
#
# The pending LIFECYCLE that resolves an open did_you_mean pending BEFORE the normal assertion path
# (the author's fork b: a «did you mean?» must HANDLE the answer). The asker's next DIRECTED message
# binds it — affirmation re-ingests the reading AS CONFIRMED (now believable), negation drops it,
# a clear restatement supersedes (and falls through to normal ingestion), silence past expires_at
# LAPSES (a lazy check, no scheduler). yes/no via the anchor-catch (multilingual «sì»/«no»).
# ------------------------------------------------------------------------------------------------
import json
import time
from datetime import datetime, timedelta, timezone

import pytest

from lib.core.memory import EvalToken, MEMChannels, MEMPending, TokenikoAction


# ---- the pure classifier (per-token answer polarity, multilingual) --------------------------------

@pytest.mark.parametrize("text,expected", [
    ("yes", "affirmation"), ("Yeah", "affirmation"), ("yep", "affirmation"),
    ("ok", "affirmation"), ("exactly", "affirmation"), ("yes exactly", "affirmation"),
    ("sì", "affirmation"), ("si", "affirmation"), ("esatto", "affirmation"),   # multilingual
    ("no", "negation"), ("Nope", "negation"), ("no.", "negation"), ("nein", "negation"),
    ("no that is wrong", "restatement"),        # a non-answer word survives -> content kept
    ("no, a cat is a dog", "restatement"),      # a reword, never a bare drop
    ("a cat is a dog", "restatement"),
    ("maybe", "restatement"),                   # not a clear yes/no
    ("", "restatement"),
])
def test_classify_answer(text, expected):
    from brain.thinking import _classify_answer
    assert _classify_answer(text) == expected


# ---- the binding lifecycle ------------------------------------------------------------------------

@pytest.fixture()
def bind_world(_io):
    from lib.core.models import (TKExchangeDoc, TKMemoryItemDoc, TKMemoryStakeholdersDoc)
    from lib.core.io import get_exchange
    sh = TKMemoryStakeholdersDoc(uid="binder@bind-test:3", name="binder", isMe=False,
                                 channel=MEMChannels.DISCORD, trust=0.5).save()
    yield {"speaker": sh, "channel_id": "bind-chan"}
    TKMemoryItemDoc.get_motor_collection().delete_many({"sourceId": str(sh.id)})
    TKExchangeDoc.get_motor_collection().delete_many({"user_uid": sh.uid})
    TKMemoryStakeholdersDoc.get_motor_collection().delete_many({"uid": sh.uid})


def _original(sh, channel_id, reading="a pug is a dog"):
    # the stumbling item that carries the offered reading (referenced by the pending, never copied)
    from lib.core.models import TKMemoryItemDoc
    item = TKMemoryItemDoc(
        original="a wug is a blicket", zip=None, sourceId=str(sh.id),
        channel=MEMChannels.DISCORD, directedness=1.0, suggested_reading=reading,
        metadata=json.dumps({"channel_id": channel_id, "message_id": "orig-1"}),
    )
    item.insert()
    return item


def _open_pending(sh, channel_id, ref_item, window=720):
    # seed the room with ONE open did_you_mean pending referencing the original item
    from lib.core.io import get_exchange
    now = int(time.time())
    room = get_exchange(sh.uid, channel_id)
    room.pending = [MEMPending(kind="did_you_mean", ref_item_id=str(ref_item.id),
                               opened_at=now, expires_at=now + window, status="open")]
    room.save()
    return room


def _answer(sh, channel_id, text, directedness=1.0):
    # a lightweight ANSWER turn — the binder reads sourceId / original / directedness / channel key
    from types import SimpleNamespace
    return SimpleNamespace(sourceId=str(sh.id), original=text, directedness=directedness,
                           channel=MEMChannels.DISCORD,
                           metadata=json.dumps({"channel_id": channel_id}))


def test_affirmation_reingests_and_resolves(bind_world, monkeypatch):
    from brain import thinking
    from lib.core.io import get_exchange
    sh, ch = bind_world["speaker"], bind_world["channel_id"]
    ref = _original(sh, ch, reading="a pug is a dog")
    _open_pending(sh, ch, ref)

    captured = {}
    monkeypatch.setattr("brain.api_client.ingest_input",
                        lambda **kw: captured.update(kw) or {"status": "complete", "data": {}})

    verdict = thinking._bind_pending_answer(_answer(sh, ch, "yes"), None)
    assert verdict == "affirmation"
    # the reading was re-ingested through the normal path, attributed to the SAME speaker/channel
    assert captured["tokens"] == "a pug is a dog"
    assert captured["talker"] == sh.uid
    assert captured["channel"] == MEMChannels.DISCORD.value
    # the pending is resolved (never deleted — biography)
    room = get_exchange(sh.uid, ch)
    assert len(room.pending) == 1 and room.pending[0].status == "resolved"


def test_negation_drops_and_resolves(bind_world, monkeypatch):
    from brain import thinking
    from lib.core.io import get_exchange
    sh, ch = bind_world["speaker"], bind_world["channel_id"]
    ref = _original(sh, ch)
    _open_pending(sh, ch, ref)

    called = {"n": 0}
    monkeypatch.setattr("brain.api_client.ingest_input",
                        lambda **kw: called.__setitem__("n", called["n"] + 1))

    verdict = thinking._bind_pending_answer(_answer(sh, ch, "no"), None)
    assert verdict == "negation"
    assert called["n"] == 0                      # a «no» is never re-ingested — the reading is dropped
    room = get_exchange(sh.uid, ch)
    assert room.pending[0].status == "resolved"


def test_restatement_resolves_and_returns_restatement(bind_world, monkeypatch):
    from brain import thinking
    from lib.core.io import get_exchange
    sh, ch = bind_world["speaker"], bind_world["channel_id"]
    ref = _original(sh, ch)
    _open_pending(sh, ch, ref)
    monkeypatch.setattr("brain.api_client.ingest_input", lambda **kw: pytest.fail("no re-ingest on restatement"))

    verdict = thinking._bind_pending_answer(_answer(sh, ch, "a cat is a dog"), None)
    assert verdict == "restatement"              # the caller FALLS THROUGH to normal ingestion
    room = get_exchange(sh.uid, ch)
    assert room.pending[0].status == "resolved"


def test_ambient_aside_does_not_bind(bind_world):
    # the directedness guard: an ambient turn (0.6) mid-window is not necessarily the answer — it does
    # NOT bind, and the pending stays OPEN for a later directed turn.
    from brain import thinking
    from lib.core.io import get_exchange
    sh, ch = bind_world["speaker"], bind_world["channel_id"]
    ref = _original(sh, ch)
    _open_pending(sh, ch, ref)
    verdict = thinking._bind_pending_answer(_answer(sh, ch, "yes", directedness=0.6), None)
    assert verdict is None
    room = get_exchange(sh.uid, ch)
    assert room.pending[0].status == "open"      # still open — nothing was bound


def test_no_open_pending_leaves_normal_path(bind_world):
    # nothing binds when there is no open pending — the normal path is untouched (None)
    from brain import thinking
    sh, ch = bind_world["speaker"], bind_world["channel_id"]
    assert thinking._bind_pending_answer(_answer(sh, ch, "yes"), None) is None


def test_silence_lapses_and_never_binds(bind_world):
    # silence past expires_at -> LAPSE on the next touch (lazy), and a lapsed pending is never a
    # binding target even for a clean «yes».
    from brain import thinking
    from lib.core.io import get_exchange
    sh, ch = bind_world["speaker"], bind_world["channel_id"]
    ref = _original(sh, ch)
    room = get_exchange(sh.uid, ch)
    now = int(time.time())
    room.pending = [MEMPending(kind="did_you_mean", ref_item_id=str(ref.id),
                               opened_at=now - 1000, expires_at=now - 10, status="open")]
    room.save()

    verdict = thinking._bind_pending_answer(_answer(sh, ch, "yes"), None)
    assert verdict is None                        # expired -> not a binding target
    room = get_exchange(sh.uid, ch)
    assert room.pending[0].status == "lapsed"     # folded to lapsed on the touch (never deleted)


# ---- the full think_one route ---------------------------------------------------------------------

@pytest.fixture()
def route_world(_io):
    # seed the eval:unknown -> why rule so a NORMAL assertion path WOULD spawn a why idea — the yes/no
    # tests prove it does NOT (the answer is not an assertion), the restatement proves it DOES.
    from lib.core.models import (TKBehaviorRuleDoc, TKExchangeDoc, TKIdeaDoc,
                                 TKMemoryItemDoc, TKMemoryStakeholdersDoc)
    rule = TKBehaviorRuleDoc(trigger=EvalToken.UNKNOWN.value,
                             action=TokenikoAction.WHY.value, urge=0.6)
    rule.insert()
    sh = TKMemoryStakeholdersDoc(uid="router@bind-test:8", name="router", isMe=False,
                                 channel=MEMChannels.DISCORD, trust=0.5).save()
    yield {"speaker": sh, "channel_id": "route-chan"}
    TKBehaviorRuleDoc.get_motor_collection().delete_many({"trigger": EvalToken.UNKNOWN.value})
    TKIdeaDoc.get_motor_collection().delete_many({"trigger": EvalToken.UNKNOWN.value})
    TKMemoryItemDoc.get_motor_collection().delete_many({"sourceId": str(sh.id)})
    TKExchangeDoc.get_motor_collection().delete_many({"user_uid": sh.uid})
    TKMemoryStakeholdersDoc.get_motor_collection().delete_many({"uid": sh.uid})


def _route_answer_item(sh, channel_id, text, zip_obj, ts):
    from lib.core.models import TKMemoryItemDoc
    item = TKMemoryItemDoc(
        original=text, zip=zip_obj, sourceId=str(sh.id), channel=MEMChannels.DISCORD,
        directedness=1.0, timestamp=ts,
        metadata=json.dumps({"channel_id": channel_id, "message_id": "ans-1"}),
    )
    item.insert()
    return item


def test_think_one_affirmation_stops_the_yes(route_world, compile_zip, monkeypatch):
    # the «yes» is an ANSWER, not an assertion: think_one resolves the pending, re-ingests the reading,
    # and does NOT evaluate the «yes» itself (no eval:unknown -> why idea for it).
    from brain import thinking
    from lib.core.io import get_exchange
    from lib.core.models import TKBrainStateDoc, TKIdeaDoc
    sh, ch = route_world["speaker"], route_world["channel_id"]

    orig = _original(sh, ch, reading="a pug is a dog")   # timestamp = now (before wake)
    _open_pending(sh, ch, orig)
    captured = {}
    monkeypatch.setattr("brain.api_client.ingest_input",
                        lambda **kw: captured.update(kw) or {"status": "complete", "data": {}})

    ans = _route_answer_item(sh, ch, "yes", compile_zip("yes"),
                             datetime.now(timezone.utc) + timedelta(seconds=2))
    bs = TKBrainStateDoc(key="bind-route-state", wake_at=time.time()).insert()
    try:
        assert thinking.think_one(bs) is True
        assert captured.get("tokens") == "a pug is a dog"       # the reading WAS re-ingested
        room = get_exchange(sh.uid, ch)
        assert room.pending[0].status == "resolved"
        # the «yes» itself drove NO content reaction (no why idea for its id)
        assert TKIdeaDoc.find_one({"trigger": EvalToken.UNKNOWN.value,
                                   "source": str(ans.id)}).run() is None
    finally:
        TKBrainStateDoc.get_motor_collection().delete_many({"key": "bind-route-state"})


def test_think_one_restatement_falls_through(route_world, compile_zip, monkeypatch):
    # a restatement resolves the pending AND ingests normally (the reworded assertion grades UNKNOWN
    # -> the seeded why idea IS spawned for it): the fall-through the affirmation/negation paths skip.
    from brain import thinking
    from lib.core.io import get_exchange
    from lib.core.models import TKBrainStateDoc, TKIdeaDoc
    sh, ch = route_world["speaker"], route_world["channel_id"]

    orig = _original(sh, ch)
    _open_pending(sh, ch, orig)
    monkeypatch.setattr("brain.api_client.ingest_input",
                        lambda **kw: pytest.fail("no re-ingest on a restatement"))

    ans = _route_answer_item(sh, ch, "a wug is a blicket", compile_zip("a wug is a blicket"),
                             datetime.now(timezone.utc) + timedelta(seconds=2))
    bs = TKBrainStateDoc(key="bind-route-state2", wake_at=time.time()).insert()
    try:
        assert thinking.think_one(bs) is True
        room = get_exchange(sh.uid, ch)
        assert room.pending[0].status == "resolved"             # the reword superseded
        # the normal assertion path RAN for the reworded turn (its own why idea)
        assert TKIdeaDoc.find_one({"trigger": EvalToken.UNKNOWN.value,
                                   "source": str(ans.id)}).run() is not None
    finally:
        TKBrainStateDoc.get_motor_collection().delete_many({"key": "bind-route-state2"})
