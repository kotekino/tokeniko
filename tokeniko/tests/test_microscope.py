"""rag3 P1 — the microscope (the instrument arc, 2026-07-14 summit).

Covers the three organs: the DIGEST (pure — a deterministic structural rendering of a zip), the
JUDGE (schema/validation behavior over a fake client — same discipline as the blog polish tests:
any failure returns None, never raises), and the PASS (sandbox: inputs-only filtering, dedup by
item_id, an entry written with the verdict). The memory collection is a TIMESERIES — cleanup uses
raw pymongo delete_many (the bunnet delete no-op).
"""
import asyncio
import json

import pytest

from lib.core.memory import MEMChannels
from lib.core.tk import TKOperator, TKQuantifier, TKWhRole
from lib.core.tkzip import TKZip, TKZipContent, TKZipItem
from senses import microscope


# ---- the digest (pure) -----------------------------------------------------------------------

def _leaf(op=TKOperator.AND, **over):
    fields = dict(senses={"subject": "coin.n.01", "predicate": "have.v.01", "direct": "value.n.01"},
                  quantifier=TKQuantifier.INDEFINITE)
    fields.update(over)
    return TKZipItem(op=op, content=TKZipContent(subject=None, predicate=None, direct=None, **fields))


def test_digest_renders_roles_operators_and_flags():
    zp = TKZip(map=[0.0] * 8, items=TKZipItem(content=[
        _leaf(),
        _leaf(op=TKOperator.CONV, senses={"subject": "person.n.01", "predicate": "state.v.01"},
              quantifier=TKQuantifier.GENERIC, negated=True),
    ]))
    d = microscope.digest_zip(zp)
    assert "subject: coin.n.01" in d and "direct: value.n.01" in d
    assert "op=CONV" in d                      # the operator survives — the storm's tell
    assert "negated=True" in d
    assert "quantifier=indefinite" in d


def test_digest_carries_mood_and_identity():
    zp = TKZip(map=[0.0] * 8, items=TKZipItem(content=[
        _leaf(dubitative=1.0, wh_role=TKWhRole.TIME,
              identities={"subject": "kotekino@discord:1"}),
    ]))
    d = microscope.digest_zip(zp)
    assert "mood=question" in d and "wh_role=time" in d
    assert "kotekino@discord:1" in d


def test_digest_is_deterministic():
    zp = TKZip(map=[0.0] * 8, items=TKZipItem(content=[_leaf()]))
    assert microscope.digest_zip(zp) == microscope.digest_zip(zp)


# ---- the judge (fake client) ------------------------------------------------------------------

class _FakeMessages:
    def __init__(self, text=None, exc=None):
        self._text, self._exc = text, exc

    async def create(self, **kwargs):
        if self._exc:
            raise self._exc
        block = type("B", (), {"type": "text", "text": self._text})()
        return type("R", (), {"content": [block]})()


class _FakeClient:
    def __init__(self, text=None, exc=None):
        self.messages = _FakeMessages(text=text, exc=exc)


_GOOD = {"verdict": "mismatch", "confidence": 0.9, "severity": "high",
         "category": "operator-flattening", "note": "the IF clause reads as a bare assertion"}


def test_judge_returns_the_validated_verdict():
    out = asyncio.run(microscope.judge("s", "d", subject_uid=None, client=_FakeClient(text=json.dumps(_GOOD))))
    assert out["verdict"] == "mismatch" and out["category"] == "operator-flattening"
    from lib.rag import RAG3_JUDGE
    assert out["model"] == RAG3_JUDGE.model


def test_judge_clamps_confidence():
    payload = dict(_GOOD, confidence=7.5)
    out = asyncio.run(microscope.judge("s", "d", subject_uid=None, client=_FakeClient(text=json.dumps(payload))))
    assert out["confidence"] == 1.0


@pytest.mark.parametrize("bad", [
    dict(exc=RuntimeError("api down")),
    dict(text="not json {"),
    dict(text=json.dumps({"verdict": "maybe", "confidence": 0.5,
                          "severity": None, "category": None, "note": None})),
])
def test_judge_failure_returns_none_never_raises(bad):
    assert asyncio.run(microscope.judge("s", "d", subject_uid=None, client=_FakeClient(**bad))) is None


# ---- the pass (sandbox) -----------------------------------------------------------------------

@pytest.fixture()
def clean_microscope(_io):
    from lib.core.io import init_io  # noqa: F401 (the _io fixture already ran it)
    from lib.core.models import TKMemoryItemDoc, TKZipDebugDoc

    def _wipe():
        TKZipDebugDoc.find({"original": {"$regex": "^rag3-test"}}).delete().run()
        # the memory collection is a TIMESERIES: bunnet delete is a silent no-op — raw pymongo
        col = TKMemoryItemDoc.get_motor_collection()
        col.delete_many({"original": {"$regex": "^rag3-test"}})

    _wipe()
    yield
    _wipe()


