"""THE CONSENT GATE — privacy §1 step 3 (2026-07-29).

The first constraint in this engine that is ETHICAL rather than logical: before a stranger's words
may reach a third party, that stranger must have said yes. What is asserted here is the property
the design was built for — LEAK-PROOF BY CONSTRUCTION, not by discipline:

  - the gate lives at rag_call, the ONE door every Claude call passes through;
  - it asks «whose words is this payload carrying?», not «which instrument is this?» — which is
    what closes the back door (the «did you mean…?» ask is outbound speech carrying inbound words);
  - unasked behaves exactly as denied, and an UNWIRED process denies everything.

No network, ever: the client factory is booby-trapped in every gated test, so a leak is a loud
AssertionError rather than a silent HTTP call. Discord objects are faked; no gateway is touched.
The mirror tests run against the sandbox memory DB like the rest of the gate.
"""
import asyncio
import time
from types import SimpleNamespace

import pytest

from lib.core.consent import (
    CONSENT_TEXT, CONSENT_TEXT_VERSION, clear_consent, consent_for, record_consent,
)
from lib.discord.models import DiscordMember


def _run(coro):
    return asyncio.run(coro)


# ---- fakes ---------------------------------------------------------------------------------

class _FakeMessages:
    def __init__(self, text="tidied."):
        self._text, self.calls = text, []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=self._text)])


class _FakeClient:
    def __init__(self, text="tidied."):
        self.messages = _FakeMessages(text)


@pytest.fixture()
def no_cloud(monkeypatch):
    """Booby-trap the process client: reaching the wire at all is a test failure. This is what
    makes «no HTTP» an assertion rather than a hope."""
    import lib.rag.client as client_module

    def exploded():
        raise AssertionError("a gated call reached the Anthropic client — THE GATE LEAKED")

    monkeypatch.setattr(client_module, "get_client", exploded)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")   # the instruments' arm-checks
    monkeypatch.delenv("RAG1_DISABLED", raising=False)
    monkeypatch.delenv("RAG4_DISABLED", raising=False)
    monkeypatch.delenv("RAG2_OUT_DISABLED", raising=False)


@pytest.fixture()
def reader(monkeypatch):
    """Install a consent reader for the duration of one test and restore the deny-all default."""
    from lib.rag import set_consent_reader

    def _install(fn):
        set_consent_reader(fn)

    yield _install
    set_consent_reader(None)


@pytest.fixture()
def subject(_io):
    """A sandbox stakeholder to hold the mirror — created unasked, removed after."""
    from lib.core.models import TKMemoryStakeholdersDoc
    from lib.core.memory import MEMChannels
    uid = "consentito@discord:9001"
    TKMemoryStakeholdersDoc.get_motor_collection().delete_many({"uid": uid})
    sh = TKMemoryStakeholdersDoc(uid=uid, name="consentito", isMe=False,
                                 channel=MEMChannels.DISCORD, contextKey="discord:9001").save()
    yield sh
    TKMemoryStakeholdersDoc.get_motor_collection().delete_many({"uid": uid})


# every instrument that carries a PERSON's words, exercised through its own public function —
# not through rag_call — so the assertion covers the threading too, not just the gate.
def _every_user_carrying_instrument(uid: str) -> list:
    from lib.llc import language
    from lib.llc.decompiler import decompiler_decompile
    from lib.llc.normalizer import normalizer_polish
    from senses import microscope, outbound
    return [
        ("rag1 normalizer", _run(normalizer_polish("the catt is a mamal", subject_uid=uid))),
        ("rag4 readers", _run(language.translate_in("il gatto", subject_uid=uid))),
        ("rag4 translate-out", _run(language.translate_out("yes", "italian", subject_uid=uid))),
        ("rag4 back-translate", _run(language.back_translate("sì", subject_uid=uid))),
        ("rag2 decompile", _run(decompiler_decompile("(A cat IS mammal)", subject_uid=uid))),
        ("rag3 judge", _run(microscope.judge("a cat is a mammal", "clause[0]", subject_uid=uid))),
        ("rag2-out polish", _run(outbound._polish("I do not agree with that claim at all", uid))),
    ]


