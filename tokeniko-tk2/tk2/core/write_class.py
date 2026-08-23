"""THE WRITE-CLASS — the everything-is-rows seam, made a schema property.

The body is an interpreter of the db (body req. 2), and there are exactly three kinds of row it
interprets. The kind is not a convention anyone remembers: it is declared on the model, and the
datatier refuses on it.

  kb     (rw)  the knowledge base. The body writes here, and only here. Beliefs, rules, memory,
               theorems, the heart's biography — everything he learns and everything that happens
               to him. This is the tier the evaluator guards the door of.
  param  (r)   the tunables. Read at boot, refreshed on a slow tick, never written by the body —
               a parameter the body could rewrite is a parameter the body could drift on.
  logic  (r)   the hardwired-logic tables. The math expressed as rows instead of code. Read-only
               for the same reason logic is sacred: he does not get to edit the floor he stands on.

`param` and `logic` are the r-classes, and their only writer is a MIGRATION (body req. 3: deploys
are scripts that write the db). That is the whole point of the distinction — a change to either is a
deploy, visible in `db/`, reviewable, and applied by a hand that is not the body's.
"""

from enum import Enum


class WriteClass(str, Enum):
    """A `str` enum so a row can carry the value verbatim and a mongo query can read it as itself."""

    KB = "kb"
    PARAM = "param"
    LOGIC = "logic"

    @property
    def writable(self) -> bool:
        """Whether the BODY may write this class through the datatier's public path.

        Migrations are not the body: they do not ask this question, they use the migration writer.
        """
        return self is WriteClass.KB


class WriteClassViolation(RuntimeError):
    """A write was attempted against an r-class collection through a public path.

    Raised, never logged-and-continued: a silent refusal here would look exactly like the tk1 trap
    the datatier exists to wrap away (a `.delete()` that never ran and never said so).
    """
