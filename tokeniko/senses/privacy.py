# --------------------------------------------------------------
# senses/privacy.py — THE #privacy ROOM (privacy §1 step 3, the Captain's Route C).
#
# Consent is MANDATED AT JOINING and delivered by SERVER FURNITURE, not by tokeniko asking: a
# newcomer sees only #privacy, reads the frozen notice, and presses one of two buttons — EITHER
# answer unlocks the rest of the server. (Rules Screening was rejected: it can only express
# accept-or-leave. Discord Onboarding was rejected: it needs Community mode and cannot re-ask
# EXISTING members, which collides with the «change the text -> ask again» rule.)
#
# THE TRUTH IS THE ROLE, the mirror is the mirror. A member's consent roles are what the server
# shows and what the Captain can inspect by eye; lib/core/consent holds the copy the engine reads.
# Everything below exists to keep the two in step: the click writes both, on_member_update and
# on_member_remove follow the roles, and a startup sweep reconciles the whole roster — so a
# hand-edited role, a missed event, or a restart-window gap HEALS instead of silently persisting.
#
# THE PERSISTENT-VIEW TRAP (all three are required, and the third fails SILENTLY):
#   1. timeout=None on the view;
#   2. an explicit custom_id on EVERY component (version-stamped: consent:v1:allow / :deny);
#   3. re-registered via add_view() in SETUP_HOOK — not on_ready.
# discord.py raises ValueError when (1) or (2) are unmet, which is a loud and welcome failure. (3)
# raises nothing at all: the buttons of an already-posted message simply stop answering after a
# restart, and restarts are routine (every deploy, every `task senses`).
#
# This is the ONE module in senses that speaks discord.py natively. It has to: a UI component has
# no channel-agnostic form. Everything BELOW the interaction — role reading, mirror writing,
# reconciliation — is written against the adapter's normalized DiscordMember so it stays testable
# without a gateway, and so the day another channel grows its own consent room, the logic moves.
# --------------------------------------------------------------
import asyncio
import logging
import os
from typing import Optional

import discord

from lib.core.consent import CONSENT_TEXT, CONSENT_TEXT_VERSION, clear_consent, record_consent
from lib.discord.models import DiscordMember

logger = logging.getLogger("tokeniko-senses")

# the two consent roles, BY NAME — the EXACT strings the Captain creates server-side (colon and
# spaces included; nothing here slugifies or normalizes them, the match is literal). Env-overridable
# so the names can be whatever reads best in the room without a code change. TWO roles rather than
# one «admitted» role (the Captain's ruling, 2026-07-29) because the roles are then the SOURCE the
# sweep can heal the mirror FROM — one role could say "answered" but never say WHICH answer.
_ROLE_ALLOW_DEFAULT = "Outside help: yes"
_ROLE_DENY_DEFAULT = "Outside help: no"


def role_allow() -> str:
    return os.getenv("DISCORD_CONSENT_ROLE_ALLOW", _ROLE_ALLOW_DEFAULT)


def role_deny() -> str:
    return os.getenv("DISCORD_CONSENT_ROLE_DENY", _ROLE_DENY_DEFAULT)


# the component ids carry the TEXT VERSION: a v2 notice posts v2 buttons, and a stale v1 message
# left in the channel routes to nothing rather than silently recording consent to a retired text.
CUSTOM_ID_ALLOW = f"consent:{CONSENT_TEXT_VERSION}:allow"
CUSTOM_ID_DENY = f"consent:{CONSENT_TEXT_VERSION}:deny"

# BOTH labels name a GAIN (the Captain's, approved and deliberate — do not "balance" them into
# allow/deny). They are the notice's own two bullets, verbatim. The pair sits on ONE axis —
# *outside* vs *here* — which is the actual decision: the consent covers rag1's typo-tidying as
# well as rag4's translation, and «Allow the translator» named only half of what travels.
LABEL_ALLOW = "Allow outside help"
LABEL_DENY = "Keep my words here"

# the ephemeral confirmations — EPHEMERAL so the channel never becomes a public log of who chose
# what. One sentence each, in the notice's own register.
CONFIRM_ALLOW = ("Done — tokeniko may now send a message's text for outside help when he cannot "
                 "understand it, and you can change your mind here whenever you like.")
