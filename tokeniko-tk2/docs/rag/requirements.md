# rag-in / rag-out — REQUIREMENTS

*What the rag layer must be. One line each. Deliberately short — the tk1 shape (one client, one
registry, named call sites) is inherited; only the contract is conceived. Evidence in the dated
`_notes.md` beside this.*

1. **Syntax-only translator, never a mind** — repairs surface, translates, tidies; never reasons, never adds content.
2. **Inbound is escalation-only** — a stumbling parse gets ONE tidying pass; a clean parse never pays the toll.
3. **Outbound is the mouth's stage 3** — polish, when enabled (senses req. 4).
4. **One round-trip fence, both directions** — meaning proven preserved or the original ships (raw input in, scaffold verbatim out).
5. **Optional by design** — rag off, he still works: parser tolerance in, scaffold out; graceful degradation, never a hard dependency.
6. **One client, one registry, every call site named** — the tk1 `lib/rag/` shape, inherited.
7. **The goal is shrinkage** — rag's scope shrinks as the parser toughens; its ceiling is zero; peer TKZip needs no translator at all.