def _assert_all_denied(results, raw_for_polish: str = "I do not agree with that claim at all"):
    by_name = dict(results)
    assert by_name["rag1 normalizer"] is None
    assert by_name["rag4 readers"] == (None, None)      # half a consensus is no reading
    assert by_name["rag4 translate-out"] is None
    assert by_name["rag4 back-translate"] is None
    assert by_name["rag2 decompile"] == "(A cat IS mammal)"   # the raw render, unchanged
    assert by_name["rag3 judge"] is None
    assert by_name["rag2-out polish"] == raw_for_polish       # the scaffold ships verbatim


# ---- 1-2. unasked and denied are the same thing at the gate ---------------------------------

def test_unasked_denies_every_user_carrying_instrument(subject, no_cloud):
    # THE WINDOW between someone's first word and their answer: nothing leaks in it. `None` is not
    # a third state at the gate — it is a denial that has not been spoken yet.
    from lib.core.consent import install_consent_reader
    from lib.rag import set_consent_reader
    install_consent_reader()
    try:
        assert consent_for(subject.uid) is None
        _assert_all_denied(_every_user_carrying_instrument(subject.uid))
    finally:
        set_consent_reader(None)


def test_explicit_refusal_denies_every_user_carrying_instrument(subject, no_cloud):
    from lib.core.consent import install_consent_reader
    from lib.rag import set_consent_reader
    install_consent_reader()
    try:
        record_consent(subject.uid, False, name="consentito")
        assert consent_for(subject.uid) is False
        _assert_all_denied(_every_user_carrying_instrument(subject.uid))
    finally:
        set_consent_reader(None)


# ---- 3. an explicit yes proceeds -------------------------------------------------------------

def test_allowed_proceeds(subject, reader):
    from lib.core.consent import install_consent_reader
    from senses import microscope
    install_consent_reader()
    try:
        record_consent(subject.uid, True, name="consentito")
        assert consent_for(subject.uid) is True
        client = _FakeClient(text='{"verdict": "ok", "confidence": 0.9, "severity": "none",'
                                  ' "category": "none", "note": ""}')
        out = _run(microscope.judge("a cat is a mammal", "clause[0]",
                                    subject_uid=subject.uid, client=client))
        assert out is not None and out["verdict"] == "ok"
        assert len(client.messages.calls) == 1          # the call was actually made
    finally:
        from lib.rag import set_consent_reader
        set_consent_reader(None)


# ---- 4. the fail-closed default: an UNWIRED process is a silent process ----------------------

def test_an_unwired_reader_denies(no_cloud):
    # no install_consent_reader() anywhere — a process that never declared how it reads consent
    # must never send anyone's words. This is the property that survives a future process being
    # added by someone who forgets the wiring.
    from lib.rag import RAG1_NORMALIZER, rag_call, set_consent_reader
    set_consent_reader(None)
    assert _run(rag_call(RAG1_NORMALIZER, "anything", subject_uid="a-stranger@discord:1")) is None


def test_a_raising_reader_denies(no_cloud):
    # fail CLOSED, not open: a reader that blows up (Mongo down mid-flight) must deny, never pass.
    from lib.rag import RAG1_NORMALIZER, rag_call, set_consent_reader

    def broken(uid):
        raise RuntimeError("mongo is gone")

    set_consent_reader(broken)
    try:
        assert _run(rag_call(RAG1_NORMALIZER, "anything", subject_uid="x@discord:1")) is None
    finally:
        set_consent_reader(None)


# ---- 5. tokeniko's own content is never gated ------------------------------------------------

