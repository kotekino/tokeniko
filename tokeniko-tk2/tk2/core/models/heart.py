"""The heart's tables — the second reward family, and character as integrated biography.

**The anatomy is rows, not code** (the Captain's ruling of 2026-08-23). An earlier draft of this file
held the six spheres and three spikes as python enums, on the argument that they are what this heart
IS. The ruling overrules that, and the reason is the seam the whole project rests on: even invariant
data is r-rows. A new sphere must be a MIGRATION, never a binary change — otherwise the one thing
the body cannot grow through someone else's hands is its own emotional anatomy, which is exactly
backwards (body req. 5).

So `heart_anatomy` is a `logic` table: read at boot into the r-cache, written only by migrations,
never by him. Questions that used to be answered by an enum — which sphere is this pole in, what is
its opposite, is it a spike — are answered by `HeartAnatomy`, a reader over those rows.

The RATES at which the tiers integrate are dna parameters and live in `params`; the VALUES are
biography and live in the tables below (heart req. 10). The three tiers are one design — levels
(fast) → mood (slow) → temperament (very slow), each integrating the one below — so they are three
tables of the same shape rather than three inventions.
"""

from datetime import datetime
from typing import Annotated, Iterable

from bunnet import Granularity, Indexed, TimeSeriesConfig
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from tk2.core.documents import KbDocument, LogicDocument
from tk2.core.mixins import Parent, Timestamped, Updated


class UnknownPole(ValueError):
    """A row named a pole the anatomy does not define."""


class AnatomyIncoherent(ValueError):
    """The anatomy table itself does not describe a workable heart."""


# ------------------------------------------------------------------------------------------------
# the anatomy — one row per pole
# ------------------------------------------------------------------------------------------------


class HeartAnatomyDoc(LogicDocument, Timestamped):
    """logic (r) — the shape of the organ, not a tunable and not something he learns: a new sphere arrives as a migration.

    One row per pole. A SPHERE pole carries the pair it belongs to and the pole it stands against;
    a SPIKE carries neither — surprise has no opposite, it fires and decays (heart req. 8) — and
    carries instead the name of what triggers it.

    `targets` is a list because a sphere's target is not always singular: love–hate targets «people,
    including self» (heart req. 7), and collapsing that to one value would lose the half that makes
    self-love representable.
    """

    pole: Annotated[str, Indexed(unique=True)]

    # None on both marks a spike. Two nullable columns rather than an `is_spike` flag: the flag
    # could disagree with the columns, and then the table has two answers.
    sphere: str | None = None
    opposite: str | None = None

    #: Which kinds of thing this pole may attach to — `self`, `person`, `idea`.
    targets: Annotated[list[str], Field(min_length=1)]

    #: Spikes only: what fires them (unexpected input · a staked expectation breaking · an equation
    #: closing unsought). Named here so the trigger inventory is data as well.
    trigger: str | None = None

    class Settings:
        name = "heart_anatomy"


