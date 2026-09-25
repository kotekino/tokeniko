# stack — REQUIREMENTS

*Serves: `E0` — the ids of `roadmap.md` / `plan.md`*

*Which modules, components, tech — the dependency summary. Distillation session 2026-08-23. One line
each.*

1. **Python + numpy-scale everywhere** — laptop-honest; no heavyweight ML framework (micro-nn req. 3).
2. **stanza/spaCy as the swappable skeleton** (parser-compiler req. 2) — a dependency, never a foundation.
3. **MongoDB + bunnet + pydantic** — the one persistence stack (datatier req. 1).
4. **FastAPI for the surfaces** — inherited; thin handlers, framework-agnostic services.
5. **Claude for rag — optional by design** — the system runs whole with it disabled (rag req. 5); the only cloud dependency beside the public window.
6. **Every dependency justified in this file** — the list is closed like the register: adding one takes an argument; the fewer, the freer the body.

## The admitted list, and what each one cost to admit

*Requirement 6 says the list is closed and adding one takes an argument. This is where the arguments
are kept — the ones in `pyproject.toml`'s comments, gathered so «is the list still closed?» is
answerable by reading one page rather than by grepping a build file.*

| dependency | admitted | the argument |
|---|---|---|
| `pydantic` · `bunnet` · `pymongo` · `numpy` · `taskipy` | E0, 2026-08-23 | req 1 and req 3 — the persistence stack and numpy-scale, both named at conception |
| `python-dotenv` | 2026-08-23 (T1 finding 1) | the datatier reads `.env` the tk2_config way |
| `nltk` | 2026-08-25 (E1 T1) | pure python plus a LOCAL corpus, and **it enters through ONE door** — `tk2.dictionary.wordnet` is the only module that may import it, so the engine stays runnable and testable with no corpus on the machine. The corpora are an operator install, never a download at import: *a build that reaches the network mid-run is a build nobody pinned* |
| `word2number` | **2026-09-16 (E3, nummod)** | converting an English number WORD needs a roster of atoms plus composition rules, and `db/0001` ruled numerals out of the closed classes for that reason — *«productive and infinite, however finite the words below ten look»*. **Same terms as `nltk`: one door** (`tk2.language.compile.numeral_value`), local import, and its failure is an ABSTENTION rather than a crash — a machine without the package still parses and only the count is missing. tk1 used the same library. **Not trusted blindly**: it returns `0` for some strings that are not numerals, so a zero no word in the phrase asked for is refused |

**THE PATTERN WORTH KEEPING, and it is now twice-used**: a dependency that does a *mechanical,
standard-conforming transformation* — tokens to UD, number words to integers — is admitted behind
ONE DOOR and its absence degrades the station rather than stopping it. A dependency that would make
a JUDGEMENT is a different question and has never been admitted on these terms.

*(`stanza` and `fastapi` are reqs 2 and 4 and are not repeated here; `word2number` is listed because
it is the first addition since the stack session closed.)*