def test_subject_uid_none_proceeds_with_no_reader():
    # the deny-all default is in force, and it does not matter: nobody's words are in this payload.
    from lib.rag import RAG1_NORMALIZER, rag_call, set_consent_reader
    set_consent_reader(None)
    client = _FakeClient(text="a fluent English sentence.")
    assert _run(rag_call(RAG1_NORMALIZER, "raw render", subject_uid=None,
                         client=client)) == "a fluent English sentence."
    assert len(client.messages.calls) == 1


def test_the_signature_forces_the_decision():
    # subject_uid is REQUIRED with NO DEFAULT — the leak-proof property expressed in the signature
    # rather than in a comment: a future instrument cannot be added without its author consciously
    # deciding whose words it carries.
    import inspect
    from lib.rag import RAG1_NORMALIZER, rag_call
    param = inspect.signature(rag_call).parameters["subject_uid"]
    assert param.kind is inspect.Parameter.KEYWORD_ONLY
    assert param.default is inspect.Parameter.empty
    with pytest.raises(TypeError):
        _run(rag_call(RAG1_NORMALIZER, "x"))


# ---- 6. THE BACK DOOR ------------------------------------------------------------------------

def test_the_did_you_mean_ask_for_a_denied_user_makes_no_cloud_call_but_still_replies(
        no_cloud, reader, monkeypatch):
    """The single strongest argument for gating on the PAYLOAD rather than the direction.

    A «did you mean: …?» is classified as OUTBOUND — tokeniko's own speech — yet its text literally
    carries the listener's own sentence back out. Under an "inbound gated, outbound free" rule it
    would ship an opted-out speaker's words to the cloud through the localizer. Here it does not,
    and the person still gets an answer."""
    from senses import outbound
    reader(lambda uid: False)
    monkeypatch.setattr(outbound, "_room_language", lambda uid, chan: "italian")
    ask = "did you mean: «the cat is a mammal and it feeds its young»?"
    spoken = _run(outbound._voice_out(ask, "rifiutato@discord:9002", "chan"))
    assert spoken == ask          # not silence, not a crash — the English reply ships


# ---- 7. THE PERSISTENT-VIEW TRAP -------------------------------------------------------------

def test_the_consent_view_is_persistent_and_registered_from_setup_hook():
    """All three conditions, and the third is the one that fails SILENTLY.

    (1) and (2) — no timeout, an explicit custom_id per component — discord.py enforces loudly:
    add_view raises ValueError otherwise. (3) — registration in setup_hook rather than on_ready —
    raises nothing at all; it just means every restart quietly kills the buttons of the already-
    posted notice. Hence this assertion."""
    from senses.privacy import CUSTOM_ID_ALLOW, CUSTOM_ID_DENY, ConsentView, consent_setup_hook

    view = ConsentView()
    assert view.timeout is None                                    # (1)
    ids = [c.custom_id for c in view.children]
    assert ids == [CUSTOM_ID_ALLOW, CUSTOM_ID_DENY]                # (2) — and version-stamped
    assert all(CONSENT_TEXT_VERSION in i for i in ids)

    # (3): the hook the adapter hands to discord.Client registers the view.
    registered, swept = [], []

    class _FakeClient:
        def add_view(self, v):
            registered.append(v)

        async def wait_until_ready(self):
            swept.append("ready")

        def members(self):
            return []

    fake = _FakeClient()
    _run(consent_setup_hook(fake)())
    assert len(registered) == 1 and isinstance(registered[0], ConsentView)
    assert registered[0].timeout is None


def test_the_adapter_installs_the_hook_where_discordpy_actually_awaits_it():
    # discord.py awaits setup_hook() at the END OF login() — before the gateway connects. The
    # adapter constructs discord.Client directly, so this instance-level seam is the only place a
    # persistent view can be re-registered at all.
    import discord
    from lib.discord.client import DiscordClient

    async def hook():
        return None

    client = DiscordClient.__new__(DiscordClient)          # no token, no gateway
    client._client = discord.Client(intents=discord.Intents.default())
    client.set_setup_hook(hook)
    assert client._client.setup_hook is hook