class HeartAnatomy:
    """The reader over the anatomy rows.

    Takes ROWS, not the r-cache, on purpose: `tk2.core` must not import `tk2.datatier` (the
    dependency runs the other way, and inverting it would put Mongo underneath the shape layer).
    The caller does the joining — `HeartAnatomy(cache.rows("heart_anatomy"))` — which also makes
    every question here answerable in a test with no database at all.

    --------------------------------------------------------------------------------------------
    WHERE THE VALIDATION LIVES, and why
    --------------------------------------------------------------------------------------------

    A `heart_levels` row naming an unknown pole must fail. It cannot fail in a pydantic validator on
    the model, and that is not a limitation to route around: the legal set lives in the DATABASE, so
    a field validator could only reach it through module-global state — the very thing the migration
    door was designed to avoid (a permission the calling side can toggle is not a permission). A
    global «current anatomy» would be exactly that shape.

    So the check is split, and each half sits where the thing it checks is actually in hand:

      **boot time** — `check_coherent()` validates the ANATOMY ITSELF, once, against the rows the
      r-cache just loaded. This is what catches a bad migration: a sphere with three poles, an
      opposite that does not point back, a spike carrying a sphere. It runs when the body opens its
      eyes, before anything reads a pole, because a body whose anatomy is contradictory should
      refuse to start rather than discover it a week later in one unlucky code path.

      **write time** — `validate_pole()` is called by the heart's writer, which holds the anatomy
      because it holds the snapshot. That writer arrives with the heart itself (E7); until then this
      is the primitive it will call, and it is tested directly.

    The r-cache's slow tick keeps both honest: a migration that adds a sphere is visible to the
    running body within one interval, with no restart (datatier req. 3).
    """

    def __init__(self, rows: Iterable[HeartAnatomyDoc]):
        self._by_pole: dict[str, HeartAnatomyDoc] = {row.pole: row for row in rows}

    # --- reading ---

    def knows(self, pole: str) -> bool:
        return pole in self._by_pole

    def poles(self) -> list[str]:
        """Every pole the anatomy defines, spikes included."""
        return list(self._by_pole)

    def spheres(self) -> list[str]:
        """The pair names, each once, in the order the rows define them."""
        seen: list[str] = []
        for row in self._by_pole.values():
            if row.sphere is not None and row.sphere not in seen:
                seen.append(row.sphere)
        return seen

    def poles_of(self, sphere: str) -> list[str]:
        return [p for p, row in self._by_pole.items() if row.sphere == sphere]

    def sphere_of(self, pole: str) -> str | None:
        """The pair a pole belongs to, or None if it is a spike (or unknown — `knows()` separates
        those two cases when the caller needs them separated)."""
        row = self._by_pole.get(pole)
        return row.sphere if row else None

    def opposite_of(self, pole: str) -> str | None:
        row = self._by_pole.get(pole)
        return row.opposite if row else None

    def is_spike(self, pole: str) -> bool:
        row = self._by_pole.get(pole)
        return row is not None and row.sphere is None

    def spikes(self) -> list[str]:
        return [p for p, row in self._by_pole.items() if row.sphere is None]

    def targets_of(self, pole: str) -> list[str]:
        row = self._by_pole.get(pole)
        return list(row.targets) if row else []

    def trigger_of(self, pole: str) -> str | None:
        row = self._by_pole.get(pole)
        return row.trigger if row else None

    # --- checking ---

    def validate_pole(self, pole: str) -> str:
        """THE write-time seam. Returns the pole, or raises `UnknownPole`."""
        if pole not in self._by_pole:
            known = ", ".join(sorted(self._by_pole)) or "(the anatomy is empty)"
            raise UnknownPole(
                f"'{pole}' is not a pole this heart has. Known: {known}. A new sphere or spike is a "
                f"migration against `heart_anatomy`, not a value someone writes in passing."
            )
        return pole

    def validate_target(self, pole: str, target_kind: str) -> str:
        """A level must attach to something its pole can attach to — curiosity toward a person is
        not a stricter rule, it is a different feeling than the anatomy describes."""
        self.validate_pole(pole)
        allowed = self._by_pole[pole].targets
        if target_kind not in allowed:
            raise UnknownPole(
                f"pole '{pole}' targets {sorted(allowed)}, not '{target_kind}'."
            )
        return target_kind

    def check_coherent(self) -> None:
        """THE boot-time seam. Raises `AnatomyIncoherent` on a heart that could not work.

        Every rule here is one a migration could plausibly get wrong, and each would otherwise
        surface as a puzzling absence much later — a sphere that never balances, an opposite that
        cannot be found, a spike that decays like a level.
        """
        if not self._by_pole:
            raise AnatomyIncoherent("the anatomy is empty: this body has no heart to speak of.")

        for pole, row in self._by_pole.items():
            is_spike = row.sphere is None

            if is_spike:
                if row.opposite is not None:
                    raise AnatomyIncoherent(
                        f"spike '{pole}' names an opposite: surprise has no opposite pole to sit "
                        f"against — it fires and decays (heart req. 8)."
                    )
                if not row.trigger:
                    raise AnatomyIncoherent(
                        f"spike '{pole}' names no trigger: a spike is an event signal, and an event "
                        f"signal with no event is a level wearing the wrong hat."
                    )
                continue

            if row.trigger:
                raise AnatomyIncoherent(
                    f"sphere pole '{pole}' names a trigger. Triggers belong to spikes; a sphere "
                    f"pole sits at a level."
                )
            if row.opposite is None:
                raise AnatomyIncoherent(
                    f"sphere pole '{pole}' names no opposite: a sphere is a PAIR (heart req. 6)."
                )
            if row.opposite not in self._by_pole:
                raise AnatomyIncoherent(
                    f"pole '{pole}' stands against '{row.opposite}', which the anatomy does not define."
                )
            other = self._by_pole[row.opposite]
            if other.opposite != pole:
                raise AnatomyIncoherent(
                    f"opposition is not reciprocal: '{pole}' stands against '{row.opposite}', which "
                    f"stands against '{other.opposite}'."
                )
            if other.sphere != row.sphere:
                raise AnatomyIncoherent(
                    f"'{pole}' and its opposite '{row.opposite}' are in different spheres "
                    f"('{row.sphere}' and '{other.sphere}')."
                )

        for sphere in self.spheres():
            members = self.poles_of(sphere)
            if len(members) != 2:
                raise AnatomyIncoherent(
                    f"sphere '{sphere}' has {len(members)} poles ({sorted(members)}); a sphere is an "
                    f"opposite PAIR with independent levels, so it has exactly two."
                )