def _mk_item(original, source_id):
    from lib.core.models import TKMemoryItemDoc
    zp = TKZip(map=[0.0] * 8, items=TKZipItem(content=TKZipContent(
        subject=None, predicate=None, direct=None,
        senses={"subject": "coin.n.01", "predicate": "have.v.01"})))
    item = TKMemoryItemDoc(original=original, sourceId=source_id,
                           channel=MEMChannels.DISCORD, zip=zp)
    item.insert()
    return item


# the microscope is INSIDE the consent gate (privacy §1 step 3, the Captain's ruling 2026-07-29):
# its payload opens with the speaker's sentence verbatim, so the judge only runs for a speaker who
# allowed it. The instrument is deliberately absent from the consent NOTICE — it is a debug tool,
# disabled before the public opening — but the flag is a code backstop on that process control.
# This fixture gives the judged item a speaker who said yes; the denial side is test_consent's.
@pytest.fixture()
def consenting_speaker(_io):
    from lib.core.consent import install_consent_reader, record_consent
    from lib.core.memory import MEMChannels
    from lib.core.models import TKMemoryStakeholdersDoc
    from lib.rag import set_consent_reader
    uid = "rag3-parlante@discord:7001"
    TKMemoryStakeholdersDoc.get_motor_collection().delete_many({"uid": uid})
    sh = TKMemoryStakeholdersDoc(uid=uid, name="rag3-parlante", isMe=False,
                                 channel=MEMChannels.DISCORD, contextKey="discord:7001").save()
    record_consent(uid, True, name="rag3-parlante")
    install_consent_reader()
    yield sh
    set_consent_reader(None)
    TKMemoryStakeholdersDoc.get_motor_collection().delete_many({"uid": uid})


def test_pass_judges_only_others_inputs_and_dedups(_io, clean_microscope, consenting_speaker):
    from lib.core.io import get_tokeniko
    from lib.core.models import TKZipDebugDoc
    me = str(get_tokeniko().id)
    _mk_item("rag3-test self talk", me)                       # self: never judged (inputs-only)
    other = _mk_item("rag3-test a coin has value", str(consenting_speaker.id))

    fake = _FakeClient(text=json.dumps(dict(_GOOD, verdict="ok", severity=None, category=None)))
    n = asyncio.run(microscope.microscope_pass(client=fake, batch=10))
    assert n == 1
    entries = TKZipDebugDoc.find({"original": {"$regex": "^rag3-test"}}).to_list()
    assert len(entries) == 1
    assert entries[0].item_id == str(other.id) and entries[0].verdict == "ok"
    assert "coin.n.01" in entries[0].digest

    # second pass: everything already judged -> nothing written (dedup by item_id)
    assert asyncio.run(microscope.microscope_pass(client=fake, batch=10)) == 0


# ---- the denial is not a failure (2026-08-03) --------------------------------------------------
# Live symptom: «[rag:rag3-judge] denied — no consent for 6a6a…» every 60 seconds, forever. The two
# failures wore the same `None` and are entirely different animals — an API failure SHOULD retry,
# a consent denial will not change until a human presses a button. The denial now MARKS the item
# and moves on; the mark is keyed by the speaker so it lapses the day they consent.

@pytest.fixture()
def silent_speaker(_io):
    """A stakeholder who has NOT consented — the mirror armed, the answer absent."""
    from lib.core.consent import install_consent_reader
    from lib.core.memory import MEMChannels
    from lib.core.models import TKMemoryStakeholdersDoc
    from lib.rag import set_consent_reader
    uid = "rag3-silenzioso@discord:7002"
    TKMemoryStakeholdersDoc.get_motor_collection().delete_many({"uid": uid})
    sh = TKMemoryStakeholdersDoc(uid=uid, name="rag3-silenzioso", isMe=False,
                                 channel=MEMChannels.DISCORD, contextKey="discord:7002").save()
    install_consent_reader()
    yield sh
    set_consent_reader(None)
    TKMemoryStakeholdersDoc.get_motor_collection().delete_many({"uid": uid})


class _ExplodingClient:
    """Reaching the wire at all is the failure — a denied item must never get that far."""
    class _Messages:
        async def create(self, **kwargs):
            raise AssertionError("a denied item reached the judge — THE GATE LEAKED")

    def __init__(self):
        self.messages = self._Messages()