def test_the_members_intent_and_manage_roles_are_armed():
    # the privileged intent the whole mirror depends on, and the permission bit the roles need.
    from lib.discord.constants import INVITE_PERMISSIONS, default_intents
    assert default_intents().members is True
    assert INVITE_PERMISSIONS & (1 << 28)                  # MANAGE_ROLES


# ---- 8. the flip -----------------------------------------------------------------------------

def test_allow_deny_allow_the_mirror_follows(subject):
    record_consent(subject.uid, True, name="consentito")
    first = consent_for(subject.uid)
    from lib.core.consent import _body
    at_allow = _body(subject.uid).consent_at
    assert first is True and at_allow is not None
    assert _body(subject.uid).consent_text_version == CONSENT_TEXT_VERSION

    time.sleep(1.1)                                  # consent_at is epoch SECONDS
    record_consent(subject.uid, False, name="consentito")
    assert consent_for(subject.uid) is False
    at_deny = _body(subject.uid).consent_at
    assert at_deny > at_allow                        # the moment of the answer moves with it

    time.sleep(1.1)
    record_consent(subject.uid, True, name="consentito")
    assert consent_for(subject.uid) is True
    assert _body(subject.uid).consent_at > at_deny


def test_consent_does_not_resolve_through_canonical_uid(_io):
    """The deliberate asymmetry with the trust ledger — consent is an act performed IN A ROOM.

    A soul's Discord body agreeing does not make its API body agree: trust unifies channel bodies
    into one ledger, consent does not."""
    from lib.core.models import TKMemoryStakeholdersDoc
    from lib.core.memory import MEMChannels
    canon_uid, body_uid = "anima-consenso", "anima@discord:9003"
    for uid in (canon_uid, body_uid):
        TKMemoryStakeholdersDoc.get_motor_collection().delete_many({"uid": uid})
    try:
        TKMemoryStakeholdersDoc(uid=canon_uid, name="anima", isMe=False,
                                channel=MEMChannels.INTERNAL).save()
        TKMemoryStakeholdersDoc(uid=body_uid, name="anima", isMe=False,
                                channel=MEMChannels.DISCORD, contextKey="discord:9003",
                                canonical_uid=canon_uid).save()
        record_consent(body_uid, True, name="anima")
        assert consent_for(body_uid) is True
        assert consent_for(canon_uid) is None        # the soul did not inherit the room's answer
    finally:
        for uid in (canon_uid, body_uid):
            TKMemoryStakeholdersDoc.get_motor_collection().delete_many({"uid": uid})


# ---- 9. the startup sweep: the mirror is SELF-HEALING ----------------------------------------

def test_startup_reconciliation_corrects_a_mirror_that_contradicts_the_roles(subject):
    """A hand-edited role, a missed event, a restart-window gap — all heal at the next boot."""
    from senses.privacy import reconcile_members, role_allow, role_deny

    record_consent(subject.uid, True, name="consentito")
    assert consent_for(subject.uid) is True

    # the ROLES say otherwise: they are the truth, the mirror is the mirror.
    member = DiscordMember(user_id="9001", name="consentito", guild_id="g1",
                           role_names=["@everyone", role_deny()])
    assert reconcile_members([member]) == 1
    assert consent_for(subject.uid) is False

    member.role_names = ["@everyone", role_allow()]
    reconcile_members([member])
    assert consent_for(subject.uid) is True

    # neither role -> back to unasked, and unasked denies. Never a stamped answer nobody gave.
    member.role_names = ["@everyone"]
    reconcile_members([member])
    assert consent_for(subject.uid) is None
    from lib.core.consent import _body
    assert _body(subject.uid).consent_at is None