CONFIRM_DENY = ("Done — nothing of yours will leave this machine, and you can change your mind "
                "here whenever you like.")
# the honest failure: nothing was recorded, and the person is told plainly rather than left to
# believe a choice was saved.
CONFIRM_FAILED = ("Sorry — I could not set that just now, so nothing has been recorded. Please "
                  "tell the server admin that tokeniko cannot assign the consent roles.")

_REASON = f"tokeniko consent ({CONSENT_TEXT_VERSION})"


# --------------------------------------------------------------
# the mirror side — pure over the adapter's normalized member (no discord.py, no gateway)
# --------------------------------------------------------------

# the channel-scoped uid scheme, IDENTICAL to the one senses/inbound stamps on /input — the consent
# record and the speech record must land on the same stakeholder body or the gate reads a stranger.
def member_uid(member: DiscordMember) -> str:
    return f"{member.name}@discord:{member.user_id}"


# the roles' verdict: True allowed, False refused, None nothing to say. BOTH roles at once is a
# server-side accident, not an answer — it reads None (and None denies at the gate).
def consent_from_roles(role_names) -> Optional[bool]:
    names = set(role_names or ())
    allowed, denied = role_allow() in names, role_deny() in names
    if allowed and not denied:
        return True
    if denied and not allowed:
        return False
    return None


# TOKENIKO'S OWN ACCOUNT IS NEVER MIRRORED (the guard, 2026-07-29 — found live while the server was
# being configured). Three reasons, and the third is operational, not philosophical:
#   1. his own content is subject_uid=None by design — ungated, because they are his words. A
#      consent record for himself is meaningless at best.
#   2. holding BOTH roles is a state reconciliation does not expect, and the bot account is the
#      only place it can arise — exclude the account rather than invent a tiebreak.
#   3. if his channel visibility ever leant on a consent role, reconsent_all would make him DEAF on
#      his own server, presenting as an engine bug. (His access must come from an explicit
#      overwrite on HIS OWN role — doc/ref/deploy-body.md §6.)
# Scoped to SELF, deliberately NOT to bots generally: a playbot is driven by a person, so its words
# genuinely do need an answer — and an unanswered one is already safe by default-deny.
def _is_tokeniko(member: DiscordMember) -> bool:
    return bool(getattr(member, "is_self", False))


# THE ADMIN GRANT (the Captain's ruling, 2026-08-03). An administrator BYPASSES channel
# permissions, so the #privacy room — a channel everyone else is funnelled through — structurally
# cannot reach them: they would sit at *unasked*, and therefore denied, forever. Not because they
# declined; because the mechanism cannot touch them. An act that cannot be asked for needs another
# way to be expressed, and the admin grant itself carries it: our server, our rules — administering
# the server IS accepting its privacy terms.
#
# BUT AN EXPLICIT ROLE WINS, in BOTH directions, and the deny direction is the load-bearing one:
# the DENY role is the only way an admin can refuse at all. If the permission bit overrode it, the
# two people who run the server would be the only two who CANNOT opt out — «you can always change
# your mind» would be false for exactly them, and a consent that cannot be refused is not consent.
# So the bit only speaks where the roles say nothing (which is also where both-roles-at-once, the
# server-side accident, lands — and auto-allowing there is the same "we could not ask" case).
def _auto_admin(member: DiscordMember) -> bool:
    return bool(getattr(member, "is_admin", False))


# reconcile ONE member's mirror against their roles; returns the value the mirror now holds.
# Write-avoiding: on_member_update fires for a nickname change too, and the mirror must not churn.
# A member with neither role has their record CLEARED (unasked), never stamped — unless they are an
# admin, whom the room cannot reach (see above).
def reconcile_member(member: DiscordMember) -> Optional[bool]:
    from lib.core.consent import CONSENT_AUTO_ADMIN, CONSENT_TEXT_VERSION, consent_for
    if _is_tokeniko(member):
        return None
    uid = member_uid(member)
    wanted = consent_from_roles(member.role_names)
    auto = wanted is None and _auto_admin(member)
    if auto:
        wanted = True
    if consent_for(uid) == wanted:
        return wanted
    if wanted is None:
        clear_consent(uid)
    else:
        # the stamp is the honesty: a record must say how it came to be, so a later reader can
        # never mistake a permission bit for a pressed button.
        record_consent(uid, wanted, name=member.name,
                       text_version=CONSENT_AUTO_ADMIN if auto else CONSENT_TEXT_VERSION)
    if auto:
        logger.info("[privacy] %s is a server ADMIN — consent AUTO-GRANTED (%s); nobody pressed a "
                    "button, the #privacy gate cannot reach an admin", uid, CONSENT_AUTO_ADMIN)
    else:
        logger.info("[privacy] mirror reconciled for %s -> %s", uid, wanted)
    return wanted