def test_a_denied_item_is_marked_unjudgeable_and_never_retried(_io, clean_microscope, silent_speaker):
    from lib.core.models import TKZipDebugDoc
    item = _mk_item("rag3-test a coin has value", str(silent_speaker.id))

    assert asyncio.run(microscope.microscope_pass(client=_ExplodingClient(), batch=10)) == 0
    rows = TKZipDebugDoc.find({"original": {"$regex": "^rag3-test"}}).to_list()
    assert len(rows) == 1
    row = rows[0]
    assert row.verdict == microscope.SKIPPED       # NOT a verdict — no judge ever saw it
    assert row.item_id == str(item.id)
    assert row.subject_uid == str(silent_speaker.id)   # the key the reversal reads
    assert row.digest == "" and row.note                # nothing was shown; the why is recorded

    # the point of the marker: the next pass does not ask again, and writes nothing further.
    assert asyncio.run(microscope.microscope_pass(client=_ExplodingClient(), batch=10)) == 0
    assert len(TKZipDebugDoc.find({"original": {"$regex": "^rag3-test"}}).to_list()) == 1


def test_a_skip_is_never_counted_as_a_lead(_io, clean_microscope, silent_speaker):
    # every lead query reads verdict == "mismatch"; an unjudgeable item must never appear in one.
    from lib.core.models import TKZipDebugDoc
    _mk_item("rag3-test a coin has value", str(silent_speaker.id))
    asyncio.run(microscope.microscope_pass(client=_ExplodingClient(), batch=10))
    leads = TKZipDebugDoc.find({"original": {"$regex": "^rag3-test"},
                                "verdict": "mismatch"}).to_list()
    assert leads == []


def test_the_skip_lapses_the_day_the_speaker_consents(_io, clean_microscope, silent_speaker):
    """REVERSIBLE, which is the whole constraint — a skip is a note of WHY, not a write-off."""
    from lib.core.consent import record_consent
    from lib.core.models import TKZipDebugDoc
    item = _mk_item("rag3-test a coin has value", str(silent_speaker.id))
    asyncio.run(microscope.microscope_pass(client=_ExplodingClient(), batch=10))
    assert TKZipDebugDoc.find({"item_id": str(item.id)}).to_list()[0].verdict == microscope.SKIPPED

    record_consent(silent_speaker.uid, True, name="rag3-silenzioso")
    fake = _FakeClient(text=json.dumps(dict(_GOOD, verdict="ok", severity=None, category=None)))
    assert asyncio.run(microscope.microscope_pass(client=fake, batch=10)) == 1

    rows = TKZipDebugDoc.find({"item_id": str(item.id)}).to_list()
    assert len(rows) == 1                          # the marker was bookkeeping — replaced, not kept
    assert rows[0].verdict == "ok" and rows[0].digest


def test_an_api_failure_still_retries(_io, clean_microscope, consenting_speaker):
    # the other half of the distinction: a transient failure leaves the item UNJUDGED, and the next
    # pass tries again. Nothing is marked, because nothing is known to be impossible.
    from lib.core.models import TKZipDebugDoc
    _mk_item("rag3-test a coin has value", str(consenting_speaker.id))
    broken = _FakeClient(exc=RuntimeError("api down"))
    assert asyncio.run(microscope.microscope_pass(client=broken, batch=10)) == 0
    assert TKZipDebugDoc.find({"original": {"$regex": "^rag3-test"}}).to_list() == []

    fake = _FakeClient(text=json.dumps(dict(_GOOD, verdict="ok", severity=None, category=None)))
    assert asyncio.run(microscope.microscope_pass(client=fake, batch=10)) == 1


def test_a_skipped_item_costs_no_batch_slot(_io, clean_microscope, silent_speaker,
                                            consenting_speaker):
    # a permanently-unjudgeable item must not sit at the head of the queue eating the batch: with
    # batch=1 the judgeable item behind it is still reached on the very next pass.
    from lib.core.models import TKZipDebugDoc
    _mk_item("rag3-test unjudgeable", str(silent_speaker.id))
    good = _mk_item("rag3-test a coin has value", str(consenting_speaker.id))
    fake = _FakeClient(text=json.dumps(dict(_GOOD, verdict="ok", severity=None, category=None)))

    assert asyncio.run(microscope.microscope_pass(client=fake, batch=1)) == 0   # the skip is written
    assert asyncio.run(microscope.microscope_pass(client=fake, batch=1)) == 1   # and stands aside
    judged = TKZipDebugDoc.find({"item_id": str(good.id)}).to_list()
    assert len(judged) == 1 and judged[0].verdict == "ok"


def test_judge_maps_sentinels_to_none():
    # the schema carries no null unions (the API rejects enum-vs-type-array) — "none"/"" come back
    # as sentinels and must land as real Nones in the entry
    payload = {"verdict": "ok", "confidence": 0.95, "severity": "none", "category": "none", "note": ""}
    out = asyncio.run(microscope.judge("s", "d", subject_uid=None, client=_FakeClient(text=json.dumps(payload))))
    assert out["verdict"] == "ok"
    assert out["severity"] is None and out["category"] is None and out["note"] is None