def test_tokenikos_own_account_is_never_mirrored(subject):
    """The guard found live while the server was being configured (2026-07-29).

    His own content is `subject_uid=None` by design, so a consent record for himself is meaningless;
    holding both roles is a state only the bot account can reach; and if his channel visibility ever
    leant on a consent role, the re-consent sweep would make him DEAF on his own server — presenting
    as an engine bug rather than a permissions one. Scoped to SELF, never to bots generally: a
    playbot is driven by a person and genuinely does owe an answer."""
    from senses.privacy import forget_member, reconcile_member, role_allow

    record_consent(subject.uid, True, name="consentito")
    me = DiscordMember(user_id="9001", name="consentito", guild_id="g1",
                       role_names=[role_allow(), "Outside help: no"], is_self=True)
    assert reconcile_member(me) is None
    assert consent_for(subject.uid) is True      # untouched — no write, no clear, no tiebreak
    forget_member(me)
    assert consent_for(subject.uid) is True      # and a self "departure" erases nothing


def test_a_playbot_is_not_exempt(subject):
    # only the bot's OWN id is excluded: any other account — playbot included — answers for itself,
    # and an unanswered one is already safe by default-deny.
    from senses.privacy import reconcile_member, role_deny
    other = DiscordMember(user_id="9001", name="consentito", guild_id="g1",
                          role_names=[role_deny()], is_self=False)
    assert reconcile_member(other) is False
    assert consent_for(subject.uid) is False


def test_a_self_click_records_nothing(subject):
    # unreachable through the UI (bots cannot press buttons) — the third door of the same rule.
    from senses.privacy import CONFIRM_FAILED, apply_choice, role_allow, role_deny
    roles = [_FakeRole(role_allow()), _FakeRole(role_deny())]
    member = _FakeMember(9001, "consentito", roles=[])
    interaction = SimpleNamespace(user=member, guild=SimpleNamespace(id=1, roles=roles),
                                  client=SimpleNamespace(user=SimpleNamespace(id=9001)))
    assert _run(apply_choice(interaction, True)) == CONFIRM_FAILED
    assert member.added == [] and consent_for(subject.uid) is None


def test_the_role_names_are_matched_literally():
    # the configured strings carry a colon and spaces; nothing slugifies or normalizes them.
    from senses.privacy import consent_from_roles, role_allow, role_deny
    assert role_allow() == "Outside help: yes" and role_deny() == "Outside help: no"
    assert consent_from_roles(["outside help: yes"]) is None      # case matters — literal match
    assert consent_from_roles(["Outside-help-yes"]) is None       # no slug is ever accepted


def test_both_roles_at_once_is_not_an_answer():
    # a server-side accident, not a choice — it reads None, and None denies.
    from senses.privacy import consent_from_roles, role_allow, role_deny
    assert consent_from_roles([role_allow()]) is True
    assert consent_from_roles([role_deny()]) is False
    assert consent_from_roles([role_allow(), role_deny()]) is None
    assert consent_from_roles([]) is None


# ---- 10. leaving the room withdraws consent ---------------------------------------------------

def test_leaving_the_room_clears_the_mirror(subject):
    from senses.privacy import forget_member
    record_consent(subject.uid, True, name="consentito")
    assert consent_for(subject.uid) is True
    forget_member(DiscordMember(user_id="9001", name="consentito", guild_id="g1", role_names=[]))
    assert consent_for(subject.uid) is None          # consent was given IN the room


# ---- 11. a failed role assignment FAILS CLOSED ------------------------------------------------

class _FakeRole:
    def __init__(self, name):
        self.name = name


class _FakeMember:
    def __init__(self, uid, name, roles, forbid=False):
        self.id, self.name, self.roles = uid, name, roles
        self._forbid = forbid
        self.added, self.removed = [], []

    async def add_roles(self, *roles, reason=None):
        if self._forbid:
            import discord
            raise discord.Forbidden(SimpleNamespace(status=403, reason="Forbidden"),
                                    "Missing Permissions")
        self.added += list(roles)

    async def remove_roles(self, *roles, reason=None):
        self.removed += list(roles)


def _interaction(member, roles):
    return SimpleNamespace(user=member, guild=SimpleNamespace(id=1, roles=roles))


