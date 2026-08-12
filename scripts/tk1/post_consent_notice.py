#!/usr/bin/env python3
"""Post the frozen consent notice + its two buttons into #privacy. ONE-SHOT, run by hand.

    python scripts/tk1/post_consent_notice.py <channel_id>          # dry-run: prints, posts nothing
    python scripts/tk1/post_consent_notice.py <channel_id> --apply  # actually posts

Run ONCE per text version (privacy §1 step 3). The message it posts is what every future click is
routed from — the buttons carry version-stamped custom_ids (`consent:v1:allow` / `:deny`), and the
handler for them lives in the RUNNING senses daemon, which re-registers the persistent view in its
setup_hook on every start. So this script only has to put the message in the room and leave: it
opens its own short-lived connection, posts, and exits. Nothing here handles a click, and the
daemon does not need restarting afterwards.

If the text version bumps, the old message's buttons route to nothing (by design — a stale notice
can never record consent to a retired text). Post the new one, and run senses/privacy.reconsent_all
to strip the roles so everyone chooses again.
"""
import asyncio
import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tokeniko"))
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tokeniko", ".env"))


async def main(channel_id: str, apply: bool) -> int:
    import discord
    from lib.core.consent import CONSENT_TEXT, CONSENT_TEXT_VERSION
    from lib.discord.constants import default_intents
    from senses.privacy import (CUSTOM_ID_ALLOW, CUSTOM_ID_DENY, ConsentView,
                                LABEL_ALLOW, LABEL_DENY, role_allow, role_deny)

    print(f"--- the notice ({CONSENT_TEXT_VERSION}, {len(CONSENT_TEXT)} chars) "
          f"{'-' * 30}\n{CONSENT_TEXT}\n{'-' * 60}")
    print(f"buttons : [{LABEL_ALLOW}] ({CUSTOM_ID_ALLOW})  ·  [{LABEL_DENY}] ({CUSTOM_ID_DENY})")
    print(f"roles   : {role_allow()!r} / {role_deny()!r}   (must EXIST, spelled exactly so)")
    print(f"channel : {channel_id}")

    if len(CONSENT_TEXT) > 2000:
        print("REFUSING: the notice exceeds Discord's 2000-character limit.")
        return 1
    if not apply:
        print("\nDRY RUN — nothing posted. Re-run with --apply to post it for real.")
        return 0

    token = os.getenv("DISCORD_TOKEN")  # the same name senses/main.py reads
    if not token:
        print("REFUSING: DISCORD_TOKEN is not set in tokeniko/.env")
        return 1

    client = discord.Client(intents=default_intents())
    posted: dict = {}

    @client.event
    async def on_ready():
        try:
            channel = client.get_channel(int(channel_id)) or await client.fetch_channel(int(channel_id))
            # what tokeniko can ACTUALLY do here — a channel-level deny (e.g. Send Messages denied
            # for @everyone) overrides the server-level grant from the invite, and he holds no
            # Administrator by design. Printed before the attempt so a 403 is never a guess.
            me = getattr(channel, "guild", None) and channel.guild.me
            if me is not None:
                perms = channel.permissions_for(me)
                print(f"\ntokeniko's permissions in #{getattr(channel, 'name', '?')}: "
                      f"view={perms.view_channel} send={perms.send_messages} "
                      f"embed={perms.embed_links} history={perms.read_message_history}")
                if not perms.send_messages:
                    print("  -> SEND IS DENIED. Fix: channel settings -> Permissions -> add "
                          "tokeniko's ROLE with 'Send Messages' explicitly ALLOWED (a green ✓, "
                          "not a grey slash). The @everyone deny applies to him too otherwise.")
            sent = await channel.send(CONSENT_TEXT, view=ConsentView())
            posted["id"] = str(sent.id)
            print(f"\nPOSTED — message id {sent.id} in #{getattr(channel, 'name', channel_id)}")
            print("Pin it (and the machine's photo above it, when there is one).")
        except Exception as error:
            print(f"\nFAILED: {type(error).__name__}: {error}")
        finally:
            await client.close()

    await client.start(token)
    return 0 if posted else 1


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(asyncio.run(main(args[0], "--apply" in sys.argv)))
