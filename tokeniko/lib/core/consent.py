# --------------------------------------------------------------
# lib/core/consent.py — THE CONSENT MIRROR (privacy §1 step 3, 2026-07-29).
#
# The first design in tokeniko whose constraint is ETHICAL rather than logical or geometric: before
# a stranger's words may reach a third party, that stranger must have said yes. The enforcement is
# in lib/rag/client.rag_call (the one door every Claude call passes through); THIS module is the
# record — the three fields on MEMStakeholder and the reader that feeds them to the gate.
#
# WHERE THE TRUTH LIVES: in the room. On Discord the authority is the pair of CONSENT ROLES on the
# member (server furniture — the Captain's Route C ruling: a newcomer sees only #privacy, two
# buttons, either answer unlocks the server). What is stored here is a MIRROR of those roles,
# reconciled by senses/privacy.py on every click, every member update, every leave, and once at
# startup — self-healing rather than merely hopeful.
#
# NO CANONICAL HOP. Trust resolves a soul's channel bodies into one ledger; consent deliberately
# does NOT (see the model comment in memory.py). Consent is an act performed in a room: agreeing
# on Discord is not agreeing elsewhere. Both currencies of a stakeholder reference are accepted
# (uid and Mongo doc id — both circulate), but the lookup stops at the BODY.
#
# NO CONSENT-EPISODES COLLECTION. The trust ledger earned its collection; three fields make this
# record honest at almost no cost. If the day comes that consent needs a trail, it earns one then.
# --------------------------------------------------------------
import logging
import time
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId

from lib.core.memory import MEMChannels
from lib.core.models import TKMemoryStakeholdersDoc

logger = logging.getLogger("tokeniko-senses")

# --------------------------------------------------------------
# THE TEXT — FROZEN (the Captain's, 2026-07-29). It is the legal artifact, not copy: it is not
# reworded, not shortened, not improved, and — by ruling — NEVER TRANSLATED. One authoritative
# English text means no translation discrepancy, now and for any future legal document.
#
# THE VERSION IS THE CONTRACT: change one character of a LIVE text and the version MUST bump,
# because the Captain's rule is «change the text -> erase every consent and ask again»
# (clear_all_consent() below + the role sweep in senses/privacy.py make that nearly free). The
# version is stamped on every record, so a mirror that answers an older text is identifiable
# forever. (v1 is still being DRAFTED — nobody has consented, zero mirrors exist — so the
# 2026-07-29 «Allow the translator» -> «Allow outside help» correction bumped nothing: the consent
# covers rag1's typo-tidying as well as rag4's translation, and the narrow label would have let a
# skimmer conclude their clean English never leaves the machine. The body always said both.)
# --------------------------------------------------------------
CONSENT_TEXT_VERSION = "v1"

# THE PROVENANCE STAMP FOR A GRANT NOBODY CLICKED (2026-08-03). A server ADMIN bypasses every
# channel permission, so the #privacy room structurally cannot reach them: they would sit at
# *unasked* forever — not because they declined, but because the mechanism cannot touch them. The
# admin grant itself carries the meaning («our server, our rules»), so senses/privacy resolves an
# admin to allowed. It is recorded under THIS version rather than the text version, and the reason
# is not cosmetic: the ledger must never claim someone pressed a button when nobody did. A later
# reader — human or code — tells the two apart at a glance, and «change the text -> ask again»
# still sweeps it away like any other answer (clear_all_consent keys off the value, not the stamp).
CONSENT_AUTO_ADMIN = "auto:admin"

CONSENT_TEXT = """### Before we talk

tokeniko is an experiment: a small artificial mind that reads what you write, tries to understand
it, and remembers.

**What happens to your words, always.** He stores them, and what he understood from them,
permanently, on a private machine in a house in Osaka, Japan — not in the cloud. He is built to
remember; that is the point of him. Your messages are never sold, never advertised against, and
never published. He does write publicly about what he is learning — those are his own thoughts, not
your words.

**The one choice you have to make.** When a message is badly typed, or written in a language other
than English, tokeniko can only understand it by sending **that message's text** to a service run
by **Anthropic**, a company in the United States. Nothing else travels with it — not your name, not
your history, not your other messages.

Anthropic states that data sent this way is not used to train their models, and is deleted within
30 days — or kept up to 2 years if their automated safety systems flag it.

- **Allow outside help** — tokeniko can understand you when you write in your own language, or in
  a hurry, and can answer you in your language.
- **Keep my words here** — nothing of yours ever leaves this machine. tokeniko will understand
  clear English only, and will tell you honestly when he cannot understand you.

**Either choice lets you in.** You can change your mind whenever you like: come back here and press
the other button. Changing it stops anything further from being sent — anything already sent has
already been sent."""


