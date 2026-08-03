# lib/discord — the Discord channel-adapter SDK.
#
# A thin, DUMB facade over discord.py: it owns the wire (gateway, heartbeat, reconnect, rate-limits —
# all discord.py's job) and speaks exactly the seam senses agrees on (senses/README.md):
#   - on_message(handler)  : register a callback fed a normalized DiscordMessage for EVERY message
#   - send(destination, content, *, kind, polish) -> message_id
#   - fetch_messages(channel_id, ...) -> list[DiscordMessage]
#   - start() / close()    : lifecycle for the senses TaskGroup + SIGTERM stop_event
#
# It knows NOTHING about the brain: no memory, no MEMAction, no stakeholder/contextKey, no NL polish.
# senses owns the translation to/from tokeniko's world; the adapter only moves bytes and normalizes them.

import logging
import re
from typing import Awaitable, Callable, Optional

import discord

from lib.discord.constants import default_intents
from lib.discord.models import DiscordAttachment, DiscordMember, DiscordMessage, Destination

logger = logging.getLogger("tokeniko-senses")

# the inbound callback signature senses registers.
MessageHandler = Callable[[DiscordMessage], Awaitable[None]]
# the MEMBER callbacks (privacy §1 step 3): a role change and a departure, both normalized.
MemberHandler = Callable[[DiscordMember], Awaitable[None]]
# the startup hook, run by discord.py AFTER login and BEFORE the gateway connects — the only place
# a persistent view may be re-registered (see senses/privacy.py).
SetupHook = Callable[[], Awaitable[None]]

# Discord user-mention wire tokens: <@id> and the legacy nickname form <@!id>.
_MENTION_RE = re.compile(r"<@!?(\d+)>")

# punctuation that ALREADY closes a leading vocative — the human typed it, we never double it.
_VOCATIVE_PUNCT = ",.!?;:…-—"


# decode `<@id>` mention tokens to plain usernames (from the message's resolved mention list) —
# normalization of the channel's wire encoding, part of the adapter's job. An id missing from the
# list is dropped; whitespace is re-collapsed so the parser never sees the artifacts.
#
# THE LEADING-VOCATIVE COMMA (2026-08-03, found live). «@tokeniko the cat is a mammal» decodes to
# «tokeniko the cat is a mammal» — a bare name glued to the following noun phrase, and spaCy reads
# the pair as ONE NP headed by *tokeniko*: the subject is silently STOLEN and the sentence compiles
# to a claim ABOUT him ((tokeniko be [a] mammal); cat.n.01 gone, and «tokeniko every bird has
# feathers» loses the quantifier too). The comma is the only thing that marks the address, and the
# WIRE knows this token was a mention — that information exists exactly here and was being thrown
# away. Restoring the punctuation a human would have typed is not inference.
#
# Scoped to HIS OWN mention, by id (the same signal mentions_me reads, and the same reading the
# directedness ladder already commits to: a mention of him is an ADDRESS). For anyone else the same
# comma would COST more than it buys — measured on the live pipeline, «hellen, is a machine» loses
# its subject outright where «hellen is a machine» compiles clean, and «hellen the cat is a mammal»
# never suffered the theft in the first place (it splits into a stray leaf, not a false claim).
def _decode_mentions(content: str, mentions, me_id: Optional[str] = None) -> str:
    names = {str(u.id): u.name for u in (mentions or [])}
    rest = (content or "").lstrip()

    head = ""
    if me_id is not None:
        lead = _MENTION_RE.match(rest)
        if lead is not None and lead.group(1) == str(me_id) and names.get(lead.group(1)):
            head = names[lead.group(1)]
            rest = rest[lead.end():].lstrip()

    body = re.sub(r"\s{2,}", " ",
                  _MENTION_RE.sub(lambda match: names.get(match.group(1), ""), rest)).strip()
    if not head:
        return body
    if not body:
        return head                                  # a bare «@tokeniko» — nothing to separate
    if body[0] in _VOCATIVE_PUNCT:
        return f"{head}{body}"                       # «@tokeniko, …» / «@tokeniko: …» already read
    return f"{head}, {body}"


