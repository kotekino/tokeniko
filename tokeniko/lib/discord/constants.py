# lib/discord — costanti dell'adapter: intents + permessi di invito.

import discord


# the gateway intents tokeniko's bot needs. message_content and members are PRIVILEGED intents — both
# must ALSO be toggled ON in the Developer Portal (Bot -> Privileged Gateway Intents), otherwise
# inbound `content` arrives empty and no member/role event is ever delivered (the consent mirror
# would then be blind: no on_member_update, no startup sweep, no member list). guild + DM message
# events are already part of Intents.default().
def default_intents() -> discord.Intents:
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True          # privacy §1 step 3: the consent roles are read off members
    return intents


# OAuth2 invite permission bits for adding the bot to a server (scope "bot"):
#   VIEW_CHANNEL (1<<10) | SEND_MESSAGES (1<<11) | READ_MESSAGE_HISTORY (1<<16) | MANAGE_ROLES (1<<28)
# = 268504064. Read channels + post + read history, plus assigning the two consent roles.
# MANAGE_ROLES IS NOT SUFFICIENT ON ITS OWN — Discord's rule: "a bot can grant roles to other users
# that are of a lower position than its own highest role", so tokeniko's own role must sit ABOVE
# both consent roles in the server's role order. That placement is server-side (the Captain's hand,
# doc/ref/deploy-body.md §6); a misplacement surfaces here as discord.Forbidden and fails CLOSED.
INVITE_PERMISSIONS = (1 << 10) | (1 << 11) | (1 << 16) | (1 << 28)