# THE STARTUP SWEEP — the whole roster, once. Cheap on a small server, and it is what makes the
# mirror SELF-HEALING rather than merely hopeful. Returns how many members were inspected.
def reconcile_members(members) -> int:
    n = 0
    for member in members:
        try:
            reconcile_member(member)
            n += 1
        except Exception as error:  # one unreadable member must never abort the sweep
            logger.warning("[privacy] reconcile failed for %s (%s: %s)",
                           getattr(member, "name", "?"), type(error).__name__, error)
    return n


# someone LEFT the room. Consent was given IN the room, so leaving withdraws it — back to unasked,
# which denies. (Their memory items stay: true history be it. What goes is permission, not record.)
def forget_member(member: DiscordMember) -> None:
    if _is_tokeniko(member):
        return
    uid = member_uid(member)
    if clear_consent(uid):
        logger.info("[privacy] %s left the room — consent cleared (unasked = denied)", uid)


# --------------------------------------------------------------
# the room side — discord.py
# --------------------------------------------------------------

# apply one click. Order is deliberate: the ROLES move first and the mirror follows, because the
# roles are the truth — a mirror written against a role that could not be assigned would be a lie
# the sweep would later "heal" by undoing the person's choice. FAILS CLOSED: if the assignment is
# refused (role hierarchy misconfigured -> discord.Forbidden), NOTHING is written and the person is
# told plainly. Returns the message to reply with.
async def apply_choice(interaction, allowed: bool) -> str:
    member, guild = interaction.user, interaction.guild
    if guild is None or member is None:
        logger.error("[privacy] consent click outside a guild — ignored")
        return CONFIRM_FAILED
    # the self guard again, at the third door (see _is_tokeniko): unreachable through the UI — bots
    # cannot press buttons — but the rule is "never mirror consent for his own account", and a rule
    # enforced at two of three doors is a rule waiting to be bypassed by the third.
    me = getattr(getattr(interaction, "client", None), "user", None)
    if me is not None and getattr(member, "id", None) == me.id:
        logger.error("[privacy] tokeniko's own account reached the consent buttons — ignored "
                     "(his words are his own; they are never gated)")
        return CONFIRM_FAILED
    grant_name, revoke_name = ((role_allow(), role_deny()) if allowed
                               else (role_deny(), role_allow()))
    grant = discord.utils.get(guild.roles, name=grant_name)
    revoke = discord.utils.get(guild.roles, name=revoke_name)
    if grant is None:
        logger.error("[privacy] role %r does not exist in guild %s — create both consent roles "
                     "(doc/ref/deploy-body.md §6); nothing recorded for %s",
                     grant_name, guild.id, member.name)
        return CONFIRM_FAILED
    held = {r.name for r in getattr(member, "roles", [])}
    try:
        if grant_name not in held:
            await member.add_roles(grant, reason=_REASON)
        if revoke is not None and revoke_name in held:
            await member.remove_roles(revoke, reason=_REASON)
    except discord.Forbidden:
        logger.error("[privacy] FORBIDDEN assigning %r to %s — tokeniko's own role must sit ABOVE "
                     "both consent roles in the server's role order (MANAGE_ROLES alone is not "
                     "enough); nothing recorded", grant_name, member.name)
        return CONFIRM_FAILED
    except discord.HTTPException as error:
        logger.error("[privacy] role assignment failed for %s (%s) — nothing recorded",
                     member.name, error)
        return CONFIRM_FAILED

    uid = f"{member.name}@discord:{member.id}"
    try:
        # Bunnet is synchronous — never block the gateway loop with it.
        await asyncio.to_thread(record_consent, uid, allowed, name=member.name)
    except Exception as error:
        # the roles carry the truth and the next sweep will copy it here, so the CHOICE is safe —
        # but until then the gate reads the stale mirror (and unasked denies). Loud, not fatal.
        logger.error("[privacy] mirror write failed for %s (%s: %s) — the roles hold; the startup "
                     "sweep will reconcile", uid, type(error).__name__, error)
    logger.info("[privacy] %s answered %s (text %s)", uid,
                "ALLOW" if allowed else "DENY", CONSENT_TEXT_VERSION)
    return CONFIRM_ALLOW if allowed else CONFIRM_DENY