class DiscordClient:

    def __init__(self, token: str):
        self._token = token
        self._handler: Optional[MessageHandler] = None
        self._member_update: Optional[MemberHandler] = None
        self._member_remove: Optional[MemberHandler] = None
        self._client = discord.Client(intents=default_intents())
        self._register_events()

    # discord.py awaits `self.setup_hook()` at the end of login(): assigning it on the instance is
    # the seam a directly-constructed Client otherwise lacks. It is where a PERSISTENT view must be
    # re-registered — after login, before the gateway connects — and doing that in on_ready instead
    # fails SILENTLY (the buttons of an already-posted message simply stop responding after a
    # restart). Set it before start(); a hook installed after login has already been missed.
    def set_setup_hook(self, hook: SetupHook) -> None:
        self._client.setup_hook = hook

    # --- seam: inbound ------------------------------------------------------

    # register the handler fed EVERY incoming message (channel + DM, including the bot's own —
    # is_self lets senses decide what to drop; per the brief every message is an input).
    def on_message(self, handler: MessageHandler) -> None:
        self._handler = handler

    # register the handlers fed a normalized member when their roles/profile change, and when they
    # leave the guild (privacy §1 step 3 — the consent mirror reconciles off both).
    def on_member_update(self, handler: MemberHandler) -> None:
        self._member_update = handler

    def on_member_remove(self, handler: MemberHandler) -> None:
        self._member_remove = handler

    def _register_events(self) -> None:
        @self._client.event
        async def on_message(message: discord.Message):
            if self._handler is not None:
                await self._handler(self._to_message(message))

        @self._client.event
        async def on_member_update(before: discord.Member, after: discord.Member):
            # the event payload CARRIES the roles array — no fetch needed, no rate-limit cost.
            if self._member_update is not None:
                await self._member_update(self._to_member(after))

        @self._client.event
        async def on_member_remove(member: discord.Member):
            if self._member_remove is not None:
                await self._member_remove(self._to_member(member))

    def _to_member(self, m) -> DiscordMember:
        me = self._client.user
        # guild_permissions is discord.py's FOLD of every role the member wears (plus the owner
        # short-circuit) — the resolved bit, which is why this read belongs here and nowhere else.
        # Defensive getattr: a member object from a partial cache may carry no permissions at all,
        # and "not an admin" is the safe reading (it only ever means «ask them properly»).
        perms = getattr(m, "guild_permissions", None)
        return DiscordMember(
            user_id=str(m.id),
            name=m.name,
            guild_id=str(m.guild.id) if getattr(m, "guild", None) is not None else "",
            role_names=[r.name for r in getattr(m, "roles", [])],
            is_self=bool(me is not None and m.id == me.id),
            is_admin=bool(getattr(perms, "administrator", False)),
        )

    def _to_message(self, m: discord.Message) -> DiscordMessage:
        guild_id = str(m.guild.id) if m.guild is not None else None
        me = self._client.user
        # decode Discord's mention wire-encoding BEFORE the content crosses the seam: a raw
        # `<@id>` token is channel encoding, not language — the parser met one literally and the
        # compile failed («I agree with <@15188…>», 2026-07-11). Names come from the message's own
        # resolved mention list; an unresolvable id is dropped rather than shipped as noise. His own
        # id goes in so a LEADING mention of him is restored to the vocative a human would have
        # punctuated (2026-08-03 — see _decode_mentions).
        content = _decode_mentions(m.content, m.mentions,
                                   me_id=(str(me.id) if me is not None else None))
        reply_to = (
            str(m.reference.message_id)
            if (m.reference is not None and m.reference.message_id is not None)
            else None
        )
        # addressing signals (senses C directedness): a real @-mention OR the bot's name as a word;
        # and whether the replied-to message is one of the bot's own (resolved may be a
        # DeletedReferencedMessage or None if not in cache — treat both as "not me").
        mentions_me = bool(me is not None and (
            any(u.id == me.id for u in m.mentions)
            or re.search(rf"\b{re.escape(me.name)}\b", m.content or "", re.IGNORECASE) is not None
        ))
        resolved = m.reference.resolved if m.reference is not None else None
        reply_author = getattr(resolved, "author", None)
        reply_to_me = bool(me is not None and reply_author is not None and reply_author.id == me.id)
        return DiscordMessage(
            message_id=str(m.id),
            author_id=str(m.author.id),
            author_name=m.author.name,
            channel_id=str(m.channel.id),
            guild_id=guild_id,
            content=content,
            reply_to=reply_to,
            attachments=[
                DiscordAttachment(filename=a.filename, url=a.url, content_type=a.content_type)
                for a in m.attachments
            ],
            is_dm=guild_id is None,
            is_self=bool(me is not None and m.author.id == me.id),
            mentions_me=mentions_me,
            reply_to_me=reply_to_me,
        )

    # --- seam: outbound -----------------------------------------------------

    # deliver an ALREADY-PREPARED content to a destination. kind/polish are accepted to honor the
    # general seam but are passthrough here: for the human Discord channel content is pre-rendered NL
    # in senses, so the adapter ships it verbatim. (They are the reserved hook for a future native-zip
    # channel where polish=False would ship a serialized TKZip.) Returns the sent message id.
    async def send(
        self,
        destination: Destination,
        content: str,
        *,
        kind: str = "message",
        polish: bool = True,
    ) -> str:
        channel = await self._resolve_destination(destination)
        reference = None
        if destination.reply_to is not None:
            reference = discord.MessageReference(
                message_id=int(destination.reply_to), channel_id=channel.id
            )
        sent = await channel.send(content, reference=reference)
        return str(sent.id)

    # resolve a Destination to a discord.py "messageable" channel (guild text channel or DM channel).
    async def _resolve_destination(self, d: Destination):
        if d.channel_id is not None:
            cid = int(d.channel_id)
            return self._client.get_channel(cid) or await self._client.fetch_channel(cid)
        # user_id route: open (or reuse) the 1:1 DM channel.
        uid = int(d.user_id)
        user = self._client.get_user(uid) or await self._client.fetch_user(uid)
        return user.dm_channel or await user.create_dm()

    # --- seam: read history -------------------------------------------------

    # read recent messages of a channel/DM on demand. before/after are message ids (cursor paging).
    async def fetch_messages(
        self,
        channel_id: str,
        *,
        limit: int = 50,
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> list[DiscordMessage]:
        cid = int(channel_id)
        channel = self._client.get_channel(cid) or await self._client.fetch_channel(cid)
        kwargs: dict = {"limit": limit}
        if before is not None:
            kwargs["before"] = discord.Object(id=int(before))
        if after is not None:
            kwargs["after"] = discord.Object(id=int(after))
        return [self._to_message(m) async for m in channel.history(**kwargs)]

    # --- seam: persistent components + the member roster --------------------

    # re-register a PERSISTENT view (timeout=None, every component carrying an explicit custom_id)
    # so clicks on a message posted by a previous run are still routed after a restart. discord.py
    # raises ValueError if the view is not persistent — a loud failure, and the right one.
    def add_view(self, view) -> None:
        self._client.add_view(view)

    # every cached guild member, normalized — the source of the consent mirror's startup sweep.
    # Requires the privileged `members` intent (constants.default_intents) AND a connected gateway:
    # the member cache is filled at READY, so callers await wait_until_ready() first.
    def members(self) -> list[DiscordMember]:
        return [self._to_member(m) for g in self._client.guilds for m in g.members]

    async def wait_until_ready(self) -> None:
        await self._client.wait_until_ready()

    # remove the named roles from EVERY member of every guild — the server half of the re-consent
    # sweep (privacy §1 step 3: change the text, ask everyone again). Returns how many members were
    # actually stripped; a Forbidden on one member is logged and skipped, never fatal.
    async def strip_roles_from_all(self, role_names: list[str], *, reason: str = "") -> int:
        wanted = set(role_names)
        me = self._client.user
        touched = 0
        for guild in self._client.guilds:
            roles = [r for r in guild.roles if r.name in wanted]
            if not roles:
                continue
            for member in guild.members:
                # NEVER strip the bot's own account. If tokeniko's channel access ever leant on one
                # of these roles, a text-version change would silently make him DEAF on his own
                # server — and it would present as an engine bug, not a permissions one.
                if me is not None and member.id == me.id:
                    continue
                held = [r for r in roles if r in member.roles]
                if not held:
                    continue
                try:
                    await member.remove_roles(*held, reason=reason or None)
                    touched += 1
                except discord.Forbidden:
                    logger.error("[discord] cannot strip %s from %s — tokeniko's role must sit "
                                 "ABOVE those roles in the server's role order",
                                 [r.name for r in held], member.name)
        return touched

    # --- lifecycle ----------------------------------------------------------

    # connect the gateway and run until close(). Awaited by the senses listener task.
    async def start(self) -> None:
        await self._client.start(self._token)

    # graceful disconnect — wired to the senses stop_event / task cancellation.
    async def close(self) -> None:
        await self._client.close()