# ------------------------------------------------------------------------------------------------
# the three tiers
# ------------------------------------------------------------------------------------------------


class HeartLevelDoc(KbDocument, Timestamped, Updated):
    """kb — his current feeling is state the body writes every time something moves him.

    The FAST tier, self-scoped: one row per pole, rewritten in place. The history is not here — it
    is in `emotional_log`, which is why this table can be overwritten without losing biography.

    `pole` is a plain string checked against `heart_anatomy` at the seams described on
    `HeartAnatomy`, not an enum: the legal set is data, and a model cannot reach data.
    """

    pole: Annotated[str, Indexed(unique=True)]
    level: float = Field(ge=0.0, le=1.0)

    class Settings:
        name = "heart_levels"


class HeartTargetDoc(KbDocument, Timestamped, Updated):
    """kb — attachment is data, and it is learned: «her joy moves me» is a row, not machinery (heart req. 4).

    The per-target tier (heart req. 13). Keyed by uid for people, which is the case the requirements
    name; ideas are admitted in the same table because curiosity–boredom targets KB regions (heart
    req. 7), and which kinds a pole may attach to is declared by the anatomy's `targets`.
    """

    target_kind: str
    target_ref: Annotated[str, Indexed()]
    pole: str
    level: float = Field(ge=0.0, le=1.0)

    class Settings:
        name = "heart_targets"
        indexes = [
            # One level per (what it is about, which pole). The compound key is unique because two
            # rows for the same person's trust would be two answers to one question.
            IndexModel(
                [("target_kind", ASCENDING), ("target_ref", ASCENDING), ("pole", ASCENDING)],
                unique=True,
            ),
        ]


class HeartMoodDoc(KbDocument, Timestamped, Updated):
    """kb — the slow average of his own levels; his, and written by him.

    The SLOW tier: the window average of `heart_levels`, and the thing that sways the brain's phases
    — never the instant spike (heart req. 12). Self-scoped, because a mood is not held toward
    someone; that is what `heart_targets` is for.
    """

    pole: Annotated[str, Indexed(unique=True)]
    value: float = Field(ge=0.0, le=1.0)

    class Settings:
        name = "heart_mood"


class HeartTemperamentDoc(KbDocument, Timestamped, Updated):
    """kb — the seed is only t₀; after that, temperament is biography and it DRIFTS (heart req. 11).

    The VERY SLOW tier. It would be easy to read this table as parameters — the 2026-08-22 notes
    themselves first called temperament «the db(r) parameter set that makes him him» — but the
    distilled requirement supersedes that: the RATES are dna(r) and live in `params`, the VALUES are
    biography and live here (heart req. 10). Continuous disillusion hardening trust's baseline is
    him becoming who life made him, and a read-only table could not record that happening.
    """

    pole: Annotated[str, Indexed(unique=True)]
    baseline: float = Field(ge=0.0, le=1.0)

    class Settings:
        name = "heart_temperament"


# ------------------------------------------------------------------------------------------------
# the log
# ------------------------------------------------------------------------------------------------


class EmotionalLogDoc(KbDocument):
    """kb — «how did I feel when…» is answerable, and the answer is biography (heart req. 14).

    A TIMESERIES collection, and deliberately so: this is an append-only record of moments, exactly
    the shape tk1's memory already has. It buys the storage that fits the access pattern, and it
    costs the ability to update a row — which is the correct constraint for a log, and the reason
    the datatier's `delete_timeseries_rows` exists at all.

    Note the absence of `Timestamped`: `at` IS the time field, and a second stamp beside it would be
    two clocks on one event.
    """

    at: datetime
    pole: str
    level: float = Field(ge=0.0, le=1.0)

    # What the level was about, when it was not himself — the same scoping `heart_targets` uses, so
    # a person's history is answerable and not only their current standing.
    target_kind: str | None = None
    target_ref: str | None = None

    # What moved him. Optional because the tiers integrate on their own schedule and those entries
    # have no single event behind them; named as a Parent so the cause can actually be FOLLOWED.
    cause: Parent | None = None

    class Settings:
        name = "emotional_log"
        timeseries = TimeSeriesConfig(
            time_field="at",
            meta_field="pole",
            granularity=Granularity.seconds,
        )