class ConsentView(discord.ui.View):
    """The two buttons under the notice. PERSISTENT by construction (see the module header): no
    timeout, explicit version-stamped custom_ids — so a click on a message posted three deploys
    ago is still routed to this code."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label=LABEL_ALLOW, style=discord.ButtonStyle.primary,
                       custom_id=CUSTOM_ID_ALLOW)
    async def allow(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(await apply_choice(interaction, True),
                                                ephemeral=True)

    @discord.ui.button(label=LABEL_DENY, style=discord.ButtonStyle.secondary,
                       custom_id=CUSTOM_ID_DENY)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(await apply_choice(interaction, False),
                                                ephemeral=True)


# --------------------------------------------------------------
# the wiring
# --------------------------------------------------------------

# the setup_hook the adapter hangs on discord.Client: re-register the persistent view (the ONE
# thing that must happen here — after login, before the gateway connects) and launch the roster
# sweep. The sweep itself CANNOT run here: setup_hook is awaited at the end of login(), before the
# gateway is connected, so the member cache is still empty — it waits for READY inside its own
# task. (The brief said "sweep at setup_hook"; this is that intent, at the earliest point the
# platform can actually honor it.)
def consent_setup_hook(client):
    async def setup_hook() -> None:
        client.add_view(ConsentView())
        logger.info("[privacy] persistent consent view registered (%s)", CONSENT_TEXT_VERSION)
        asyncio.create_task(startup_reconcile(client))
    return setup_hook


async def startup_reconcile(client) -> int:
    """Wait for READY (the member cache fills there), then reconcile the whole roster."""
    try:
        await client.wait_until_ready()
        n = await asyncio.to_thread(reconcile_members, client.members())
        logger.info("[privacy] startup sweep — %d member(s) reconciled", n)
        return n
    except Exception as error:
        logger.warning("[privacy] startup sweep skipped (%s: %s) — the mirror still follows "
                       "events; a click always writes both", type(error).__name__, error)
        return 0


# register the member seams on the adapter (called from senses/main alongside on_message).
def register_consent_events(client) -> None:
    async def on_update(member: DiscordMember) -> None:
        await asyncio.to_thread(reconcile_member, member)

    async def on_remove(member: DiscordMember) -> None:
        await asyncio.to_thread(forget_member, member)

    client.on_member_update(on_update)
    client.on_member_remove(on_remove)


# --------------------------------------------------------------
# the Captain's hands (never automatic — both are run deliberately, and both are documented in
# doc/ref/deploy-body.md §6)
# --------------------------------------------------------------

# post the frozen notice + the buttons into #privacy. Run ONCE per text version; the message is
# what every future click is routed from. 1583 characters — comfortably inside Discord's 2000.
async def post_consent_message(client, channel_id: str) -> Optional[str]:
    from lib.discord.models import Destination
    view = ConsentView()
    channel = await client._resolve_destination(Destination(channel_id=str(channel_id)))
    sent = await channel.send(CONSENT_TEXT, view=view)
    logger.info("[privacy] consent notice %s posted to channel %s (message %s)",
                CONSENT_TEXT_VERSION, channel_id, sent.id)
    return str(sent.id)


# THE RE-CONSENT SWEEP — the Captain's «change the text -> erase every consent and ask again» rule,
# made nearly free: strip both roles from everyone (the server half) and clear every mirrored
# answer (the engine half). Everyone reverts to unasked, unasked denies, and the newly-posted
# notice asks again. Not pretty; it exists and it is documented.
async def reconsent_all(client) -> tuple[int, int]:
    from lib.core.consent import clear_all_consent
    stripped = await client.strip_roles_from_all([role_allow(), role_deny()], reason=_REASON)
    cleared = await asyncio.to_thread(clear_all_consent)
    logger.info("[privacy] RE-CONSENT: %d member(s) stripped, %d mirror(s) cleared", stripped, cleared)
    return stripped, cleared