def test_a_forbidden_role_assignment_records_nothing(subject):
    """Role hierarchy misconfigured (tokeniko's own role not ABOVE the consent roles) — the member
    is told plainly and the mirror is left UNTOUCHED. A mirror written against a role that could
    not be assigned would be a lie the next sweep would 'heal' by undoing the person's choice."""
    from senses.privacy import CONFIRM_FAILED, apply_choice, role_allow, role_deny

    roles = [_FakeRole(role_allow()), _FakeRole(role_deny())]
    member = _FakeMember(9001, "consentito", roles=[], forbid=True)
    reply = _run(apply_choice(_interaction(member, roles), True))
    assert reply == CONFIRM_FAILED
    assert consent_for(subject.uid) is None          # nothing recorded — fails CLOSED


def test_a_missing_role_records_nothing(subject):
    # the roles were never created server-side: same discipline, no write, an honest reply.
    from senses.privacy import CONFIRM_FAILED, apply_choice
    member = _FakeMember(9001, "consentito", roles=[])
    reply = _run(apply_choice(_interaction(member, []), True))
    assert reply == CONFIRM_FAILED
    assert consent_for(subject.uid) is None


def test_a_successful_click_moves_both_the_role_and_the_mirror(subject):
    from senses.privacy import CONFIRM_ALLOW, CONFIRM_DENY, apply_choice, role_allow, role_deny
    allow_role, deny_role = _FakeRole(role_allow()), _FakeRole(role_deny())
    roles = [allow_role, deny_role]

    member = _FakeMember(9001, "consentito", roles=[])
    assert _run(apply_choice(_interaction(member, roles), True)) == CONFIRM_ALLOW
    assert member.added == [allow_role] and member.removed == []
    assert consent_for(subject.uid) is True

    # the change of mind: the other button grants its role and REVOKES the first.
    member = _FakeMember(9001, "consentito", roles=[allow_role])
    assert _run(apply_choice(_interaction(member, roles), False)) == CONFIRM_DENY
    assert member.added == [deny_role] and member.removed == [allow_role]
    assert consent_for(subject.uid) is False


# ---- the frozen text --------------------------------------------------------------------------

def test_the_notice_is_frozen_and_fits_the_medium():
    """The text is the Captain's, it is the legal artifact, and the version is the contract: change
    a character and the version MUST bump (the «change the text -> ask again» rule keys off it)."""
    assert CONSENT_TEXT_VERSION == "v1"
    assert len(CONSENT_TEXT) <= 2000                 # one plain Discord message, no splitting
    # the load-bearing promises, pinned so a silent reword is a failing test rather than a drift
    for line in ("Osaka, Japan — not in the cloud",
                 "**Anthropic**, a company in the United States",
                 "deleted within",
                 "Either choice lets you in",
                 "**Allow outside help**",
                 "**Keep my words here**"):
        assert line in CONSENT_TEXT
    # the labels ARE the notice's two bullets, and they sit on ONE axis — *outside* vs *here*.
    # «Allow the translator» (the first draft) named only rag4 while the consent also covers rag1's
    # typo-tidying: a skimmer would have concluded their clean English never leaves the machine.
    from senses.privacy import LABEL_ALLOW, LABEL_DENY
    assert LABEL_ALLOW == "Allow outside help" and LABEL_DENY == "Keep my words here"
    assert f"**{LABEL_ALLOW}**" in CONSENT_TEXT and f"**{LABEL_DENY}**" in CONSENT_TEXT
    assert "badly typed" in CONSENT_TEXT and "language other" in CONSENT_TEXT  # BOTH phases named


def test_the_re_consent_sweep_clears_every_mirror(subject):
    # the code half of «change the text -> erase every consent and ask again». Everyone reverts to
    # unasked, and unasked denies.
    from lib.core.consent import clear_all_consent
    record_consent(subject.uid, True, name="consentito")
    assert clear_all_consent() >= 1
    assert consent_for(subject.uid) is None
