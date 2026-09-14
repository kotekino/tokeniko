"""0005 — the two edges the Captain approved in August, restored as ROWS.

**WHAT WAS LOST.** On 2026-08-12, after the curation round, the Captain approved two analytic edges
and the note recorded «authorization recorded on the cells and in the manifest»:

    bed.n -> sleep.v    used_for    «a piece of furniture that provides a place to *sleep*»
    hungry.a -> eat.v   state_of    «feeling a need or desire to *eat* food»

`sleep~bed` was the pair the review singled out as **the one only R gets right** — D reads it 0.045,
and the curated layer beat co-occurrence on the axis where WordNet was mute.

The E1 audit of 2026-09-14 found the built base carrying **zero curated cells**. Both edges lived
only in the prototype database that E1b dropped, and R was regenerated from WordNet without them.

**WHY THIS MIGRATION AND NOT ANOTHER CURATION ROUND.** T4 made a curated edge an INPUT to a build
rather than an output of one (`dictionary_curated_edges`). These two rows are the restoration, and
from here a rebuild cannot lose them: it consumes them, and refuses outright if it cannot place one.

**WHAT IS NOT CLAIMED HERE.** The evidence is the resource's own definition, verbatim and marked, as
requirement 20 demands — not a paraphrase, and not a re-derivation. `approved_by` and `approved_at`
carry the ORIGINAL authorization and its date, because the Captain approved these edges in August
and this file is restoring a decision rather than making a new one.

**T3 ALREADY MINES ONE OF THEM, AND THAT IS NOT A REASON TO DROP IT.** `hungry.a -> eat.v` now comes
out of the gloss-reference mine as well, and a curated cell overrides a mined one: the mine found
the reference, the Captain judged the RELATION (`state_of`, not a bare reference), and the judgement
is the part worth keeping. `bed.n -> sleep.v` the mine cannot decide at all — «sleep» is two
dimensions — which is precisely the case curation exists for.

**NOT APPLIED BY THE QM.** Written and reported; the apply is the Captain's hand.
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, CuratedEdgeDoc
from tk2.migrations import ensure_collections

#: The date the Captain approved them, kept rather than refreshed: this restores a decision, and a
#: decision's date is part of what it is.
APPROVED_AT = 1_755_000_000  # 2026-08-12
APPROVED_BY = "the Captain, 2026-08-12 — «agree on the reciprocal 0.60, approve both edges»"

EDGES = [
    {
        "source_key": "bed.n",
        "target_key": "sleep.v",
        "relation": "used_for",
        "weight": 0.8,
        "sense": "bed.n.01",
        "evidence": "bed.n.01 a piece of furniture that provides a place to *sleep*",
        "relabelled": False,
        "approved_by": APPROVED_BY,
        "approved_at": APPROVED_AT,
        "withdrawn_at": None,
    },
    {
        "source_key": "hungry.a",
        "target_key": "eat.v",
        "relation": "state_of",
        "weight": 0.8,
        "sense": "hungry.a.01",
        "evidence": "hungry.a.01 feeling hunger; feeling a need or desire to *eat* food",
        "relabelled": False,
        "approved_by": APPROVED_BY,
        "approved_at": APPROVED_AT,
        "withdrawn_at": None,
    },
]


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(CuratedEdgeDoc, EDGES)
