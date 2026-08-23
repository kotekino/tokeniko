# stack — REQUIREMENTS

*Which modules, components, tech — the dependency summary. Distillation session 2026-08-23. One line
each.*

1. **Python + numpy-scale everywhere** — laptop-honest; no heavyweight ML framework (micro-nn req. 3).
2. **stanza/spaCy as the swappable skeleton** (parser-compiler req. 2) — a dependency, never a foundation.
3. **MongoDB + bunnet + pydantic** — the one persistence stack (datatier req. 1).
4. **FastAPI for the surfaces** — inherited; thin handlers, framework-agnostic services.
5. **Claude for rag — optional by design** — the system runs whole with it disabled (rag req. 5); the only cloud dependency beside the public window.
6. **Every dependency justified in this file** — the list is closed like the register: adding one takes an argument; the fewer, the freer the body.
