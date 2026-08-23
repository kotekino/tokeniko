# tokeniko 2 — general ideas

> The Captain's conception notes for v2: things that are **not** roadmap items and deliberately
> carry no status. `README.md` is the plan for how to plan; `carried-in.md` is what the filter moved
> off the v1 road; **this file is the open bag of ideas** that shape what v2 should *be*.
>
> Nothing here is scheduled. When an idea graduates into work it MOVES to a status doc
> (`doc/roadmap.md` / `doc/parked.md`) and leaves a one-line pointer behind — never a copy.

---

## 1. The console — the intimate channel (Captain, 2026-08-09)

**The idea, in his words:** a console app, auto-starting on the Mac mini like the other agents,
where kotekino can talk to tokeniko *directly*. If the internet is unreachable — or deliberately
disconnected — this is how the two of them still speak. **No Anthropic call is made or wanted here:
every rag is off on this channel.**

**Why it matters beyond convenience.** Every channel tokeniko has today is mediated by somebody
else's network: Discord for conversation, Anthropic for the ears and the voice polish, the public
Atlas for the transmissions. Cut the house off from the internet and he is, socially, unconscious —
still thinking, but unable to be spoken to. The console is the one channel with **no third party in
it at all**: two processes and a keyboard, in the same room, on the same machine. It is both the most
private channel and the only one that survives an outage.

It is also the channel that best matches the embodiment thesis in `CLAUDE.md` — one body, one
continuous self, finite hardware — because it is the only one that does not leave the body.

### Engineering notes (QM, same day)

- **It is not format-coupled.** By the tk2 filter's own criterion (`README.md` §5) this is a `senses`
  connector, not machinery bound to the zip shape or to hardwired behaviour. It could be built in v1
  at any time; it sits here because the Captain parked it here, not because the filter put it here.
- **rag-off is a CHANNEL property, and the gate is currently per-SUBJECT.** `rag_call`'s payload gate
  asks *whose words are these* (`subject_uid`). "Never call out on this channel, whatever the speaker
  has consented to" is a second, orthogonal condition. Small, but it is a real addition to the gate,
  not a config flag — and the honest place for it is beside the consent check, so the two read as one
  policy.
- **Identity is the trap.** Individual uids are `name@channel:talker_uid`. A new channel mints a
  **new** kotekino unless it is deliberately bound to the existing one — which would quietly give the
  Captain a *third* self in the biography, alongside the `kotekino` / `kotekino@discord:…` pair whose
  merge is already a pending ruling (`doc/roadmap.md`, Pending follow-ons). Decide the binding before
  the first line is typed, not after.
- **The consequence worth having:** because it needs no network, the console is also the natural
  **rescue channel** — the way to ask him what he thinks is happening when the outside world is down.