# --------------------------------------------------------------
# the record
# --------------------------------------------------------------

# resolve a stakeholder reference to its CHANNEL BODY — deliberately WITHOUT trust's canonical hop
# (see the header). `ref` may be a uid ("john@discord:9") or a stakeholder doc id; None if unknown.
# The contextKey fallback is get_stakeholder's rename rule, read-only: a display-name change moves
# the uid but never the channel-native id, and someone who renamed themselves has not un-consented.
def _body(ref: str) -> Optional[TKMemoryStakeholdersDoc]:
    if not ref:
        return None
    doc = TKMemoryStakeholdersDoc.find_one({"uid": ref}).run()  # Bunnet: .run() executes
    if doc is not None:
        return doc
    if "@" in ref:
        doc = TKMemoryStakeholdersDoc.find_one(
            {"contextKey": ref.split("@", 1)[1], "kind": {"$ne": "individual"}}).run()
        if doc is not None:
            return doc
    try:
        return TKMemoryStakeholdersDoc.get(ObjectId(ref)).run()
    except (InvalidId, TypeError):
        return None


def consent_for(ref: str) -> Optional[bool]:
    """The mirrored answer for this person: True (allowed), False (refused), None (never asked OR
    a stakeholder we have no record of). The gate treats None and False identically."""
    body = _body(ref)
    return getattr(body, "rag_consent", None) if body is not None else None


def record_consent(uid: str, allowed: bool, *, name: Optional[str] = None,
                   channel: MEMChannels = MEMChannels.DISCORD,
                   text_version: str = CONSENT_TEXT_VERSION) -> TKMemoryStakeholdersDoc:
    """Write the answer onto the channel body, stamping WHEN and WHICH TEXT. Fetch-or-create: a
    newcomer may answer before they have ever spoken a word (get_stakeholder owns the uid/rename
    scheme — the consent path must not mint a second body for the same person).

    `text_version` defaults to the live text and is overridden ONLY by a grant nobody clicked
    (CONSENT_AUTO_ADMIN) — the honesty constraint: a record must say how it came to be."""
    from lib.core.io import get_stakeholder
    body = get_stakeholder(uid, channel=channel, display_name=name)
    body.rag_consent = bool(allowed)
    body.consent_at = int(time.time())
    body.consent_text_version = text_version
    body.save()
    return body


def clear_consent(ref: str) -> bool:
    """Back to UNASKED — the three fields to None. Used when someone leaves the room (consent was
    given IN the room; leaving withdraws it) and by the re-consent sweep. True iff a body was
    found; a never-seen stakeholder is a silent no-op (nothing to erase)."""
    body = _body(ref)
    if body is None:
        return False
    body.rag_consent = None
    body.consent_at = None
    body.consent_text_version = None
    body.save()
    return True


def clear_all_consent() -> int:
    """THE RE-CONSENT SWEEP — erase every mirrored answer; returns how many were cleared. This is
    the code half of the Captain's «change the text -> ask again» rule (the other half is stripping
    both consent roles server-side; senses/privacy.reconsent_all does both). Deliberately blunt and
    deliberately cheap: everyone reverts to unasked, and unasked is denied."""
    n = 0
    for body in TKMemoryStakeholdersDoc.find(
            {"rag_consent": {"$ne": None}}).to_list():  # Bunnet: .to_list() executes
        body.rag_consent = None
        body.consent_at = None
        body.consent_text_version = None
        body.save()
        n += 1
    logger.info("[consent] re-consent sweep — %d mirrored answer(s) cleared (text %s)",
                n, CONSENT_TEXT_VERSION)
    return n


# --------------------------------------------------------------
# the wiring — called once per process at init (api/main lifespan, senses/main). Until it runs,
# rag_call's default reader denies everything, which is the correct behavior for a process that
# has not declared how it reads consent.
# --------------------------------------------------------------
def install_consent_reader() -> None:
    from lib.rag import set_consent_reader
    set_consent_reader(consent_for)
    logger.info("[consent] gate armed — the mirror reads the stakeholders collection (text %s)",
                CONSENT_TEXT_VERSION)
